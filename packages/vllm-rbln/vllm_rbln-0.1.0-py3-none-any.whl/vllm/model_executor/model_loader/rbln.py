"""Utilities for selecting and loading rbln models."""
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

import optimum.rbln
import torch
import torch.nn as nn
from transformers import PretrainedConfig

from vllm.config import ModelConfig, SchedulerConfig
from vllm.logger import init_logger
from vllm.model_executor.layers.logits_processor import LogitsProcessor
from vllm.model_executor.layers.sampler import Sampler, SamplerOutput
from vllm.model_executor.models.llava_next import (LlavaNextImageInputs,
                                                   LlavaNextImagePixelInputs)
from vllm.model_executor.models.utils import flatten_bn
from vllm.model_executor.sampling_metadata import SamplingMetadata
from vllm.multimodal import BatchedTensorInputs
from vllm.worker.model_runner_base import ModelRunnerInputBase

if TYPE_CHECKING:
    from vllm.attention.backends.abstract import AttentionBackend

logger = init_logger(__name__)

# modified/customized models for RBLN
_RBLN_GENERATION_MODELS: Dict[str, Tuple[str, str]] = {
    "LlamaForCausalLM": (
        "llama",
        "RBLNLlamaForCausalLM",
    ),
    "GemmaForCausalLM": ("gemma", "RBLNGemmaForCausalLM"),
    "PhiForCausalLM": ("phi", "RBLNPhiForCausalLM"),
    "GPT2LMHeadModel": ("gpt2", "RBLNGPT2LMHeadModel"),
    "MidmLMHeadModel": ("midm", "RBLNMidmLMHeadModel"),
    "MistralForCausalLM": ("mistral", "RBLNMistralForCausalLM"),
    "ExaoneForCausalLM": ("exaone", "RBLNExaoneForCausalLM"),
    "Qwen2ForCausalLM": ("qwen2", "RBLNQwen2ForCausalLM"),
}

_RBLN_ENCODER_DECODER_MODELS: Dict[str, Tuple[str, str]] = {
    "BartForConditionalGeneration": ("bart", "RBLNAutoModelForSeq2SeqLM"),
    "T5ForConditionalGeneration": ("t5", "RBLNAutoModelForSeq2SeqLM"),
}

_RBLN_MULTIMODAL_MODELS = {
    "LlavaNextForConditionalGeneration":
    ("llava_next", "RBLNLlavaNextForConditionalGeneration"),
}

_RBLN_SUPPORTED_MODELS = {
    **_RBLN_GENERATION_MODELS,
    **_RBLN_ENCODER_DECODER_MODELS,
    **_RBLN_MULTIMODAL_MODELS,
}


@dataclass(frozen=True)
class ModelInputForRBLN(ModelRunnerInputBase):
    """
    Used by the RBLNModelRunner.
    """
    input_tokens: torch.Tensor
    input_positions: torch.Tensor
    input_block_ids: torch.Tensor
    sampling_metadata: "SamplingMetadata"
    multi_modal_kwargs: Optional[BatchedTensorInputs] = None

    def as_broadcastable_tensor_dict(
            self) -> Dict[str, Union[int, torch.Tensor]]:
        raise NotImplementedError("ModelInputForNeuron cannot be broadcast.")

    @classmethod
    def from_broadcasted_tensor_dict(
        cls,
        tensor_dict: Dict[str, Any],
        attn_backend: Optional["AttentionBackend"] = None,
    ) -> "ModelInputForRBLN":
        assert attn_backend is None
        return cls.from_broadcasted_tensor_dict(tensor_dict)


class RBLNOptimumForCausalLM(nn.Module):

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__()
        self.model_config = model_config
        self.scheduler_config = scheduler_config
        # keep track last kv cache position for model.forward
        self.kv_cache_pos: Dict[int, int] = {}
        self.decoder_batch_size = self.scheduler_config.max_num_seqs
        self.logits_processor = LogitsProcessor(
            model_config.hf_config.vocab_size, logits_as_input=True)
        self.sampler = Sampler()
        self.init_model()

    def sample(
        self,
        logits: torch.Tensor,
        sampling_metadata: SamplingMetadata,
    ) -> Optional[SamplerOutput]:
        next_tokens = self.sampler(logits, sampling_metadata)
        return next_tokens

    def compute_logits(self, hidden_states: torch.Tensor,
                       sampling_metadata: SamplingMetadata) -> torch.Tensor:
        logits = self.logits_processor(None, hidden_states, sampling_metadata)
        return logits

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        input_block_ids = model_input.input_block_ids
        batch_idx = input_block_ids[0] if is_prompt else None

        if not is_prompt:
            input_ids, positions = self.preprocess_decode(
                input_ids, positions, input_block_ids)

        # optimum.rbln forward()
        logits = self.model.vllm_forward(input_ids=input_ids.to(torch.int64),
                                         cache_position=positions.to(
                                             torch.int32),
                                         batch_idx=batch_idx)
        if not is_prompt:
            logits.logits = logits.logits[input_block_ids]
        return logits

    def init_model(self) -> None:
        config = self.model_config.hf_config
        model_name, model_cls_name = get_rbln_model_info(config)

        compiled_path = self.model_config.compiled_model_dir
        if compiled_path is None or not os.path.exists(compiled_path):
            raise RuntimeError(
                f"compiled_model_dir does not exist {compiled_path}")

        # huggingface model class name
        logger.info("model_name = %s, model_cls_name = %s, model_path = %s",
                    model_name, model_cls_name, compiled_path)

        # huggingface model class
        model_cls = getattr(optimum.rbln, model_cls_name)
        assert model_cls is not None
        # load RBLN compiler binary model
        model = model_cls.from_pretrained(compiled_path, export=False)
        self.model = model

    def preprocess_decode(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        input_block_ids: torch.Tensor,
    ):
        assert input_ids.shape[1] == 1
        padded_input_ids = torch.zeros(self.decoder_batch_size,
                                       1,
                                       dtype=input_ids.dtype)
        padded_position_ids = torch.zeros(self.decoder_batch_size,
                                          1,
                                          dtype=positions.dtype)
        padded_input_ids[input_block_ids] = input_ids
        padded_position_ids[input_block_ids] = positions

        return padded_input_ids, padded_position_ids


class RBLNOptimumConditionalGeneration(RBLNOptimumForCausalLM):

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        input_block_ids = model_input.input_block_ids

        if model_input.multi_modal_kwargs:
            image_input = self._parse_and_validate_image_input(
                model_input.multi_modal_kwargs)
            if image_input is not None:
                assert image_input["type"] == "pixel_values"
                pixel_values = image_input["data"]
                image_sizes = image_input["image_sizes"]
        else:
            pixel_values = None
            image_sizes = None

        if not is_prompt:
            input_ids, positions = self.preprocess_decode(
                input_ids, positions, input_block_ids)

        batch_idx = input_block_ids[0] if is_prompt else None
        # optimum.rbln forward()
        logits = self.model.vllm_forward(
            input_ids=input_ids.to(torch.int64),
            cache_position=positions.to(torch.int32),
            batch_idx=batch_idx,
            pixel_values=pixel_values,
            image_sizes=image_sizes,
        )
        if not is_prompt:
            logits.logits = logits.logits[input_block_ids]
        return logits

    def _parse_and_validate_image_input(
        self, batched_tensor_input: BatchedTensorInputs
    ) -> Optional[LlavaNextImageInputs]:
        pixel_values = batched_tensor_input.get("pixel_values", None)
        image_sizes = batched_tensor_input.get("image_sizes", None)
        image_embeds = batched_tensor_input.get("image_embeds", None)

        if pixel_values is None and image_embeds is None:
            return None

        if pixel_values is not None:
            if not isinstance(pixel_values, (torch.Tensor, list)):
                raise ValueError("Incorrect type of pixel values. "
                                 f"Got type: {type(pixel_values)}")

            if not isinstance(image_sizes, (torch.Tensor, list)):
                raise ValueError("Incorrect type of image sizes. "
                                 f"Got type: {type(image_sizes)}")

            return LlavaNextImagePixelInputs(
                type="pixel_values",
                data=flatten_bn(pixel_values),
                image_sizes=flatten_bn(image_sizes),
            )

        if image_embeds is not None:
            if not isinstance(image_embeds, torch.Tensor):
                raise ValueError("Incorrect type of image embeds. "
                                 f"Got type: {type(image_embeds)}")

            raise NotImplementedError(
                "Image embeds are not supported in this version for RBLN")

        raise AssertionError("This line should be unreachable.")


class RBLNOptimumEncoderDecoder(RBLNOptimumForCausalLM):

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config, scheduler_config)
        # encoder length used for encoder_decoder architecture
        self.enc_lengths = [0] * self.decoder_batch_size

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        input_block_ids = model_input.input_block_ids
        batch_idx = input_block_ids[0] if is_prompt else None

        if not is_prompt:
            input_ids, positions = self.preprocess_decode(
                input_ids, positions, input_block_ids)
        else:
            # prefill batch_size is always 1
            assert positions.shape[0] == 1
            self.enc_lengths[batch_idx] = positions[0][-1].item()

        # optimum.rbln forward()
        logits = self.model.vllm_forward(input_ids=input_ids.to(torch.int64),
                                         cache_position=positions.to(
                                             torch.int32),
                                         batch_idx=batch_idx,
                                         enc_lengths=self.enc_lengths)

        if not is_prompt:
            logits.logits = logits.logits[input_block_ids]

        return logits


def is_multi_modal(config: PretrainedConfig) -> bool:
    return is_arch_supported(config, _RBLN_MULTIMODAL_MODELS)


def is_enc_dec_arch(config: PretrainedConfig) -> bool:
    return is_arch_supported(config, _RBLN_ENCODER_DECODER_MODELS)


def is_arch_supported(config: PretrainedConfig,
                      model_set: Dict[str, Tuple[str, str]]) -> bool:
    architectures = getattr(config, "architectures", [])
    return any(arch in _RBLN_SUPPORTED_MODELS and arch in model_set
               for arch in architectures)


def get_rbln_model_info(config: PretrainedConfig) -> Tuple[str, str]:
    architectures = getattr(config, "architectures", [])
    for arch in architectures:
        if arch in _RBLN_SUPPORTED_MODELS:
            model_name, model_cls_name = _RBLN_SUPPORTED_MODELS[arch]
            return model_name, model_cls_name

    raise ValueError(
        f"Model architectures {architectures} are not supported on RBLN "
        f"for now. Supported architectures: "
        f"{list(_RBLN_SUPPORTED_MODELS.keys())}")


def get_rbln_model(
    model_config: ModelConfig,
    scheduler_config: SchedulerConfig,
) -> nn.Module:
    if is_multi_modal(model_config.hf_config):
        rbln_model = RBLNOptimumConditionalGeneration(
            model_config=model_config, scheduler_config=scheduler_config)
    elif is_enc_dec_arch(model_config.hf_config):
        rbln_model = RBLNOptimumEncoderDecoder(
            model_config=model_config, scheduler_config=scheduler_config)
    else:
        rbln_model = RBLNOptimumForCausalLM(model_config=model_config,
                                            scheduler_config=scheduler_config)
    return rbln_model.eval()
