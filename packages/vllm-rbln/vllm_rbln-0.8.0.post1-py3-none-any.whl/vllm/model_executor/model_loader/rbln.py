# SPDX-License-Identifier: Apache-2.0
"""Utilities for selecting and loading rbln models."""
import bisect
import os
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import optimum.rbln
import torch
import torch.nn as nn
from transformers import PretrainedConfig

from vllm.config import ModelConfig, PoolerConfig, SchedulerConfig
from vllm.logger import init_logger
from vllm.model_executor.layers.logits_processor import LogitsProcessor
from vllm.model_executor.layers.pooler import Pooler, PoolingType
from vllm.model_executor.layers.sampler import Sampler, SamplerOutput
from vllm.model_executor.model_loader.rbln_utils import nullable_ints
from vllm.model_executor.models.blip2 import (Blip2ImageEmbeddingInputs,
                                              Blip2ImageInputs,
                                              Blip2ImagePixelInputs)
from vllm.model_executor.models.gemma3_mm import (Gemma3ImageInputs,
                                                  Gemma3ImagePixelInputs)
from vllm.model_executor.models.idefics3 import (Idefics3ImageEmbeddingInputs,
                                                 Idefics3ImagePixelInputs,
                                                 ImageInputs)
from vllm.model_executor.models.llava_next import (LlavaNextImageInputs,
                                                   LlavaNextImagePixelInputs)
from vllm.model_executor.models.qwen2_5_vl import (
    Qwen2_5_VLImageEmbeddingInputs, Qwen2_5_VLImageInputs,
    Qwen2_5_VLImagePixelInputs, Qwen2_5_VLVideoEmbeddingInputs,
    Qwen2_5_VLVideoInputs, Qwen2_5_VLVideoPixelInputs)
from vllm.model_executor.models.utils import flatten_bn
from vllm.model_executor.pooling_metadata import PoolingMetadata
from vllm.model_executor.sampling_metadata import SamplingMetadata
from vllm.multimodal import BatchedTensorInputs
from vllm.sequence import PoolerOutput, PoolingSequenceGroupOutput
from vllm.worker.model_runner_base import ModelRunnerInputBase

if TYPE_CHECKING:
    from vllm.attention.backends.abstract import AttentionBackend

logger = init_logger(__name__)
version_error = RuntimeError(
    "Incompatible vLLM version detected. "
    "This vLLM version is not compatible with optimum-rbln. "
    "Please verify that you are using a supported version.")

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
    "OPTForCausalLM": ("opt", "RBLNOPTForCausalLM"),
}

_RBLN_ENCODER_DECODER_MODELS: Dict[str, Tuple[str, str]] = {
    "BartForConditionalGeneration":
    ("bart", "RBLNBartForConditionalGeneration"),
    "T5ForConditionalGeneration": ("t5", "RBLNT5ForConditionalGeneration"),
    "T5WithLMHeadModel": ("t5", "RBLNT5ForConditionalGeneration"),
}

_RBLN_MULTIMODAL_MODELS = {
    "LlavaNextForConditionalGeneration":
    ("llava_next", "RBLNLlavaNextForConditionalGeneration"),
    "Qwen2_5_VLForConditionalGeneration":
    ("qwen2_5_vl", "RBLNQwen2_5_VLForConditionalGeneration"),
    "Idefics3ForConditionalGeneration":
    ("idefics3", "RBLNIdefics3ForConditionalGeneration"),
    "Blip2ForConditionalGeneration":
    ("blip2", "RBLNBlip2ForConditionalGeneration"),
    "Gemma3ForConditionalGeneration": ("gemma3",
                                       "RBLNGemma3ForConditionalGeneration"),
}

_RBLN_EMBEDDING_MODELS = {
    "T5EncoderModel": ("t5_encoder", "RBLNT5EncoderModel"),
    "BertModel": ("bert_model", "RBLNBertModel"),
    "RobertaForSequenceClassification":
    ("roberta_classification", "RBLNRobertaForSequenceClassification"),
    "RobertaModel": ("roberta", "RBLNRobertaModel"),
    "XLMRobertaForSequenceClassification":
    ("xlm_roberta_classification", "RBLNXLMRobertaForSequenceClassification"),
    "XLMRobertaModel": ("xlm_roberta", "RBLNXLMRobertaModel"),
}

_RBLN_SUPPORTED_MODELS = {
    **_RBLN_GENERATION_MODELS,
    **_RBLN_ENCODER_DECODER_MODELS,
    **_RBLN_MULTIMODAL_MODELS,
    **_RBLN_EMBEDDING_MODELS,
}


@dataclass(frozen=True)
class ModelInputForRBLN(ModelRunnerInputBase):
    """
    Used by the RBLNModelRunner.
    """
    input_tokens: torch.Tensor
    input_positions: torch.Tensor
    block_tables: torch.Tensor
    sampling_metadata: "SamplingMetadata"
    running_requests_ids: List[str]
    multi_modal_kwargs: Optional[BatchedTensorInputs] = None
    token_type_ids: Optional[torch.Tensor] = None
    pooling_metadata: Optional[PoolingMetadata] = None
    finished_requests_ids: Optional[List[str]] = None

    def as_broadcastable_tensor_dict(
            self) -> Dict[str, Union[int, torch.Tensor]]:
        raise NotImplementedError("ModelInputForRBLN cannot be broadcast.")

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
        # TODO: should be renamed
        self.decoder_batch_size = self.scheduler_config.max_num_seqs
        self.logits_processor = LogitsProcessor(model_config.get_vocab_size,
                                                logits_as_input=True)
        self.sampler = Sampler()
        self.init_model()
        self.padding_value = self.get_padding_value()
        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            self.decoder_batch_sizes = tuple(
                reversed(self.model.rbln_config.decoder_batch_sizes))

    def sample(
        self,
        logits: torch.Tensor,
        sampling_metadata: SamplingMetadata,
    ) -> Optional[SamplerOutput]:
        next_tokens = self.sampler(logits, sampling_metadata)
        return next_tokens

    def compute_logits(self, hidden_states: torch.Tensor,
                       sampling_metadata: SamplingMetadata) -> torch.Tensor:
        return self.logits_processor(None, hidden_states, sampling_metadata)

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        block_tables = model_input.block_tables
        is_prompt = model_input.sampling_metadata.num_prompts > 0

        padded_batch_size = self.decoder_batch_size
        original_batch_size = input_ids.shape[0]
        # NOTE(eunji): Select lower-bounded batch size
        # in case of multiple decoders
        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            padded_batch_size = self.select_lower_bounded_batch_size(
                original_batch_size, self.decoder_batch_sizes)
            self.model.decoder = self.model.decoders[padded_batch_size]

        if not is_prompt:
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids,
                positions,
                block_tables,
                padded_batch_size=padded_batch_size)
        else:
            block_tables = block_tables.squeeze(0)

        kwargs = {
            "input_ids": input_ids.to(torch.int64),
            "cache_position": positions.to(torch.int32),
            "block_tables": block_tables,
        }

        if is_prompt:
            if self.model.prefill_decoder is None:
                raise version_error

            return self.model.prefill_decoder(**kwargs).logits

        if self.model.decoder is None:
            raise version_error

        logits = self.model.decoder(**kwargs).logits
        if self.attn_impl != "flash_attn":
            return logits[:original_batch_size]

        return logits[:model_input.block_tables.shape[0]]

    def init_model(self) -> None:
        config = self.model_config.hf_config
        model_name, model_cls_name = get_rbln_model_info(config)

        if isinstance(self.model_config.model,
                      (str, Path)) and os.path.exists(self.model_config.model):
            model_path = Path(self.model_config.model)
            if model_path.is_dir() and any(model_path.glob('*.rbln')):
                compiled_path = self.model_config.model
            else:
                compiled_path = self.model_config.compiled_model_dir
        else:
            compiled_path = self.model_config.compiled_model_dir

        if compiled_path is None or not os.path.exists(compiled_path):
            raise RuntimeError(
                f"Compiled model path does not exist: {compiled_path}")

        # huggingface model class name
        logger.info("model_name = %s, model_cls_name = %s, model_path = %s",
                    model_name, model_cls_name, compiled_path)

        # huggingface model class
        model_cls = getattr(optimum.rbln, model_cls_name)
        assert model_cls is not None
        # Load RBLN compiler binary model
        device_id = nullable_ints(self.model_config.device_id)
        model = model_cls.from_pretrained(compiled_path,
                                          export=False,
                                          rbln_device=device_id)
        self.model = model
        self.rbln_model_config = model.rbln_config
        self.attn_impl = model.get_attn_impl() if hasattr(
            model, "get_attn_impl") else None

    def get_padding_value(self):
        attn_impl = self.attn_impl
        padding = -1
        if attn_impl is not None and attn_impl == "flash_attn":
            # For flash attention, the last block is the dummy block
            padding = self.model.get_kvcache_num_blocks() - 1

            if npu_num_blocks := os.environ.get("VLLM_RBLN_NPU_NUM_BLOCKS"):
                padding = int(npu_num_blocks) - 1

        return padding

    def preprocess_decode(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        block_tables: torch.Tensor,
        input_block_ids: Optional[torch.Tensor] = None,
        padded_batch_size: Optional[int] = None,
    ):
        assert input_ids.shape[1] == 1
        if input_block_ids is None and padded_batch_size is None:
            raise ValueError(
                "Either input_block_ids or padded_batch_size must be provided."
            )
        elif input_block_ids is not None and padded_batch_size is not None:
            raise ValueError(
                "Cannot provide both input_block_ids and padded_batch_size.")

        if padded_batch_size is None:
            padded_batch_size = self.decoder_batch_size

        original_batch_size = input_ids.shape[0]

        padded_input_ids = torch.zeros(padded_batch_size,
                                       1,
                                       dtype=input_ids.dtype)
        padded_position_ids = torch.zeros(padded_batch_size,
                                          1,
                                          dtype=positions.dtype)
        padded_block_tables = torch.zeros(padded_batch_size,
                                          block_tables.shape[1],
                                          dtype=block_tables.dtype).fill_(
                                              self.padding_value)

        if self.attn_impl != "flash_attn":
            available_blocks = torch.arange(0,
                                            padded_batch_size,
                                            dtype=block_tables.dtype)
            mask = torch.ones(padded_batch_size, dtype=torch.bool)
            unused_blocks = available_blocks[
                ~torch.isin(available_blocks, block_tables.flatten())]

            if input_block_ids is None:
                padded_input_ids[:original_batch_size] = input_ids
                padded_position_ids[:original_batch_size] = positions
                padded_block_tables[:original_batch_size] = block_tables
                mask[:original_batch_size] = False
            else:
                padded_input_ids[input_block_ids] = input_ids
                padded_position_ids[input_block_ids] = positions
                padded_block_tables[input_block_ids] = block_tables
                mask[input_block_ids] = False

            if unused_blocks.numel() > 0:
                padded_block_tables[mask] = unused_blocks[0]

        else:
            padded_input_ids[:original_batch_size] = input_ids
            padded_position_ids[:original_batch_size] = positions
            padded_block_tables[:original_batch_size] = block_tables

        return padded_input_ids, padded_position_ids, padded_block_tables

    @classmethod
    @cache
    def select_lower_bounded_batch_size(self, original_batch_size: int,
                                        decoder_batch_sizes: tuple):
        index = bisect.bisect_left(decoder_batch_sizes, original_batch_size)
        return decoder_batch_sizes[index]


class RBLNOptimumForEncoderModel(RBLNOptimumForCausalLM):
    PAD_TOKEN_ID = 0

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config, scheduler_config)
        self._pooler = self._build_pooler(model_config.pooler_config)

    def is_classification_arch(self):
        architectures = getattr(self.model_config.hf_config, "architectures",
                                [])
        return len(architectures) > 0 and "Classification" in architectures[0]

    def preprocess(
        self,
        input_ids: torch.Tensor,
        type_token_ids: torch.Tensor,
        positions: torch.Tensor,
    ):
        batch_size, seq_len = input_ids.shape
        target_batch_size = self.decoder_batch_size

        def pad_if_needed(
                tensor: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
            if tensor is None:
                return None

            if tensor.size(1) > self.rbln_model_config.max_seq_len:
                tensor = tensor[:, :self.rbln_model_config.max_seq_len]

            if tensor.size(0) >= target_batch_size:
                return tensor
            padded = tensor.new_zeros((target_batch_size, tensor.size(1)))
            padded[:batch_size] = tensor
            return padded

        return pad_if_needed(input_ids), pad_if_needed(
            type_token_ids), pad_if_needed(positions)

    def pool(self, hidden_states, pooling_metadata):
        if self._pooler:
            return self._pooler(hidden_states, pooling_metadata)
        else:
            # FIXME: ad-hoc for RBLNXLMRobertaForSequenceClassification
            outputs = [
                PoolingSequenceGroupOutput(data) for data in hidden_states
            ]
            return PoolerOutput(outputs=outputs)

    def _build_pooler(self, pooler_config: PoolerConfig) -> Optional[Pooler]:
        if not self.is_classification_arch():
            return Pooler.from_config_with_defaults(
                pooler_config,
                pooling_type=PoolingType.CLS,
                normalize=True,
                softmax=False)
        return None

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids, token_type_ids, positions = self.preprocess(
            model_input.input_tokens, model_input.token_type_ids,
            model_input.input_positions)

        max_position = torch.max(positions, dim=1).indices
        position_indices = torch.arange(positions.shape[1],
                                        device=positions.device).unsqueeze(0)
        attention_mask = (position_indices <= max_position.unsqueeze(1)).long()

        kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }

        if token_type_ids:
            kwargs["token_type_ids"] = token_type_ids
        else:
            rbln_model_input_names = self.rbln_model_config.model_input_names
            if "token_type_ids" in rbln_model_input_names:
                kwargs["token_type_ids"] = torch.zeros_like(input_ids)

        embeds = self.model.forward(**kwargs)

        hidden_states = embeds[0]

        if isinstance(hidden_states, tuple):
            hidden_states = hidden_states[0]

        batch_size = model_input.input_tokens.shape[0]
        if not self.is_classification_arch():
            # Depad hidden_states for original valid batch_size and length.
            hidden_states = hidden_states[:batch_size]
            prompt_lens = max_position[:batch_size] + 1

            new_hidden_states = []
            for idx, prompt_len in enumerate(prompt_lens):
                new_hidden_states.append(hidden_states[idx, :prompt_len])
            hidden_states = torch.cat(new_hidden_states, dim=0)
        else:
            hidden_states = hidden_states[:batch_size].view(-1)

        return hidden_states


class RBLNOptimumLlavaNextForConditionalGeneration(RBLNOptimumForCausalLM):

    def merge_multimodal_embeddings(
        self,
        input_ids: torch.Tensor,
        inputs_embeds: torch.Tensor,
        multimodal_embeddings: torch.Tensor,
        placeholder_token_id: int,
    ) -> torch.Tensor:
        mask = input_ids == placeholder_token_id
        num_expected_tokens = mask.sum().item()

        if multimodal_embeddings.shape[0] != num_expected_tokens:
            raise ValueError(
                f"Attempted to assign {inputs_embeds[mask].shape}"
                f" = {multimodal_embeddings.shape} "
                f"multimodal tokens to {num_expected_tokens} placeholders")

        inputs_embeds[mask] = multimodal_embeddings
        return inputs_embeds

    def _forward(
        self,
        is_prefill: bool,
        block_tables: torch.Tensor,
        input_ids: torch.LongTensor = None,
        pixel_values: torch.FloatTensor = None,
        image_sizes: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        vision_feature_layer: Optional[int] = None,
        vision_feature_select_strategy: Optional[str] = None,
        cache_position: Union[List[torch.Tensor],
                              torch.Tensor] = None,  # vllm keyword argument
        batch_idx: Optional[int] = None,
        **kwargs,
    ):
        if inputs_embeds is not None:
            raise NotImplementedError(
                "Specifying inputs_embeds is not supported.")

        if is_prefill:
            # Get text_embeds
            inputs_embeds = self.model.text_embedding(input_ids)

            # If any images in the prompt, get image_embeds and merge with text
            if pixel_values is not None and input_ids.shape[
                    1] != 1 and pixel_values.size(0) > 0:
                image_features, _ = self.model.image_embedding(
                    image_sizes, pixel_values, vision_feature_layer,
                    vision_feature_select_strategy)

                inputs_embeds = self.merge_multimodal_embeddings(
                    input_ids, inputs_embeds, image_features,
                    self.model.config.image_token_index)
        else:
            inputs_embeds = self.model.text_embedding(input_ids=input_ids)

        if is_prefill:
            if self.model.language_model.prefill_decoder is None:
                raise version_error

            logits = self.model.language_model.prefill_decoder(
                inputs_embeds=inputs_embeds,
                cache_position=cache_position,
                batch_idx=batch_idx,
                block_tables=block_tables.squeeze(0),
            ).logits
        else:
            if self.model.language_model.decoder is None:
                raise version_error

            logits = self.model.language_model.decoder(
                inputs_embeds=inputs_embeds,
                cache_position=cache_position,
                block_tables=block_tables,
            ).logits

        return logits

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        block_tables = model_input.block_tables

        batch_idx = block_tables[0][0] if is_prompt else None
        image_input = None

        padded_batch_size = self.decoder_batch_size
        original_batch_size = input_ids.shape[0]

        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            padded_batch_size = self.select_lower_bounded_batch_size(
                original_batch_size, self.decoder_batch_sizes)
            self.model.decoder = self.model.decoders[padded_batch_size]

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
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids,
                positions,
                block_tables,
                padded_batch_size=padded_batch_size)

        logits = self._forward(
            is_prefill=is_prompt,
            block_tables=block_tables,
            input_ids=input_ids.to(torch.int64),
            cache_position=positions.to(torch.int32),
            batch_idx=batch_idx,
            pixel_values=pixel_values,
            image_sizes=image_sizes,
        )

        if not is_prompt:
            logits = logits[:original_batch_size]
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


class RBLNOptimumQwen2_5_VLForConditionalGeneration(RBLNOptimumForCausalLM):

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config, scheduler_config)
        self.rope_deltas: Dict = dict()

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions.to(torch.int32)
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        block_tables = model_input.block_tables
        input_block_ids = input_block_ids = [
            block_table[0].item() for block_table in block_tables
        ]
        batch_idx = block_tables[0][0] if is_prompt else None
        image_input = None
        video_input = None

        if model_input.multi_modal_kwargs:
            image_input = self._parse_and_validate_image_input(
                **model_input.multi_modal_kwargs)
            video_input = self._parse_and_validate_video_input(
                **model_input.multi_modal_kwargs)

        if image_input is None and video_input is None:
            inputs_embeds = None

        if is_prompt:
            attention_mask = torch.ones_like(input_ids)
            (inputs_embeds, position_embed,
             rope_deltas) = self.model._preprocess_prefill(
                 input_ids=input_ids,
                 attention_mask=attention_mask,
                 pixel_values=image_input["pixel_values"]
                 if image_input is not None else None,
                 image_grid_thw=image_input["image_grid_thw"]
                 if image_input is not None else None,
                 pixel_values_videos=video_input["pixel_values_videos"]
                 if video_input is not None else None,
                 video_grid_thw=video_input["video_grid_thw"]
                 if video_input is not None else None,
                 second_per_grid_ts=video_input["second_per_grid_ts"]
                 if video_input is not None else None,
             )
            self.model.rope_deltas[batch_idx] = rope_deltas.item()
            logits = self.model.prefill_decoder(
                inputs_embeds=inputs_embeds,
                cache_position=positions,
                batch_idx=batch_idx,
                position_embed=position_embed,
            ).logits
        else:
            if input_ids.shape[0] != self.decoder_batch_size:
                input_ids = input_ids.expand(self.decoder_batch_size,
                                             *input_ids.shape[1:])
                positions = positions.expand(self.decoder_batch_size,
                                             *positions.shape[1:])

            inputs_embeds, position_embed = self.model._preprocess_decoder(
                input_ids, positions)
            logits = self.model.decoder(
                inputs_embeds=inputs_embeds,
                cache_position=positions,
                position_embed=position_embed,
            ).logits
        if not is_prompt:
            logits = logits[input_block_ids]
        return logits

    def _validate_and_reshape_mm_tensor(self, mm_input: object,
                                        name: str) -> torch.Tensor:
        if not isinstance(mm_input, (torch.Tensor, list)):
            raise ValueError(f"Incorrect type of {name}. "
                             f"Got type: {type(mm_input)}")
        if isinstance(mm_input, torch.Tensor):
            if mm_input.ndim == 2:
                return mm_input
            if mm_input.ndim != 3:
                raise ValueError(f"{name} should be 2D or batched 3D tensor. "
                                 f"Got ndim: {mm_input.ndim} "
                                 f"(shape={mm_input.shape})")
            return torch.concat(list(mm_input))
        else:
            return torch.concat(mm_input)

        raise RuntimeError(f"Unhandled case for input '{name}'")

    def _parse_and_validate_image_input(
            self, **kwargs: object) -> Optional[Qwen2_5_VLImageInputs]:
        pixel_values = kwargs.pop("pixel_values", None)
        image_embeds = kwargs.pop("image_embeds", None)
        image_grid_thw = kwargs.pop("image_grid_thw", None)

        if pixel_values is None and image_embeds is None:
            return None

        if pixel_values is not None:
            pixel_values = self._validate_and_reshape_mm_tensor(
                pixel_values, "image pixel values")
            image_grid_thw = self._validate_and_reshape_mm_tensor(
                image_grid_thw, "image grid_thw")

            if not isinstance(pixel_values, (torch.Tensor, list)):
                raise ValueError("Incorrect type of image pixel values. "
                                 f"Got type: {type(pixel_values)}")

            return Qwen2_5_VLImagePixelInputs(type="pixel_values",
                                              pixel_values=pixel_values,
                                              image_grid_thw=image_grid_thw)

        if image_embeds is not None:
            image_embeds = self._validate_and_reshape_mm_tensor(
                image_embeds, "image embeds")
            image_grid_thw = self._validate_and_reshape_mm_tensor(
                image_grid_thw, "image grid_thw")

            if not isinstance(image_embeds, torch.Tensor):
                raise ValueError("Incorrect type of image embeddings. "
                                 f"Got type: {type(image_embeds)}")
            return Qwen2_5_VLImageEmbeddingInputs(
                type="image_embeds",
                image_embeds=image_embeds,
                image_grid_thw=image_grid_thw)

        # fallback return if both are None
        return None

    # type: ignore[return]
    def _parse_and_validate_video_input(
            self, **kwargs: object) -> Optional[Qwen2_5_VLVideoInputs]:
        pixel_values_videos = kwargs.pop("pixel_values_videos", None)
        video_embeds = kwargs.pop("video_embeds", None)
        video_grid_thw = kwargs.pop("video_grid_thw", None)
        second_per_grid_ts = kwargs.pop("second_per_grid_ts", None)

        if pixel_values_videos is None and video_embeds is None:
            return None

        if pixel_values_videos is not None:
            pixel_values_videos = self._validate_and_reshape_mm_tensor(
                pixel_values_videos, "video pixel values")
            video_grid_thw = self._validate_and_reshape_mm_tensor(
                video_grid_thw, "video grid_thw")

            assert isinstance(second_per_grid_ts, torch.Tensor)

            return Qwen2_5_VLVideoPixelInputs(
                type="pixel_values_videos",
                pixel_values_videos=pixel_values_videos,
                video_grid_thw=video_grid_thw,
                second_per_grid_ts=second_per_grid_ts.squeeze(0),
            )

        if video_embeds is not None:
            video_embeds = self._validate_and_reshape_mm_tensor(
                video_embeds, "video embeds")
            video_grid_thw = self._validate_and_reshape_mm_tensor(
                video_grid_thw, "video grid_thw")

            if not isinstance(video_embeds, torch.Tensor):
                raise ValueError("Incorrect type of video embeddings. "
                                 f"Got type: {type(video_embeds)}")
            return Qwen2_5_VLVideoEmbeddingInputs(
                type="video_embeds",
                video_embeds=video_embeds,
                video_grid_thw=video_grid_thw)

        # fallback return if both are None
        return None


class RBLNOptimumIdefics3ForConditionalGeneration(RBLNOptimumForCausalLM):

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config=model_config,
                         scheduler_config=scheduler_config)

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions.to(torch.int32)
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        block_tables = model_input.block_tables

        batch_idx = block_tables[0][0] if is_prompt else None
        image_input = None

        padded_batch_size = self.decoder_batch_size
        original_batch_size = input_ids.shape[0]

        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            padded_batch_size = self.select_lower_bounded_batch_size(
                original_batch_size, self.decoder_batch_sizes)
            self.model.decoder = self.model.decoders[padded_batch_size]

        if model_input.multi_modal_kwargs:
            image_input = self._parse_and_validate_image_input(
                **model_input.multi_modal_kwargs)

        if is_prompt:
            # Only when image input is given
            if image_input is not None:
                pixel_values = image_input["pixel_values"].unsqueeze(0)
                pixel_attention_mask = image_input[
                    "pixel_attention_mask"].unsqueeze(0)
            else:
                pixel_values = None
                pixel_attention_mask = None

            inputs_embeds = self.model._preprocess_prefill(
                input_ids=input_ids,
                pixel_values=pixel_values,
                pixel_attention_mask=pixel_attention_mask,
            )
            logits = self.model.text_model.prefill_decoder(
                inputs_embeds=inputs_embeds,
                cache_position=positions,
                batch_idx=batch_idx,
                block_tables=block_tables.squeeze(0),
            ).logits
        else:
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids,
                positions,
                block_tables,
                padded_batch_size=padded_batch_size)

            logits = self.model.text_model.decoder(
                input_ids=input_ids,
                cache_position=positions,
                block_tables=block_tables,
            ).logits
        if not is_prompt:
            logits = logits[:original_batch_size]
        return logits

    def _validate_pixel_values(self, data: torch.Tensor) -> torch.Tensor:
        h = w = self.model.config.vision_config.image_size
        expected_dims = (3, h, w)

        def _validate_shape(d: torch.Tensor):
            actual_dims = tuple(d.shape)

            if actual_dims != expected_dims:
                expected_expr = str(expected_dims)
                raise ValueError(
                    "The expected shape of pixel values per image per batch "
                    f" per patch is {expected_expr}. "
                    f"You supplied {tuple(d.shape)}.")

        for d in data:
            _validate_shape(d)

        return data

    def _parse_and_validate_image_input(
            self, **kwargs: object) -> Optional[ImageInputs]:
        pixel_values = kwargs.pop("pixel_values", None)
        image_embeds = kwargs.pop("image_embeds", None)

        if pixel_values is None and image_embeds is None:
            return None

        if image_embeds is not None:
            if not isinstance(image_embeds, (torch.Tensor, list)):
                raise ValueError("Incorrect type of image embeddings. "
                                 f"Got type: {type(image_embeds)}")

            return Idefics3ImageEmbeddingInputs(
                type="image_embeds",
                data=flatten_bn(image_embeds, concat=True),
            )

        if pixel_values is not None:
            if not isinstance(pixel_values, (torch.Tensor, list)):
                raise ValueError("Incorrect type of pixel values. "
                                 f"Got type: {type(pixel_values)}")

            pixel_attention_mask = kwargs.pop("pixel_attention_mask")
            if not isinstance(pixel_attention_mask, (torch.Tensor, list)):
                raise ValueError("Incorrect type of pixel_attention_mask. "
                                 f"Got type: {type(pixel_attention_mask)}")

            num_patches = kwargs.pop("num_patches")
            if not isinstance(num_patches, (torch.Tensor, list)):
                raise ValueError("Incorrect type of num_patches. "
                                 f"Got type: {type(num_patches)}")

            pixel_values = flatten_bn(pixel_values, concat=True)
            pixel_attention_mask = flatten_bn(pixel_attention_mask,
                                              concat=True)
            num_patches = flatten_bn(num_patches, concat=True)

            return Idefics3ImagePixelInputs(
                type="pixel_values",
                pixel_values=self._validate_pixel_values(pixel_values),
                pixel_attention_mask=pixel_attention_mask,
                num_patches=num_patches,
            )

        raise AssertionError("This line should be unreachable.")


class RBLNOptimumGemma3ForConditionalGeneration(RBLNOptimumForCausalLM):

    @dataclass
    class SlidingWindowEntry:
        local_table_id: int
        padded_cache_length: int
        attention_mask: torch.Tensor

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config=model_config,
                         scheduler_config=scheduler_config)
        self.sliding_window_table: Dict[
            str,
            RBLNOptimumGemma3ForConditionalGeneration.SlidingWindowEntry] = {}

    def select_local_block_table_value(
        self,
        is_prompt: bool,
        input_ids: torch.Tensor,
        running_requests_ids: list[str],
        finished_requests_ids: Optional[list[str]],
    ) -> Tuple[list[int], list[int], list[torch.Tensor]]:
        if is_prompt:
            # Generate attention mask without padding
            attention_mask = torch.ones_like(input_ids).squeeze(0)

            if finished_requests_ids is not None and len(
                    finished_requests_ids) > 0:
                first_id = finished_requests_ids[0]
                local_table_id = self.sliding_window_table[
                    first_id].local_table_id

                for request_id in finished_requests_ids:
                    self.sliding_window_table.pop(request_id)
            else:
                used_ids = {
                    v.local_table_id
                    for v in self.sliding_window_table.values()
                }
                available_ids = set(range(self.decoder_batch_size)) - used_ids
                assert len(available_ids) > 0
                local_table_id = min(available_ids)

            if len(self.sliding_window_table) > self.decoder_batch_size:
                raise ValueError(
                    "Sliding window table size must not exceed the batch size."
                )

            return [local_table_id], [], [attention_mask]

        else:
            local_table_ids: List[int] = []
            padded_cache_lengths: List[int] = []
            attention_masks: List[torch.Tensor] = []

            for request_id in running_requests_ids:
                sliding_window = self.sliding_window_table[request_id]
                local_table_ids.append(sliding_window.local_table_id)
                padded_cache_lengths.append(sliding_window.padded_cache_length)
                attention_masks.append(sliding_window.attention_mask)

            return local_table_ids, padded_cache_lengths, attention_masks

    def pad_local_table_items(
        self,
        sliding_window_table_ids: List[int],
        attention_masks: List[torch.Tensor],
        position_ids: torch.Tensor,
        padded_cache_lengths: List[int],
        original_batch_size: int,
        padded_batch_size: int,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Validate input
        if original_batch_size > 0 and not attention_masks:
            raise ValueError(
                "attention_masks cannot be empty when original_batch_size > 0."
            )

        position_id_dtype = position_ids.dtype
        seq_len = attention_masks[0].shape[1] if attention_masks else 0

        # Determine padding value for local_block_table_id
        used_ids = set(sliding_window_table_ids)
        pad_value = next(
            (i for i in range(self.decoder_batch_size) if i not in used_ids),
            0)

        local_block_table_id = torch.full(
            (padded_batch_size, 1),
            pad_value,
            dtype=torch.int16,
        )
        local_block_table_id[:original_batch_size] = torch.tensor(
            sliding_window_table_ids, dtype=torch.int16).unsqueeze(1)

        padded_cache_lengths_tensor = torch.zeros(padded_batch_size,
                                                  1,
                                                  dtype=position_id_dtype)
        padded_cache_lengths_tensor[:original_batch_size] = torch.tensor(
            padded_cache_lengths, dtype=position_id_dtype).unsqueeze(1)

        attention_mask_dtype = attention_masks[
            0].dtype if attention_masks else torch.bool
        attention_mask = torch.zeros(padded_batch_size,
                                     seq_len,
                                     dtype=attention_mask_dtype)
        if attention_masks:
            attention_mask[:original_batch_size] = torch.cat(attention_masks)

        # cache_positions - the index including padding between text and image
        # padded_cache_lengths_tensor - the size of padding
        # position_ids - the index of the token to be decoded in the sequence.
        cache_positions = torch.zeros(padded_batch_size,
                                      1,
                                      dtype=position_id_dtype)
        cache_positions[:original_batch_size] = (
            position_ids[:original_batch_size] +
            padded_cache_lengths_tensor[:original_batch_size])

        return local_block_table_id, attention_mask, cache_positions

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        position_ids = model_input.input_positions.to(torch.int32)
        block_tables = model_input.block_tables
        is_prompt = model_input.sampling_metadata.num_prompts > 0

        running_requests_ids = model_input.running_requests_ids
        finished_requests_ids = model_input.finished_requests_ids
        request_nums = input_ids.shape[0]

        batch_idx = None

        # In prefill phase, the length of list must be 1
        sliding_window_table_ids, padded_cache_lengths, attention_masks = \
            self.select_local_block_table_value(
                is_prompt,
                input_ids,
                running_requests_ids,
                finished_requests_ids,
            )

        padded_batch_size = self.decoder_batch_size

        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            padded_batch_size = self.select_lower_bounded_batch_size(
                request_nums, self.decoder_batch_sizes)
            self.model.decoder = self.model.decoders[padded_batch_size]

        if is_prompt:
            block_tables = block_tables.squeeze(0)
        else:
            input_ids, position_ids, block_tables = self.preprocess_decode(
                input_ids,
                position_ids,
                block_tables,
                padded_batch_size=padded_batch_size)

        if is_prompt:
            inputs_embeds = None
            batch_idx = sliding_window_table_ids[0]
            # TODO(eunji): generate `token_type_ids`
            # token_type_ids model_input != token_type_ids of gemma3
            # https://github.com/huggingface/transformers/blob/d0c9c66d1c09df3cd70bf036e813d88337b20d4c/src/transformers/models/gemma3/processing_gemma3.py#L143
            token_type_ids = torch.zeros_like(input_ids)
            token_type_ids[input_ids ==
                           self.model.config.image_token_index] = 1

            pixel_values = self.get_pixel_values(model_input)
            inputs_embeds = self.model._preprocess_prefill(
                input_ids, inputs_embeds, pixel_values)
            if self.model.language_model.prefill_decoder is None:
                raise version_error
            attention_mask = attention_masks[0]

            output = self.model.language_model.prefill_decoder(
                inputs_embeds=inputs_embeds,
                cache_position=position_ids,
                attention_mask=attention_mask,
                batch_idx=batch_idx,
                block_tables=block_tables,
                token_type_ids=token_type_ids,
            )
            logits = output.logits
            updated_attention_mask = output.attention_mask
            updated_padded_cache_length = output.padded_cache_lengths

            assert len(running_requests_ids) == 1
            self.sliding_window_table[running_requests_ids[0]] = \
                RBLNOptimumGemma3ForConditionalGeneration.SlidingWindowEntry(
                    sliding_window_table_ids[0], updated_padded_cache_length,
                    updated_attention_mask)

        else:
            if self.model.language_model.decoders is None:
                raise ValueError("Decoders is None")

            local_block_table_id, attention_mask, cache_position \
                    = self.pad_local_table_items(sliding_window_table_ids,
                                                 attention_masks,
                                                 position_ids,
                                                 padded_cache_lengths,
                                                 request_nums,
                                                 padded_batch_size)

            rows = torch.arange(attention_mask.size(0))
            cols = cache_position.squeeze(1)

            attention_mask[rows, cols] = 1

            logits = self.model.language_model.decoder(
                input_ids=input_ids,
                cache_position=cache_position.to(torch.int32),
                batch_idx=batch_idx,
                block_tables=block_tables,
                local_block_tables=local_block_table_id,
                attention_mask=attention_mask,
                position_ids=position_ids,
            ).logits

            # Update attention mask of newly generated token
            for idx, request_id in enumerate(running_requests_ids):
                self.sliding_window_table[
                    request_id].attention_mask = attention_mask[idx:idx + 1]

        if not is_prompt:
            logits = logits[:request_nums]
        return logits

    def _parse_and_validate_image_input(
            self, **kwargs: object) -> Optional[Gemma3ImageInputs]:
        pixel_values: torch.Tensor = kwargs.get("pixel_values")
        num_crops: torch.Tensor = kwargs.get("num_crops")
        embed_is_patch = kwargs.get("embed_is_patch")
        num_embeds = kwargs.get("num_embeds")

        pixel_values = pixel_values.squeeze(0)

        if pixel_values is None:
            return None

        if not isinstance(pixel_values, (torch.Tensor, list)):
            raise ValueError("Incorrect type of pixel values. "
                             f"Got type: {type(pixel_values)}")

        return Gemma3ImagePixelInputs(
            type="pixel_values",
            pixel_values=self._validate_pixel_values(pixel_values),
            num_patches=num_crops + 1,
            embed_is_patch=embed_is_patch,
            num_embeds=num_embeds,
        )

    def _validate_pixel_values(self, data: torch.Tensor) -> torch.Tensor:
        h = w = self.model.config.vision_config.image_size
        expected_dims = (3, h, w)

        def _validate_shape(d: torch.Tensor):
            actual_dims = tuple(d.shape)

            if actual_dims != expected_dims:
                expected_expr = str(expected_dims)
                raise ValueError(
                    "The expected shape of pixel values per image per batch "
                    f" per patch is {expected_expr}. "
                    f"You supplied {tuple(d.shape)}.")

        for d in data:
            _validate_shape(d)

        return data

    def get_pixel_values(self, model_input: ModelInputForRBLN):
        image_input = None

        if model_input.multi_modal_kwargs:
            image_input = self._parse_and_validate_image_input(
                **model_input.multi_modal_kwargs)
            if image_input is not None:
                assert image_input["type"] == "pixel_values"
                pixel_values = image_input["pixel_values"]

        else:
            pixel_values = None

        return pixel_values


class RBLNOptimumBlip2ForConditionalGeneration(RBLNOptimumForCausalLM):

    def __init__(
        self,
        model_config: ModelConfig,
        scheduler_config: SchedulerConfig,
    ) -> None:
        super().__init__(model_config=model_config,
                         scheduler_config=scheduler_config)

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions.to(torch.int32)
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        block_tables = model_input.block_tables

        batch_idx = block_tables[0][0] if is_prompt else None
        image_input = None
        pixel_values = None

        padded_batch_size = self.decoder_batch_size
        original_batch_size = input_ids.shape[0]

        if getattr(self.model.rbln_config, "use_multiple_decoder", None):
            padded_batch_size = self.select_lower_bounded_batch_size(
                original_batch_size, self.decoder_batch_sizes)
            self.model.decoder = self.model.decoders[padded_batch_size]

        if model_input.multi_modal_kwargs:
            image_input = self._parse_and_validate_image_input(
                **model_input.multi_modal_kwargs)
            if image_input is not None:
                assert image_input["type"] == "pixel_values"
                pixel_values = image_input["data"]

        if is_prompt:
            inputs_embeds = self.model._preprocess_prefill(
                pixel_values=pixel_values,
                input_ids=input_ids,
            )
            logits = self.model.language_model.prefill_decoder(
                inputs_embeds=inputs_embeds,
                cache_position=positions,
                batch_idx=batch_idx,
                block_tables=block_tables.squeeze(0),
            ).logits
        else:
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids,
                positions,
                block_tables,
                padded_batch_size=padded_batch_size)
            logits = self.model.language_model.decoder(
                input_ids=input_ids,
                cache_position=positions,
                block_tables=block_tables,
            ).logits
        if not is_prompt:
            logits = logits[:original_batch_size]
        return logits

    def _validate_pixel_values(self, data: torch.Tensor) -> torch.Tensor:
        h = w = self.model.config.vision_config.image_size
        expected_dims = (3, h, w)
        actual_dims = tuple(data.shape[1:])

        if actual_dims != expected_dims:
            expected_expr = ("batch_size", *map(str, expected_dims))
            raise ValueError(
                f"The expected shape of pixel values is {expected_expr}. "
                f"You supplied {tuple(data.shape)}.")

        return data

    def _parse_and_validate_image_input(
            self, **kwargs: object) -> Optional[Blip2ImageInputs]:
        pixel_values = kwargs.pop("pixel_values", None)
        image_embeds = kwargs.pop("image_embeds", None)

        if pixel_values is None and image_embeds is None:
            return None

        if pixel_values is not None:
            if not isinstance(pixel_values, (torch.Tensor, list)):
                raise ValueError("Incorrect type of pixel values. "
                                 f"Got type: {type(pixel_values)}")

            pixel_values = flatten_bn(pixel_values, concat=True)

            return Blip2ImagePixelInputs(
                type="pixel_values",
                data=self._validate_pixel_values(pixel_values),
            )

        if image_embeds is not None:
            if not isinstance(image_embeds, (torch.Tensor, list)):
                raise ValueError("Incorrect type of image embeddings. "
                                 f"Got type: {type(image_embeds)}")

            image_embeds = flatten_bn(image_embeds, concat=True)

            return Blip2ImageEmbeddingInputs(
                type="image_embeds",
                data=image_embeds,
            )

        raise AssertionError("This line should be unreachable.")


class RBLNOptimumEncoderDecoder(RBLNOptimumForCausalLM):
    INVALID_TOKEN = 100

    def _forward(
        self,
        enc_lengths: List[int],  # current attention_mask length
        input_ids: torch.LongTensor = None,
        cache_position: Union[List[torch.Tensor], torch.Tensor] = None,
        batch_idx: Optional[torch.LongTensor] = None,
        block_tables: torch.Tensor = None,
        **kwargs,
    ):
        # When using vLLM, the output of the encoder needs to include
        # an additional token (e.g., vocab_size + INVALID_TOKEN).
        # This value serves as the start_token_id in the decoder.
        # The decoder will then use (vocab_size + INVALID_TOKEN - 1)
        # as the actual start_token_id.

        # Encoder
        if batch_idx is not None:
            enc_attention_mask = torch.zeros(
                1, self.model.rbln_config.enc_max_seq_len, dtype=torch.float32)
            enc_attention_mask[0][:enc_lengths[batch_idx] + 1] = 1

            padding_need = (self.model.rbln_config.enc_max_seq_len -
                            input_ids.shape[-1])
            input_ids = torch.nn.functional.pad(input_ids, (0, padding_need))

            _ = self.model.encoder(input_ids,
                                   enc_attention_mask,
                                   block_tables=block_tables.squeeze(0))

            logits = torch.zeros(
                1, 1, self.model.config.vocab_size + self.INVALID_TOKEN)
            # Set the probability of INVALID_TOKEN (the last token in
            # the logits tensor) to 1.0.
            logits[0][0][-1] = 1

        # Decoder
        else:
            # Replace INVALID_TOKEN markers with the decoder start token ID
            input_ids[input_ids == (
                self.model.config.vocab_size + self.INVALID_TOKEN -
                1)] = self.model.config.decoder_start_token_id
            cache_position[cache_position !=
                           0] = cache_position[cache_position != 0] - 2

            enc_attention_mask = torch.zeros(
                self.model.rbln_config.batch_size,
                self.model.rbln_config.enc_max_seq_len,
                dtype=torch.float32,
            )
            dec_attention_mask = torch.zeros(
                self.model.rbln_config.batch_size,
                self.model.rbln_config.dec_max_seq_len,
                dtype=torch.float32,
            )

            for batch_idx in range(self.model.rbln_config.batch_size):
                enc_attention_mask[batch_idx, :enc_lengths[batch_idx] + 1] = 1

            if self.model.decoder is None:
                raise version_error

            logits = self.model.decoder(
                decoder_input_ids=input_ids,
                attention_mask=enc_attention_mask,
                decoder_attention_mask=dec_attention_mask,
                cache_position=cache_position,
                block_tables=block_tables,
            ).logits

        return logits

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
        block_tables = model_input.block_tables
        input_block_ids = input_block_ids = [
            block_table[0].item() for block_table in block_tables
        ]
        batch_idx = block_tables[0][0] if is_prompt else None

        if not is_prompt:
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids,
                positions,
                block_tables,
                input_block_ids=input_block_ids)
        else:
            # prefill batch_size is always 1
            assert positions.shape[0] == 1
            self.enc_lengths[batch_idx] = positions[0][-1].item()

        logits = self._forward(
            input_ids=input_ids.to(torch.int64),
            cache_position=positions.to(torch.int32),
            batch_idx=batch_idx,
            enc_lengths=self.enc_lengths,
            block_tables=block_tables,
        )

        if not is_prompt:
            logits = logits[input_block_ids]

        return logits


def is_multi_modal(config: PretrainedConfig) -> bool:
    return is_arch_supported(config, _RBLN_MULTIMODAL_MODELS)


def is_pooling_arch(config: PretrainedConfig) -> bool:
    return is_arch_supported(config, _RBLN_EMBEDDING_MODELS)


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
        architectures = getattr(model_config.hf_config, "architectures", [])
        if architectures[0] in ["Qwen2_5_VLForConditionalGeneration"]:
            rbln_model = RBLNOptimumQwen2_5_VLForConditionalGeneration(
                model_config=model_config, scheduler_config=scheduler_config)
        elif architectures[0] in ["Idefics3ForConditionalGeneration"]:
            rbln_model = RBLNOptimumIdefics3ForConditionalGeneration(
                model_config=model_config, scheduler_config=scheduler_config)
        elif architectures[0] in ["Blip2ForConditionalGeneration"]:
            rbln_model = RBLNOptimumBlip2ForConditionalGeneration(
                model_config=model_config, scheduler_config=scheduler_config)
        elif architectures[0] in ["Gemma3ForConditionalGeneration"]:
            rbln_model = RBLNOptimumGemma3ForConditionalGeneration(
                model_config=model_config, scheduler_config=scheduler_config)
        else:
            rbln_model = RBLNOptimumLlavaNextForConditionalGeneration(
                model_config=model_config, scheduler_config=scheduler_config)
    elif is_enc_dec_arch(model_config.hf_config):
        rbln_model = RBLNOptimumEncoderDecoder(
            model_config=model_config, scheduler_config=scheduler_config)
    elif is_pooling_arch(model_config.hf_config):
        rbln_model = RBLNOptimumForEncoderModel(
            model_config=model_config, scheduler_config=scheduler_config)
    else:
        rbln_model = RBLNOptimumForCausalLM(model_config=model_config,
                                            scheduler_config=scheduler_config)
    return rbln_model.eval()
