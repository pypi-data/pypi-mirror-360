from typing import TYPE_CHECKING, Optional

import torch

from vllm.logger import init_logger

from .interface import Platform, PlatformEnum

if TYPE_CHECKING:
    from vllm.config import VllmConfig
else:
    VllmConfig = None

logger = init_logger(__name__)


class RblnPlatform(Platform):
    _enum = PlatformEnum.RBLN
    device_name: str = "rbln"
    device_type: str = "rbln"
    dispatch_key: str = "CPU"

    @classmethod
    def is_async_output_supported(cls, enforce_eager: Optional[bool]) -> bool:
        return False

    @staticmethod
    def inference_mode():
        return torch.no_grad()

    @classmethod
    def is_pin_memory_available(cls):
        logger.warning("Pin memory is not supported on RBLN.")
        return False

    @classmethod
    def check_and_update_config(cls, vllm_config: VllmConfig) -> None:
        parallel_config = vllm_config.parallel_config
        if parallel_config.worker_cls == "auto":
            parallel_config.worker_cls = \
                "vllm.worker.rbln_worker.RBLNWorker"

        if parallel_config.world_size > 1:
            parallel_config.distributed_executor_backend = "uni"

        assert (vllm_config.lora_config
                is None), "LoRA is not supported for RBLN backend."
        assert (not vllm_config.speculative_config
                ), "Speculative decoding not yet supported for RBLN backend."

        cache_config = vllm_config.cache_config
        if cache_config and cache_config.block_size is None:
            vllm_config.cache_config.block_size = \
                vllm_config.model_config.max_model_len
