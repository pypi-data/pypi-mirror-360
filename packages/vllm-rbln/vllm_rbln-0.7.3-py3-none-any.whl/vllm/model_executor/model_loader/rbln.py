"""Utilities for selecting and loading rbln models."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import (TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple,
                    TypedDict, Union)

import optimum.rbln
import torch
import torch.nn as nn
from transformers import PretrainedConfig
from typing_extensions import NotRequired

from vllm.config import ModelConfig, SchedulerConfig
from vllm.logger import init_logger
from vllm.model_executor.layers.logits_processor import LogitsProcessor
from vllm.model_executor.layers.sampler import Sampler, SamplerOutput
from vllm.model_executor.models.utils import flatten_bn
from vllm.model_executor.sampling_metadata import SamplingMetadata
from vllm.multimodal import BatchedTensorInputs
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
}

_RBLN_ENCODER_DECODER_MODELS: Dict[str, Tuple[str, str]] = {
    "BartForConditionalGeneration":
    ("bart", "RBLNBartForConditionalGeneration"),
    "T5ForConditionalGeneration": ("t5", "RBLNT5ForConditionalGeneration"),
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


def nullable_ints(val: str) -> Optional[Union[int, List[int]]]:
    """Parses a string containing comma-separated integers or a single integer.

    Args:
        val: String value to be parsed.

    Returns:
        An integer if the string represents a single value, a list of integers 
        if it contains multiple values, or None if the input is empty.
    """
    if not val:
        return None

    items = [item.strip() for item in val.split(",")]

    try:
        parsed_values = [int(item) for item in items]
    except ValueError as exc:
        raise ValueError("device_id should be integers.") from exc

    return parsed_values[0] if len(parsed_values) == 1 else parsed_values


class LlavaNextImagePixelInputs(TypedDict):
    type: Literal["pixel_values"]
    data: Union[torch.Tensor, List[torch.Tensor]]
    """
    Shape:
    `(batch_size * num_images, 1 + num_patches, num_channels, height, width)`

    Note that `num_patches` may be different per batch and image,
    in which case the data is passed as a list instead of a batched tensor.
    """

    image_sizes: NotRequired[torch.Tensor]
    """
    Shape: `(batch_size * num_images, 2)`

    This should be in `(height, width)` format.
    """


class LlavaNextImageEmbeddingInputs(TypedDict):
    type: Literal["image_embeds"]
    data: torch.Tensor
    """Shape: `(batch_size * num_images, image_feature_size, hidden_size)`

    `hidden_size` must match the hidden size of language model backbone.
    """


LlavaNextImageInputs = Union[LlavaNextImagePixelInputs,
                             LlavaNextImageEmbeddingInputs]


@dataclass(frozen=True)
class ModelInputForRBLN(ModelRunnerInputBase):
    """
    Used by the RBLNModelRunner.
    """
    input_tokens: torch.Tensor
    input_positions: torch.Tensor
    block_tables: torch.Tensor
    sampling_metadata: "SamplingMetadata"
    multi_modal_kwargs: Optional[BatchedTensorInputs] = None

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
        self.decoder_batch_size = self.scheduler_config.max_num_seqs
        self.logits_processor = LogitsProcessor(
            model_config.hf_config.vocab_size, logits_as_input=True)
        self.sampler = Sampler()
        self.init_model()
        self.padding_value = self.get_padding_value()

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

        if not is_prompt:
            input_block_ids = [
                block_table[0].item() for block_table in block_tables
            ]
            input_ids, positions, block_tables = self.preprocess_decode(
                input_ids, positions, input_block_ids, block_tables)
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

            return self.model.prefill_decoder(**kwargs)

        if self.model.decoder is None:
            raise version_error

        logits = self.model.decoder(**kwargs)
        if self.attn_impl != "flash_attn":
            return logits[input_block_ids]

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
        self.rbln_model_config = model.rbln_config.model_cfg
        self.attn_impl = self.rbln_model_config.get('attn_impl', None)

    def get_padding_value(self):
        rbln_model_config = self.rbln_model_config
        attn_impl = rbln_model_config.get('attn_impl', None)
        padding = -1
        if attn_impl is not None and attn_impl == "flash_attn":
            # For flash attention, the last block is the dummy block
            padding = rbln_model_config.get('kvcache_num_blocks', 0) - 1

            if npu_num_blocks := os.environ.get("VLLM_RBLN_NPU_NUM_BLOCKS"):
                padding = int(npu_num_blocks) - 1

        return padding

    def preprocess_decode(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        input_block_ids: torch.Tensor,
        block_tables: torch.Tensor,
    ):
        assert input_ids.shape[1] == 1
        padded_input_ids = torch.zeros(self.decoder_batch_size,
                                       1,
                                       dtype=input_ids.dtype)
        padded_position_ids = torch.zeros(self.decoder_batch_size,
                                          1,
                                          dtype=positions.dtype)
        padded_block_tables = torch.zeros(self.decoder_batch_size,
                                          block_tables.shape[1],
                                          dtype=block_tables.dtype).fill_(
                                              self.padding_value)

        if self.attn_impl != "flash_attn":
            padded_input_ids[input_block_ids] = input_ids
            padded_position_ids[input_block_ids] = positions
            padded_block_tables[input_block_ids] = block_tables

            available_blocks = torch.arange(0,
                                            self.decoder_batch_size,
                                            dtype=block_tables.dtype)
            unused_blocks = available_blocks[
                ~torch.isin(available_blocks, block_tables.flatten())]
            if unused_blocks.numel() > 0:
                first_unused_block = unused_blocks[0]
                # Create a mask where indices were NOT set by input_block_ids
                mask = torch.ones(self.decoder_batch_size, dtype=torch.bool)
                mask[input_block_ids] = False
                # Apply the mask to set remaining entries
                padded_block_tables[mask] = first_unused_block
        else:
            batch_size = input_ids.shape[0]
            padded_input_ids[:batch_size] = input_ids
            padded_position_ids[:batch_size] = positions
            padded_block_tables[:batch_size] = block_tables

        return padded_input_ids, padded_position_ids, padded_block_tables


class RBLNOptimumConditionalGeneration(RBLNOptimumForCausalLM):

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
            )
        else:
            if self.model.language_model.decoder is None:
                raise version_error

            logits = self.model.language_model.decoder(
                inputs_embeds=inputs_embeds,
                cache_position=cache_position,
            )

        return logits

    def forward(self, model_input: ModelInputForRBLN) -> torch.Tensor:
        input_ids = model_input.input_tokens
        positions = model_input.input_positions
        is_prompt = model_input.sampling_metadata.num_prompts > 0
        block_tables = model_input.block_tables
        input_block_ids = input_block_ids = [
            block_table[0].item() for block_table in block_tables
        ]

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
                input_ids, positions, input_block_ids, block_tables)

        batch_idx = block_tables[0][0] if is_prompt else None

        logits = self._forward(
            is_prefill=is_prompt,
            input_ids=input_ids.to(torch.int64),
            cache_position=positions.to(torch.int32),
            batch_idx=batch_idx,
            pixel_values=pixel_values,
            image_sizes=image_sizes,
        )

        if not is_prompt:
            logits = logits[input_block_ids]
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
                1,
                self.model.rbln_config.model_cfg["enc_max_seq_len"],
                dtype=torch.float32)
            enc_attention_mask[0][:enc_lengths[batch_idx] + 1] = 1

            padding_need = self.model.rbln_config.model_cfg[
                "enc_max_seq_len"] - input_ids.shape[-1]
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
                self.model.rbln_config.model_cfg["batch_size"],
                self.model.rbln_config.model_cfg["enc_max_seq_len"],
                dtype=torch.float32,
            )
            dec_attention_mask = torch.zeros(
                self.model.rbln_config.model_cfg["batch_size"],
                self.model.rbln_config.model_cfg["dec_max_seq_len"],
                dtype=torch.float32,
            )

            for batch_idx in range(
                    self.model.rbln_config.model_cfg["batch_size"]):
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
                input_ids, positions, input_block_ids, block_tables)
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
