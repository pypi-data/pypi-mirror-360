"""
This module implements the TPTT model with linear attention (LiZA) and LoRA support.
Author : Fabien FURFARO
TPTT : Transforming Pretrained Transformers into Titans (https://arxiv.org/abs/2506.17671)
"""

import logging
import math
import os
import re
import shutil
from typing import Dict, List, Optional

import torch
import torch.nn.functional as F
from einops import rearrange
from huggingface_hub import hf_hub_download, list_repo_files
from peft import LoraConfig, get_peft_model
from safetensors import safe_open
from torch import nn
from transformers import AutoModelForCausalLM, DynamicCache, PreTrainedModel
from transformers.configuration_utils import PretrainedConfig

from .configuration_tptt import TpttConfig

logger = logging.getLogger(__name__)  # monitoring


class LCache:
    """
    Cache for storing intermediate states of linear attention layers.
    Supports a sliding window if max_length is set.
    """

    def __init__(self):
        """
        Initialize the cache.

        Args:
            max_length (Optional[int]): Maximum number of tokens to keep per layer (if set).
        """
        self.inputs_states: List[Dict[str, torch.Tensor]] = (
            []
        )  # recurrent states and qkv buffers
        self.seen_tokens = 0

    def __getitem__(self, layer_idx: int) -> Optional[Dict[str, torch.Tensor]]:
        """
        Retrieve the state for the given layer index, if it exists.
        """
        if layer_idx < len(self.inputs_states):
            return self.inputs_states[layer_idx]
        return None

    def update(self, layer_idx: int, **kwargs):
        """
        Update the cache for a given layer.
        If max_length is set, keep only the last max_length tokens in any sequence state.
        """
        detached_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, torch.Tensor):
                value = value.detach()
            detached_kwargs[key] = value

        if len(self.inputs_states) <= layer_idx:
            self.inputs_states.append(detached_kwargs)
        else:
            self.inputs_states[layer_idx].update(detached_kwargs)

    def reset(self):
        """
        Reset the cache and token counter.
        """
        self.inputs_states.clear()
        self.seen_tokens = 0


class LiZAttention(nn.Module):
    """LiZA Linear Attention module, mixing linear and vanilla attention."""

    def __init__(
        self,
        base_attn: nn.Module,
        layer_idx: int,
        base_config,  # Backbone Config
        linear_cache: Optional[LCache] = None,
        operator_mode: str = "delta_rule",
        max_self_attn_length: Optional[int] = None,  # unnecessary
        base_scale_attn: bool = False,
        mag_weight: float = 0.5,
        cross_gate: bool = False,
        max_chunk_size: int = 64,
    ):
        super().__init__()
        self.base_attn = base_attn
        self.base_config = base_config
        self.layer_idx = layer_idx
        self.max_self_attn_length = max_self_attn_length
        self.base_scale_attn = base_scale_attn
        self.mag_weight = mag_weight
        self.cross_gate = cross_gate
        self.max_chunk_size = max_chunk_size
        (
            self.num_heads,
            self.head_dim,
            self.num_key_value_heads,
            self.num_key_value_groups,
        ) = self._get_attention_parameters(base_attn, base_config)
        self.scaling = self.head_dim**-0.5
        self.operator = LinearAttention(
            layer_idx=layer_idx,
            mode=operator_mode,
            max_chunk_size=max_chunk_size,
            linear_cache=linear_cache,
        ).to(dtype=torch.float32)
        self.pool_g = nn.AdaptiveAvgPool1d(
            output_size=self.head_dim * self.num_key_value_heads
        )

    def _get_attention_parameters(self, base_attn, base_config):
        """Retrieve the attention parameters from the base attention module."""
        # first order base attention module and second order config
        num_heads = (
            getattr(base_attn, "num_heads", None)
            or getattr(base_attn, "num_q_heads", None)
            or getattr(base_config, "num_heads", None)
            or getattr(base_config, "num_attention_heads", None)
        )
        head_dim = getattr(base_attn, "head_dim", None) or getattr(
            base_config, "head_dim", None
        )
        num_key_value_heads = (
            getattr(base_attn, "num_kv_heads", None)
            or getattr(base_attn, "num_k_heads", None)
            or getattr(base_config, "num_key_value_heads", None)
            or num_heads  # fallback
        )
        num_key_value_groups = getattr(base_attn, "num_key_value_groups", None) or (
            num_heads // num_key_value_heads if num_heads and num_key_value_heads else 1
        )
        return (
            num_heads,
            head_dim,
            num_key_value_heads,
            num_key_value_groups,
        )

    def _apply_projections(self, hidden_states):
        base_attn = self.base_attn
        if hasattr(base_attn, "q_proj"):
            # LLama, OLMO and Mistral style
            q = base_attn.q_proj(hidden_states)
            k = base_attn.k_proj(hidden_states)
            v = base_attn.v_proj(hidden_states)
            out_proj = base_attn.o_proj
        elif hasattr(base_attn, "qkv_proj"):
            # OpenELM and GPT-Neo style : QKV fused, split on the last dimension
            qkv = base_attn.qkv_proj(hidden_states)
            q, k, v = split_qkv(base_attn, qkv)
            out_proj = base_attn.out_proj
        elif hasattr(base_attn, "c_attn") and hasattr(base_attn, "c_proj"):
            # GPT-2 style
            qkv = base_attn.c_attn(hidden_states)
            q, k, v = qkv.chunk(3, dim=-1)
            out_proj = base_attn.c_proj
        else:
            raise ValueError("Unsupported attention module: cannot find projections.")
        # Ensure stability
        q = ensure_stability(q, min_val=-1e4, max_val=1e4)
        k = ensure_stability(k, min_val=-1e4, max_val=1e4)
        v = ensure_stability(v, min_val=-1e4, max_val=1e4)
        return q, k, v, out_proj

    def _prepare_attn_input(self, q, k, v, gate_norm):
        # Forget and Write Gating for linear attn (abusive term)
        f_g, w_g = self.pool_g(k), self.pool_g(v)

        # Reshape for multi-head
        q = rearrange(q, "b n (h d) -> b h n d", h=self.num_heads)
        k = rearrange(k, "b n (h d) -> b h n d", h=self.num_key_value_heads)
        v = rearrange(v, "b n (h d) -> b h n d", h=self.num_key_value_heads)

        f_g = rearrange(f_g, "b n (h m) -> b h n m", h=self.num_key_value_heads)
        w_g = rearrange(w_g, "b n (h m) -> b h n m", h=self.num_key_value_heads)

        # Repeat for GQA
        k = repeat_kv(k, self.num_key_value_groups)
        v = repeat_kv(v, self.num_key_value_groups)

        f_g = repeat_kv(f_g, self.num_key_value_groups)
        w_g = repeat_kv(w_g, self.num_key_value_groups)

        ## linear stability part
        q = torch.clamp(F.softmax(q, dim=-1), min=1e-6, max=1 - 1e-6)
        k = torch.clamp(F.softmax(k, dim=-1), min=1e-6, max=1 - 1e-6)
        # scale by head_dim**-0.5
        v = ensure_stability(v * self.scaling, min_val=-1e4, max_val=1e4)

        f_g = F.logsigmoid(f_g) / gate_norm  # pylint: disable=not-callable
        w_g = torch.exp(F.logsigmoid(w_g) / gate_norm)  # pylint: disable=not-callable
        f_g = torch.clamp(f_g, min=-gate_norm, max=-1e-6)
        w_g = torch.clamp(w_g, min=1e-6, max=1 - 1e-6)

        # Convert to float32 for numerical stability and get model dtype
        q, k, v, f_g, w_g = (
            x.to(torch.float32).contiguous() for x in (q, k, v, f_g, w_g)
        )
        g = (f_g, w_g)

        return q, k, v, g

    def _process_linear_attn(self, q, k, v, g, out_proj, tensor_dtype, kwargs):
        """Process the linear attention part of the forward pass."""
        # Linear attention
        o_lin = self.operator(
            q,
            k,
            v,
            beta=g,
            **kwargs,  # pass use_cache and other kwargs
        )
        o_lin = rearrange(o_lin, "b h n d -> b n (h d)").to(tensor_dtype)
        o_lin = out_proj(o_lin)

        # Ensure stability
        o_lin = ensure_stability(o_lin, min_val=-1e4, max_val=1e4)
        return o_lin

    def _process_self_attn(self, hidden_states, attention_mask, kwargs):
        """Process the self-attention part (with truncation)."""
        if self.max_self_attn_length:  # Not needed for SWA (nonparam memorize context)
            hidden_states, attention_mask = truncate_attention_mask(
                hidden_states, attention_mask, self.max_self_attn_length
            )

            if kwargs.get("position_embeddings", None) is not None:
                cos, sin = kwargs["position_embeddings"]
                cos = cos[:, -self.max_self_attn_length :]
                sin = sin[:, -self.max_self_attn_length :]
                kwargs["position_embeddings"] = (cos, sin)

            if isinstance(kwargs.get("past_key_value", None), DynamicCache):
                # cache management
                if (
                    len(kwargs["past_key_value"]) > self.layer_idx
                    and self.layer_idx == 0
                ):
                    kwargs["past_key_value"].crop(self.max_self_attn_length - 1)

        # Standard attention (mask and rotation is applied inside)
        base_attn_outputs = self.base_attn(
            hidden_states,
            attention_mask=attention_mask,
            **kwargs,
        )

        if isinstance(base_attn_outputs, tuple):
            if len(base_attn_outputs) == 3:
                o_base, attn_weights, present_key_value = base_attn_outputs
                expected_attn_mode = 3
            elif len(base_attn_outputs) == 2:
                o_base, attn_weights = base_attn_outputs
                present_key_value, expected_attn_mode = None, 2
            else:
                raise ValueError(
                    f"Unexpected number of outputs from base_attn: {len(base_attn_outputs)}"
                )
        else:
            o_base = base_attn_outputs
            attn_weights, present_key_value, expected_attn_mode = None, None, 1
        # Ensure stability
        o_base = ensure_stability(o_base, min_val=-1e4, max_val=1e4)
        return o_base, attn_weights, present_key_value, expected_attn_mode

    def _prepare_attn_mixin(self, o_lin, o_base, tensor_dtype, eps=1e-5):
        """Prepare linear attn for mixing with self attn."""
        # Force cast typing, shape : [b n (h d)]
        o_lin = o_lin.to(tensor_dtype)
        o_base = o_base.to(tensor_dtype)
        # o_lin normalization RMSNorm
        o_lin = o_lin / o_lin.pow(2).mean(dim=-1, keepdim=True).add(eps).sqrt()
        # feature scaling
        if self.base_scale_attn:
            scaler = o_base.pow(2).mean(dim=-1, keepdim=True).add(eps).sqrt()
            o_lin = scaler * o_lin
        return o_lin, o_base

    def _apply_mag(self, linear_attention, softmax_attention):
        """Apply the MAG strategy"""
        # Left-Padding management
        if linear_attention.shape[1] != softmax_attention.shape[1]:
            left_trunc = min(linear_attention.shape[1], softmax_attention.shape[1])
            linear_attention, softmax_attention = (
                linear_attention[:, -left_trunc:],
                softmax_attention[:, -left_trunc:],
            )
        # NAM : Neural Attention Mixer (with graph forcing)
        mag_weight = torch.tensor(
            self.mag_weight,
            dtype=softmax_attention.dtype,
            device=softmax_attention.device,
        )
        softmax_weighted = (1 - mag_weight) * softmax_attention
        linear_weighted = mag_weight * linear_attention
        if self.cross_gate:
            output_attention = (
                softmax_weighted + linear_weighted + softmax_weighted * linear_weighted
            )  # complex cross product (unlinear interaction)
        else:
            output_attention = softmax_weighted + linear_weighted  # classic
        # Final output
        return ensure_stability(output_attention, min_val=-1e4, max_val=1e4)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs,
    ):
        device = hidden_states.device
        tensor_dtype = hidden_states.dtype
        self.base_attn.to(device)

        if self.training:
            kwargs.pop("past_key_value", None)
            kwargs["use_cache"] = False
        else:
            # Force evaluation
            kwargs["use_cache"] = True

        kwargs.pop("position_ids", None)  # obsolete

        # Apply projections to hidden states
        q, k, v, out_proj = self._apply_projections(hidden_states)

        # Manage attention mask (with padding)
        if attention_mask is not None:
            # attention_mask -> [batch, seq], v: [batch, seq, ...]
            v = apply_linear_attention_mask(attention_mask, v)

        # Prepare inputs tensor for linear attn
        gate_norm = kwargs.get("gate_logit_normalizer", 16)
        q, k, v, g = self._prepare_attn_input(q, k, v, gate_norm)

        # Process linear attn from mask
        o_lin = self._process_linear_attn(q, k, v, g, out_proj, tensor_dtype, kwargs)

        # Process self attn with truncation
        o_base, attn_weights, present_key_value, expected_attn_mode = (
            self._process_self_attn(hidden_states, attention_mask, kwargs)
        )

        # Prepare output mixing
        o_lin, o_base = self._prepare_attn_mixin(o_lin, o_base, tensor_dtype, eps=1e-5)

        # Apply Memory as Gate in self-attention (with max length management)
        out = self._apply_mag(o_lin, o_base)

        # Return output following transformer convention
        if expected_attn_mode == 3:
            return out, attn_weights, present_key_value
        elif expected_attn_mode == 2:
            return out, attn_weights
        else:
            return out


def get_tptt_model(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    model: nn.Module,
    base_config: PretrainedConfig,  # ou LlamaConfig, MistralConfig, etc.
    liza_attention: LiZAttention,
    target_modules: list,
    linear_cache: Optional[LCache] = None,
    operator_mode: str = "delta_rule",
    base_scale_attn: bool = False,
    mag_weight: float = 0.5,
    cross_gate: bool = False,
    max_chunk_size: int = 64,
    max_self_attn_length: Optional[int] = None,  # unnecessary
):
    """Replace target modules in a model with LiZAttention."""
    linear_cache = linear_cache or LCache()
    # Inject LiZAttention into the model
    for name, _ in model.named_modules():
        if name in target_modules:
            parent = model
            *path, last = name.split(".")
            for p in path:
                parent = getattr(parent, p)
            layer_idx = extract_layer_idx(name)
            setattr(
                parent,
                last,
                liza_attention(
                    getattr(parent, last),
                    layer_idx=layer_idx,
                    base_config=base_config,
                    linear_cache=linear_cache,
                    operator_mode=operator_mode,
                    max_self_attn_length=max_self_attn_length,
                    base_scale_attn=base_scale_attn,
                    mag_weight=mag_weight,
                    cross_gate=cross_gate,
                    max_chunk_size=max_chunk_size,
                ),
            )
    return model, linear_cache


class TpttModel(PreTrainedModel):
    """
    TPTT model wrapper with linear attention (LiZA) and LoRA support.
    Handles only architecture and weights.
    """

    config_class = TpttConfig

    def __init__(
        self,
        config: TpttConfig,
        **kwargs,
    ):
        """
        Initialize TpttModel with a given config and backbone.
        Injects LiZA attention modules into the backbone.
        """
        super().__init__(config, **kwargs)
        repo_or_path = getattr(config, "_base_path", None) or config._name_or_path

        # 1. Load backbone TODO : support no model.safetensors
        self.backbone = AutoModelForCausalLM.from_pretrained(
            config.base_model_name, **kwargs
        )
        self._retie_lm_after_load(**kwargs)  # Force lm tie weights

        # 2. Inject LiZA attention
        self.linear_cache = LCache()
        self.backbone, self.linear_cache = self.inject_liza_attention(
            self.backbone, config, self.linear_cache
        )
        # 3. Apply LoRA if present and configured
        if config.lora_config is not None:
            lora_config_obj = LoraConfig(**config.lora_config)
            self.backbone = get_peft_model(self.backbone, lora_config_obj)
            if repo_or_path:
                self.load_peft_safetensors(
                    repo_or_path, token=kwargs.get("token", None)
                )

    def load_peft_safetensors(self, src, token=None):
        # src: local dir or repo_id
        fname = "adapter_model.safetensors"
        if os.path.isdir(src):
            path = os.path.join(src, fname)
            if not os.path.exists(path):
                return
        else:
            if fname not in list_repo_files(src, token=token):
                return
            path = hf_hub_download(src, fname, token=token)
        with safe_open(path, framework="pt") as f:
            self.backbone.load_state_dict(
                {k: f.get_tensor(k) for k in f.keys()}, strict=False
            )

    @staticmethod
    def inject_liza_attention(
        backbone,
        config,
        linear_cache,
    ):
        """
        Inject LiZAttention into the specified target modules of the base model.
        """
        # Find target modules by suffix (e.g., "attn", "attention")
        target_modules = [
            name
            for name, _ in backbone.named_modules()
            if any(name.endswith(suffix) for suffix in config.target_modules_names)
        ]
        if not target_modules:
            raise ValueError(
                f"Target modules '{config.target_modules_names}' not found in the model."
            )
        # Inject LiZAttention (external function, not shown here)
        return get_tptt_model(
            backbone,
            base_config=backbone.config,
            liza_attention=LiZAttention,
            target_modules=target_modules,
            linear_cache=linear_cache,
            operator_mode=config.operator_mode,
            max_self_attn_length=config.max_self_attn_length,
            base_scale_attn=config.base_scale_attn,
            mag_weight=config.mag_weight,
            cross_gate=config.cross_gate,
            max_chunk_size=config.max_chunk_size,
        )

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        """
        Forward pass. All arguments are passed to the underlying base model.
        """
        if self.training:
            kwargs["use_cache"] = False
            kwargs.pop("num_items_in_batch", None)
        else:
            kwargs["use_cache"] = True
        return self.backbone(
            input_ids=input_ids, attention_mask=attention_mask, labels=labels, **kwargs
        )

    def generate(self, *args, **kwargs):
        # Delegate the generate call to the backbone model, which supports generation
        return self.backbone.generate(*args, **kwargs)

    def save_pretrained(self, path: str, **kwargs):
        """Save model weights, config, and source code to the given path."""
        super().save_pretrained(path, **kwargs)

        # 1. Save PEFT weights and clean adapter config
        self._save_peft_weights(path, **kwargs)
        # 2. Copy Python files for trust_remote_code
        self._copy_source_files(path)

    def _save_peft_weights(self, path: str, **kwargs):
        """Save PEFT weights and remove redundant adapter config."""
        self.backbone.save_pretrained(path, **kwargs)
        adapter_config_path = os.path.join(path, "adapter_config.json")
        if os.path.exists(adapter_config_path):
            os.remove(adapter_config_path)

    def _copy_source_files(self, path: str):
        """Copy all .py files from package directory for trust_remote_code."""
        src_dir = os.path.dirname(os.path.abspath(__file__))
        for fname in os.listdir(src_dir):
            if fname.endswith(".py"):
                src = os.path.join(src_dir, fname)
                dst = os.path.join(path, fname)
                shutil.copy2(src, dst)

    def _retie_lm_after_load(self, **kwargs):
        """Re-link lm_head after loading external weights."""
        embed_lm = find_embedding_lm(self.backbone)
        if embed_lm is not None and hasattr(self.backbone, "lm_head"):
            if self.backbone.lm_head is None:  # ensure lm_head exists
                self.backbone.lm_head = nn.Linear(
                    embed_lm.weight.shape[1], embed_lm.weight.shape[0], bias=False
                )
            if kwargs.get("tie_word_embeddings", True):
                self.backbone.lm_head.weight = embed_lm.weight  # share weights
                logger.info("Weights of lm_head have been shared with embedding.")
            else:
                self.backbone.lm_head.weight = nn.Parameter(embed_lm.weight.clone())
                logger.info("Weights of lm_head have been cloned from the embedding.")

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        model = super().from_pretrained(*args, **kwargs)
        model._retie_lm_after_load(**kwargs)
        return model


TpttModel.register_for_auto_class("AutoModelForCausalLM")


class LinearAttention(nn.Module):
    """Base class for linear attention operators."""

    _MODES = {
        "delta_rule": dict(order=1, gate_type="k", linear=True),
        "delta_rule_v": dict(order=1, gate_type="v", linear=True),
        "delta_rule_kv": dict(order=1, gate_type="kv", linear=True),
        "delta_rule_kv_gelu": dict(order=1, gate_type="kv", linear=False),
        "delta_product": dict(order=2, gate_type="kv", linear=True),
    }

    def __init__(
        self, layer_idx, mode="delta_rule", max_chunk_size=64, linear_cache=None
    ):
        super().__init__()
        self.layer_idx = layer_idx
        self.mode = mode

        if mode not in self._MODES:
            raise ValueError(f"Unsupported linear attention mode: {mode}")
        config = self._MODES[mode]
        self.order = config["order"]
        self.gate_type = config["gate_type"]
        self.linear = config["linear"]

        self.max_chunk_size = max_chunk_size
        self.linear_cache = linear_cache or LCache()

    def compute_gate(self, beta):
        """
        Compute the gating tensor according to the gate_type.
        """
        if self.gate_type == "k":
            return torch.clamp(torch.exp(beta[0]), min=1e-6, max=1 - 1e-6)
        elif self.gate_type == "v":
            return torch.clamp(beta[1], min=1e-6, max=1 - 1e-6)
        elif self.gate_type == "kv":
            return torch.clamp(torch.exp(beta[0]) * beta[1], min=1e-6, max=1 - 1e-6)
        else:
            raise ValueError(f"Unsupported gate_type: {self.gate_type}")

    def get_cache(self, use_cache):
        """
        Retrieve recurrent state and qkv buffers from the cache.
        """
        if not use_cache:
            return None, None
        last_state = self.linear_cache[self.layer_idx]
        if last_state is not None:
            recurrent_state = last_state.get("recurrent_state", None)
            qkv_buffers = last_state.get("qkv", None)
        else:
            recurrent_state = None
            qkv_buffers = None
        return recurrent_state, qkv_buffers

    def save_cache(self, use_cache, q, k, v, gate, state):
        """
        Save the recurrent state and qkv buffers to the cache.
        """
        if not use_cache:
            return
        if self.order > 1:
            qkv_buffers = (
                q[:, :, -(self.order - 1) :, :],
                k[:, :, -(self.order - 1) :, :],
                v[:, :, -(self.order - 1) :, :],
                gate[:, :, -(self.order - 1) :, :],
            )
        else:
            qkv_buffers = None
        self.linear_cache.update(self.layer_idx, recurrent_state=state, qkv=qkv_buffers)

    def forward(self, q, k, v, beta, **kwargs):
        """
        Forward pass for the attention operator.
        """
        # Ensure float32 for numerical stability
        q, k, v = [x.to(torch.float32) for x in (q, k, v)]
        if isinstance(beta, (tuple, list)):
            beta = tuple(b.to(torch.float32) for b in beta)
        else:
            beta = beta.to(torch.float32)

        gate = self.compute_gate(beta)

        # Retrieve cache if needed
        use_cache = kwargs.get("use_cache", False)
        recurrent_state, qkv_buffers = self.get_cache(use_cache)

        if qkv_buffers is not None:
            q = torch.cat([qkv_buffers[0], q], dim=2)
            k = torch.cat([qkv_buffers[1], k], dim=2)
            v = torch.cat([qkv_buffers[2], v], dim=2)
            gate = torch.cat([qkv_buffers[3], gate], dim=2)

        output, state = self.chunk_delta_product_forward(
            q,
            k,
            v,
            gate,
            self.max_chunk_size,
            n=self.order,
            linear=self.linear,
            initial_state=recurrent_state,
        )

        # Save cache if needed
        self.save_cache(use_cache, q, k, v, gate, state)

        return output

    @staticmethod
    def chunk_delta_product_forward(
        query, key, value, beta_gate, chunk_size, n=1, linear=True, initial_state=None
    ):
        """
        DeltaProduct implementation https://arxiv.org/abs/2502.10297
        Chunkwise parallele implementation https://arxiv.org/abs/2406.06484
        DeltaProduct order 2 (and with derivative trick) is Titans equivalence
        """

        def sequential_delta_product_scan(
            q_chunks, k_chunks, W, U, n, linear, chunk_size, initial_state
        ):
            """
            For each chunk, process chunk_size*n steps (virtual tokens) in order.
            """
            B, H, num_chunks, chunk_n, D = q_chunks.shape  # chunk_n = chunk_size * n
            output = torch.empty_like(q_chunks)
            state = initial_state
            for chunk_idx in range(num_chunks):
                q = q_chunks[:, :, chunk_idx]  # [B, H, chunk_n, D]
                k = k_chunks[:, :, chunk_idx]  # [B, H, chunk_n, D]
                w = W[:, :, chunk_idx]  # [B, H, chunk_n, D]
                u = U[:, :, chunk_idx]  # [B, H, chunk_n, D]
                o_intra = torch.zeros(
                    B, H, chunk_n, D, device=q.device, dtype=torch.float32
                )
                o_inter = torch.zeros(
                    B, H, chunk_n, D, device=q.device, dtype=torch.float32
                )
                new_state = state.clone()
                for step in range(n):
                    # For each Householder step, select the corresponding virtual tokens
                    idx = torch.arange(chunk_size) * n + step  # [chunk_size]
                    q_step = q[:, :, idx, :]  # [B, H, chunk_size, D]
                    k_step = k[:, :, idx, :]
                    w_step = w[:, :, idx, :]
                    u_step = u[:, :, idx, :]
                    state_i = state[:, :, step]  # [B, H, D, D]
                    u_i = u_step - torch.matmul(w_step, state_i)
                    o_inter[:, :, idx, :] = torch.matmul(q_step, state_i).to(
                        dtype=torch.float32
                    )
                    a_i = (q_step @ k_step.transpose(-2, -1)).tril()
                    o_intra[:, :, idx, :] = torch.matmul(a_i, u_i).to(
                        dtype=torch.float32
                    )
                    # Update state for this order
                    new_state_i = state_i + torch.matmul(k_step.transpose(-2, -1), u_i)
                    new_state_i = ensure_stability(
                        new_state_i, min_val=-1e4, max_val=1e4
                    )
                    new_state[:, :, step] = new_state_i.to(dtype=torch.float32)
                # Add non-linear activation if required (more RNN like)
                state = (
                    new_state
                    if linear
                    else F.gelu(new_state, approximate="tanh").to(dtype=torch.float32)
                )  # pylint: disable=not-callable
                output[:, :, chunk_idx] = o_intra + o_inter
            return output, state

        batch_size, num_heads, seq_len, head_dim = query.shape
        chunk_size = get_valid_chunk_size(seq_len, chunk_size)
        num_chunks = seq_len // chunk_size

        # Prepare product scan (trick to simulate multihead): [B, H, seq_len*n, D]
        query_n = query if n == 1 else expand_virtual_tokens_dt(query, n)
        key_n = key if n == 1 else expand_virtual_tokens_dt(key, n)
        value_n = value if n == 1 else expand_virtual_tokens_dt(value, n)
        beta_n = beta_gate if n == 1 else expand_virtual_tokens_dt(beta_gate, n)

        # Chunk input tensors to [B, H, num_chunks, chunk_size*n, D]
        q_chunks = chunk_sequence(query_n, num_chunks, chunk_size * n)
        k_chunks = chunk_sequence(key_n, num_chunks, chunk_size * n)
        v_chunks = chunk_sequence(value_n, num_chunks, chunk_size * n)
        beta_chunks = chunk_sequence(beta_n, num_chunks, chunk_size * n)

        # Gated keys/values: [B, H, C, chunk_size, D]
        k_beta = k_chunks * beta_chunks
        v_beta = v_chunks * beta_chunks

        # Build strictly lower-triangular T: [B, H, C, chunk_size*n, chunk_size*n]
        T = -(k_beta @ k_chunks.transpose(-2, -1)).tril(-1)
        T = ensure_stability(T, min_val=-1e4, max_val=1e4)

        # Invert (I - T): [B, H, C, chunk_size*n, chunk_size*n]
        inv_T = invert_nchunked_lower_triangular_matrix(T)

        # Compute W and U: [B, H, C, chunk_size*n, D]
        W = ensure_stability(torch.matmul(inv_T, k_beta), min_val=-1e4, max_val=1e4)
        U = ensure_stability(torch.matmul(inv_T, v_beta), min_val=-1e4, max_val=1e4)

        # Prepare initial recurrent state: [B, H, n, D, D]
        state_shape = (batch_size, num_heads, n, head_dim, head_dim)
        if initial_state is not None and initial_state.shape == state_shape:
            state = initial_state.to(device=query.device, dtype=torch.float32)
        else:
            state = torch.full(
                (batch_size, num_heads, n, head_dim, head_dim),
                fill_value=1e-6,
                device=query.device,
                dtype=torch.float32,
            )

        # Sequential scan over chunks using the DeltaProduct rule
        output, state = sequential_delta_product_scan(
            q_chunks.to(dtype=torch.float32),
            k_chunks.to(dtype=torch.float32),
            W.to(dtype=torch.float32),
            U.to(dtype=torch.float32),
            n,
            linear,
            chunk_size,
            state.to(dtype=torch.float32),
        )

        # Restore output shape to [batch, num_heads, seq_len, head_dim]
        idx_last = torch.arange(chunk_size, device=output.device) * n + (n - 1)
        output = output[:, :, :, idx_last, :]  # [B, H, num_chunks, chunk_size, D]
        output = output.reshape(batch_size, num_heads, seq_len, head_dim)
        return output.to(dtype=torch.float32), state.to(dtype=torch.float32)


def chunk_sequence(x, num_chunks, chunk_size):
    """
    Splits a sequence tensor into chunks along the sequence dimension. [batch, num_heads, seq_len, head_dim]
    Returns: torch.Tensor: Output tensor of shape [batch, num_heads, num_chunks, chunk_size, head_dim]
    """
    B, H, _, D = x.shape
    return x.reshape(B, H, num_chunks, chunk_size, D)


def expand_virtual_tokens_dt(x, n):
    """
    Expand tokens into 'n' virtual tokens using finite difference (derivative) trick.
    x: [B, H, S, D] --> [B, H, n*S, D] discrete (n-1)-th order derivative
    """
    B, H, S, D = x.shape
    x_pad = torch.cat(
        [torch.zeros(B, H, n - 1, D, device=x.device, dtype=torch.float32), x], dim=2
    )  # [B, H, S + n - 1, D]
    unfolded = x_pad.unfold(dimension=2, size=n, step=1)  # [B, H, S, D, n]
    # Apply binomial coefficients
    coeffs = torch.tensor(
        [(-1) ** k * math.comb(n - 1, k) for k in range(n)],
        dtype=torch.float32,
        device=x.device,
    )  # [n], "momentum, jerk, snap, crackle, pop" expressivity
    coeffs = coeffs / coeffs.norm(p=1)  # L1 normalization (if parity)
    unfolded = unfolded * coeffs.view(1, 1, 1, 1, n)
    # Flip to [x_t, x_{t-1}, ..., x_{t-n+1}]
    unfolded = unfolded.flip(-1)
    # Permute to concatenate all dt shifts for each token
    out = unfolded.permute(0, 1, 2, 4, 3).reshape(B, H, S * n, D)
    return out


def extract_layer_idx(module_name: str) -> int:
    """
    Extract the layer index from a module name string.
    """
    match = re.search(r"\.(\d+)\.", module_name)
    if match:
        return int(match.group(1))
    return -1


def find_embedding_lm(module):
    """Find the embedding weight in a model module."""
    for _, child in module.named_modules():
        if hasattr(child, "embed_tokens") and hasattr(child.embed_tokens, "weight"):
            return child.embed_tokens
        if hasattr(child, "token_embeddings") and hasattr(
            child.token_embeddings, "weight"
        ):
            return child.token_embeddings
    return None


def ensure_stability(tensor, min_val=-1e4, max_val=1e4):
    """stability forcing"""
    dtype = tensor.dtype
    center = (max_val - min_val) / 2
    tensor = torch.clamp(tensor, min=min_val, max=max_val)
    tensor = torch.nan_to_num(tensor, nan=center, posinf=max_val, neginf=min_val)
    return tensor.to(dtype=dtype)


def soft_clamp(x, min_val=1e-6, max_val=1 - 1e-6):
    """Differentiable clamping for stability"""
    dtype = x.dtype
    scale = (max_val - min_val) / 2
    center = (max_val + min_val) / 2
    return (torch.tanh((x - center) / scale) * scale + center).to(dtype=dtype)


def repeat_kv(x: torch.Tensor, n_rep: int) -> torch.Tensor:
    """Repeat key/value heads for grouped query attention (GQA)."""
    return x.repeat_interleave(n_rep, dim=1)


def split_qkv(base_attn, qkv):
    """Split the QKV tensor into separate Q, K, and V tensors."""
    num_q_heads = getattr(base_attn, "num_q_heads", None)
    num_k_heads = getattr(base_attn, "num_k_heads", None)
    num_v_heads = getattr(base_attn, "num_v_heads", None)
    head_dim = getattr(base_attn, "head_dim", None)

    q_len = num_q_heads * head_dim
    k_len = num_k_heads * head_dim
    v_len = num_v_heads * head_dim

    q, k, v = torch.split(qkv, [q_len, k_len, v_len], dim=-1)
    return q, k, v


def apply_linear_attention_mask(attention_mask, v):
    # extract (if) padding mask
    if attention_mask.dim() == 4 and attention_mask.shape[1] == 1:
        # [batch, 1, seq, seq] -> [batch, seq]
        mask = attention_mask.diagonal(dim1=-2, dim2=-1).squeeze(1)
    else:
        # Squeeze all singleton dims except batch (dim=0)
        mask = attention_mask.squeeze(
            dim=tuple(
                i
                for i in range(1, attention_mask.dim())
                if attention_mask.shape[i] == 1
            )
        )
    # handle left padding : mask is [batch, seq] --> Broadcast to v [batch, seq, (...)]
    mask = mask[:, -v.shape[-2] :][(...,) + (None,) * (v.dim() - 2)]
    return v * mask


def truncate_attention_mask(hidden_states, attention_mask, max_length):
    """
    Truncate hidden_states and attention_mask to the last window of size max_length,
    matching the sequence dimension of hidden_states.
    """
    seq_dim = 1  # convention: (batch, seq, ...)
    seq_len = hidden_states.shape[seq_dim]
    if seq_len > max_length:
        hidden_states = hidden_states.narrow(seq_dim, seq_len - max_length, max_length)
        if attention_mask is not None:
            # mask [batch, seq]
            if attention_mask.dim() == 2:
                attention_mask = attention_mask[:, -max_length:]
            # mask [batch, seq, seq]
            elif attention_mask.dim() == 3:
                attention_mask = attention_mask[:, -max_length:, -max_length:]
            # mask [batch, 1, seq, seq]
            elif attention_mask.dim() == 4 and attention_mask.shape[1] == 1:
                attention_mask = attention_mask[:, :, -max_length:, -max_length:]
            else:
                raise ValueError(
                    "No dimension in attention_mask matches sequence length of hidden_states."
                )
    return hidden_states, attention_mask


def invert_nchunked_lower_triangular_matrix(T, dtype=torch.float32):
    """
    Explicitly computes the inverse of (I - T), where T is strictly lower-triangular.
    The algorithm is equivalent to vectorized forward substitution applied to the identity matrix.
    T: [B, H, C, chunk_size*n, chunk_size*n] Returns: (..., N, N) inverse of (I - T)
    """
    size = T.shape[-1]  # chunk_size * n
    eye = torch.eye(size, device=T.device, dtype=dtype)
    inv_T = T.clone().to(dtype=dtype)
    for i in range(1, size):
        update = torch.einsum("...j,...jk->...k", inv_T[..., i, :i], inv_T[..., :i, :i])
        tmp = inv_T[..., i, :i] + update
        inv_T = inv_T.clone()
        inv_T[..., i, :i] = tmp
    inv_T = inv_T + eye.view((1,) * (inv_T.dim() - 2) + (size, size))
    return inv_T.to(dtype=dtype)


def get_valid_chunk_size(total_l: int, chunk_size: int) -> int:
    """
    Return the largest chunk_size <= chunk_size that divides total_l.
    If no chunk_size > 1 fits, return 1.
    """
    for c in range(min(chunk_size, total_l), 0, -1):
        if total_l % c == 0:
            return c
    return 1


def match_dim(x: torch.Tensor, dim: int, target_size: int) -> torch.Tensor:
    """
    Match the size of tensor x along dimension dim to target_size by interpolation
    or projection.
    """
    src_size = x.shape[dim]
    if src_size == target_size:
        return x
    x = torch.moveaxis(x, dim, -1)
    shape = x.shape
    if src_size < target_size:
        x = x.reshape(-1, 1, src_size)
        x = F.interpolate(x, size=target_size, mode="linear", align_corners=False)
        x = x.reshape(*shape[:-1], target_size)
    else:
        eye = torch.eye(target_size, src_size, device=x.device, dtype=x.dtype)
        x = F.linear(x, eye)  # pylint: disable=not-callable
    x = torch.moveaxis(x, -1, dim)
    return x
