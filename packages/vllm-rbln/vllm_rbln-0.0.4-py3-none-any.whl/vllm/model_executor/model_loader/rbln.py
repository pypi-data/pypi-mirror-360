"""Utilities for selecting and loading rbln models."""

import os
from typing import Dict, List, Optional, Tuple

import optimum.rbln
import torch
import torch.nn as nn
from transformers import PretrainedConfig
from transformers.modeling_outputs import CausalLMOutputWithPast

from vllm.config import ModelConfig, SchedulerConfig
from vllm.logger import init_logger
from vllm.model_executor.layers.logits_processor import LogitsProcessor
from vllm.model_executor.layers.sampler import Sampler
from vllm.model_executor.sampling_metadata import SamplingMetadata
from vllm.sequence import SamplerOutput, SequenceGroupMetadata

logger = init_logger(__name__)

# modified/customized models for RBLN
_RBLN_SUPPORTED_MODELS: Dict[str, Tuple[str, str]] = {
    "LlamaForCausalLM": (
        "llama",
        "RBLNLlamaForCausalLM",
    ),
    "GemmaForCausalLM": ("gemma", "RBLNGemmaForCausalLM"),
    "GPT2LMHeadModel": ("gpt2", "RBLNGPT2LMHeadModel"),
    "MidmLMHeadModel": ("midm", "RBLNMidmLMHeadModel"),
}


def extract_batch_idx(seq_group_metadata: SequenceGroupMetadata):
    """Extracts batch index to be mapped to RBLN
    """
    seq_ids = list(seq_group_metadata.seq_data.keys())
    assert len(seq_ids) == 1
    request_id = seq_ids[0]

    block_table = seq_group_metadata.block_tables[request_id]
    assert len(block_table) == 1
    return block_table[0]


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

    def forward(
        self,
        input_ids: torch.Tensor,
        attn_mask: torch.Tensor,
        positions: torch.Tensor,
        seq_group_metadata_list: List[SequenceGroupMetadata],
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> torch.Tensor:
        batch, seq_len = input_ids.shape
        # prompt or decode start position
        current_step = positions[0][0]
        logger.debug("batch_size = %s", batch)
        logger.debug("current step = %s", current_step)
        logger.debug("given input_ids = %s", input_ids)
        logger.debug("given query_length = %s", seq_len)

        is_prefill = seq_group_metadata_list[0].is_prompt
        logger.debug("is_prefill = %s", is_prefill)

        if not is_prefill:
            input_ids, positions = self.preprocess_decode(
                input_ids, positions, seq_group_metadata_list)
        batch_indices = self.get_batch_indices(seq_group_metadata_list)
        batch_idx = batch_indices[0] if is_prefill else None

        # optimum.rbln forward()
        logits = self.model.forward(input_ids=input_ids.to(torch.int64),
                                    cache_position=positions.to(torch.int32),
                                    batch_idx=batch_idx)
        if not is_prefill:
            logits = self.postprocess_decode(logits, seq_group_metadata_list)
        return logits

    def init_model(self) -> None:
        config = self.model_config.hf_config
        model_name, model_cls_name = get_rbln_model_info(config)

        compiled_path = self.model_config.compiled_model_dir
        if compiled_path is None or not os.path.exists(compiled_path):
            raise RuntimeError("compiled_model_dir does not exist")

        # huggingface model class name
        logger.info("model_name = %s, model_cls_name = %s, model_path = %s",
                    model_name, model_cls_name, compiled_path)

        # huggingface model class
        model_cls = getattr(optimum.rbln, model_cls_name)
        assert model_cls is not None
        # load RBLN compiler binary model
        model = model_cls.from_pretrained(compiled_path, export=False)
        self.model = model

    def get_batch_indices(
            self, seq_group_metadata_list: List[SequenceGroupMetadata]):
        batch_indices = []
        for seq_group_metadata in seq_group_metadata_list:
            batch_indices.append(extract_batch_idx(seq_group_metadata))

        return batch_indices

    def preprocess_decode(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ):
        assert input_ids.shape[1] == 1
        padded_input_ids = torch.zeros(self.decoder_batch_size, 1)
        padded_position_ids = torch.zeros(self.decoder_batch_size,
                                          1,
                                          dtype=torch.int32)
        for i, seq_group_metadata in enumerate(seq_group_metadata_list):
            batch_idx = extract_batch_idx(seq_group_metadata)
            padded_input_ids[batch_idx, :] = input_ids[i, :]
            padded_position_ids[batch_idx, :] = positions[i, :]

        return padded_input_ids, padded_position_ids

    def postprocess_decode(
            self, output: CausalLMOutputWithPast,
            seq_group_metadata_list: List[SequenceGroupMetadata]):
        input_batch_size = len(seq_group_metadata_list)
        logits = output.logits
        sliced_logits = torch.zeros(input_batch_size, *logits.shape[1:])

        for i, seq_group_metadata in enumerate(seq_group_metadata_list):
            batch_idx = extract_batch_idx(seq_group_metadata)
            sliced_logits[i, :] = logits[batch_idx, :]

        output.logits = sliced_logits
        return output


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
    rbln_model = RBLNOptimumForCausalLM(model_config=model_config,
                                        scheduler_config=scheduler_config)
    return rbln_model.eval()
