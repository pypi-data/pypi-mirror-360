from typing import List, Optional, Tuple

import torch
from torch import nn

from vllm.config import (DeviceConfig, ModelConfig, ParallelConfig,
                         SchedulerConfig)
from vllm.logger import init_logger
from vllm.model_executor import SamplingMetadata
from vllm.model_executor.model_loader.rbln import get_rbln_model
from vllm.sequence import (CompletionSequenceGroupOutput, Logprob,
                           SamplerOutput, SequenceGroupMetadata,
                           SequenceOutput)
from vllm.utils import is_pin_memory_available, make_tensor_with_pad

logger = init_logger(__name__)


class RBLNModelRunner:

    def __init__(
        self,
        model_config: ModelConfig,
        parallel_config: ParallelConfig,
        scheduler_config: SchedulerConfig,
        device_config: DeviceConfig,
    ):
        self.model_config = model_config
        self.parallel_config = parallel_config
        self.scheduler_config = scheduler_config

        if model_config is not None and model_config.get_sliding_window():
            logger.warning("Sliding window is not supported on RBLN. "
                           "The model will run without sliding window.")
        self.device_config = (device_config
                              if device_config is not None else DeviceConfig())
        self.device = self.device_config.device
        self.pin_memory = is_pin_memory_available()

        # Lazy initialization.
        self.model: nn.Module  # initialize after load_model.

    def load_model(self) -> None:
        self.model = get_rbln_model(model_config=self.model_config,
                                    scheduler_config=self.scheduler_config)

    def _prepare_prompt(
        self,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[int]]:
        assert len(seq_group_metadata_list) > 0
        input_tokens: List[List[int]] = []
        input_positions: List[List[int]] = []
        input_block_ids: List[int] = []

        seq_lens: List[int] = []
        for seq_group_metadata in seq_group_metadata_list:
            assert seq_group_metadata.is_prompt
            seq_ids = list(seq_group_metadata.seq_data.keys())
            assert len(seq_ids) == 1
            seq_id = seq_ids[0]

            seq_data = seq_group_metadata.seq_data[seq_id]
            prompt_tokens = seq_data.get_token_ids()
            seq_len = len(prompt_tokens)
            seq_lens.append(seq_len)

            input_tokens.append(prompt_tokens)
            input_positions.append(list(range(seq_len)))

            assert seq_group_metadata.block_tables is not None
            block_table = seq_group_metadata.block_tables[seq_id]
            assert len(block_table) == 1
            input_block_ids.append(block_table[0])

        max_seq_len = max(seq_lens)
        assert max_seq_len > 0
        input_tokens = make_tensor_with_pad(input_tokens,
                                            max_len=max_seq_len,
                                            pad=0,
                                            dtype=torch.long,
                                            device=self.device)
        input_positions = make_tensor_with_pad(input_positions,
                                               max_len=max_seq_len,
                                               pad=0,
                                               dtype=torch.long,
                                               device=self.device)
        input_block_ids = torch.tensor(input_block_ids,
                                       dtype=torch.long,
                                       device=self.device)

        return input_tokens, input_positions, input_block_ids, seq_lens

    def _prepare_decode(
        self,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        assert len(seq_group_metadata_list) > 0
        input_tokens: List[List[int]] = []
        input_positions: List[List[int]] = []
        input_block_ids: List[int] = []
        context_lens: List[int] = []

        for seq_group_metadata in seq_group_metadata_list:
            assert not seq_group_metadata.is_prompt

            seq_ids = list(seq_group_metadata.seq_data.keys())

            for seq_id in seq_ids:
                seq_data = seq_group_metadata.seq_data[seq_id]
                generation_token = seq_data.get_last_token_id()
                input_tokens.append([generation_token])

                seq_len = seq_data.get_len()
                position = seq_len - 1
                input_positions.append([position])
                context_lens.append(seq_len)

                assert seq_group_metadata.block_tables is not None
                block_table = seq_group_metadata.block_tables[seq_id]
                assert len(block_table) >= 1
                for i in range(len(block_table)):
                    input_block_ids.append(block_table[i])

        input_tokens = make_tensor_with_pad(input_tokens,
                                            max_len=1,
                                            pad=0,
                                            dtype=torch.long,
                                            device=self.device)
        input_positions = make_tensor_with_pad(input_positions,
                                               max_len=1,
                                               pad=0,
                                               dtype=torch.long,
                                               device=self.device)
        context_lens = torch.tensor(context_lens,
                                    dtype=torch.int,
                                    device=self.device)
        input_block_ids = torch.tensor(input_block_ids,
                                       dtype=torch.long,
                                       device=self.device)

        return input_tokens, input_positions, input_block_ids

    def prepare_input_tensors(
        self,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, SamplingMetadata]:
        # NOTE: We assume that all sequences in the group are all prompts or
        # all decodes.
        is_prompt = seq_group_metadata_list[0].is_prompt
        # Prepare input tensors.
        if is_prompt:
            (input_tokens, input_positions, input_block_ids,
             seq_lens) = self._prepare_prompt(seq_group_metadata_list)
        else:
            (input_tokens, input_positions,
             input_block_ids) = self._prepare_decode(seq_group_metadata_list)
            seq_lens = []
        sampling_metadata = SamplingMetadata.prepare(
            seq_group_metadata_list,
            seq_lens,
            # query_lens is not needed if chunked prefill is not
            # supported. Since rbln worker doesn't support chunked prefill
            # just use seq_lens instead.
            seq_lens,
            self.device,
            self.pin_memory)

        return (input_tokens, input_positions, input_block_ids,
                sampling_metadata)

    @torch.inference_mode()
    def execute_model(
        self,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ) -> Optional[SamplerOutput]:
        (input_tokens, input_positions, input_block_ids, sampling_metadata
         ) = self.prepare_input_tensors(seq_group_metadata_list)

        hidden_states = None
        # CausalLMOutput {hidden_states, logits}
        batch, seq_len = input_tokens.shape
        attn_mask = torch.ones(batch, seq_len, dtype=torch.int64)

        # original huggingface transformer model
        causal_lm_output = self.model(
            input_ids=input_tokens,
            attn_mask=attn_mask,
            positions=input_positions,
            seq_group_metadata_list=seq_group_metadata_list,
            output_hidden_states=True,
            use_cache=True,
            return_dict=True,
        )
        assert causal_lm_output is not None
        assert causal_lm_output.logits is not None
        # causal lm output generates logits
        hidden_states = causal_lm_output.logits

        # Compute the logits.
        # select last sequence in logits
        if hidden_states is not None:
            assert hidden_states.dim() == 3
            hidden_states = hidden_states[:, -1, :]
            assert hidden_states.dim() == 2
        logits = self.model.compute_logits(hidden_states, sampling_metadata)

        # Sample the next token.
        output = self.model.sample(
            logits=logits,
            sampling_metadata=sampling_metadata,
        )
        return output

    def dummy_sample(
        self,
        logits: torch.Tensor,
        seq_group_metadata_list: List[SequenceGroupMetadata],
    ) -> Optional[SamplerOutput]:
        """generates dummy sampler output
        """
        group_logprobs = None
        sampler_output = []
        # for sequence groups, calculate log_probs & select next token index
        # calculate log_softmax from random logits
        log_probs = torch.log_softmax(logits, dim=-1, dtype=torch.float)
        # select argmax (=token index) as next token id
        next_token_ids = torch.argmax(log_probs, dim=-1)
        assert log_probs.shape[0] == len(seq_group_metadata_list)
        assert next_token_ids.shape[0] == len(seq_group_metadata_list)
        batch_idx = 0
        for seq_group_metadata in seq_group_metadata_list:
            # sequence group
            seq_outputs = []
            for seq_id, seq_data in seq_group_metadata.seq_data.items():
                next_token_id = next_token_ids[batch_idx]
                logprobs = {
                    next_token_id:
                    Logprob(logprob=log_probs[batch_idx, next_token_id],
                            rank=1,
                            decoded_token=None)
                }
                seq_outputs.append(
                    SequenceOutput(
                        parent_seq_id=seq_id,
                        output_token=next_token_id,
                        logprobs=logprobs,
                    ))
                batch_idx = batch_idx + 1
            seq_group_output = CompletionSequenceGroupOutput(
                seq_outputs, group_logprobs)

            sampler_output.append(seq_group_output)
        assert batch_idx == log_probs.shape[0]
        assert batch_idx == next_token_ids.shape[0]
        output = SamplerOutput(outputs=sampler_output)
        return output

    @property
    def vocab_size(self) -> int:
        return self.model_config.get_vocab_size()
