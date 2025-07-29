from typing import Optional

import torch

from vllm.logger import init_logger

from .interface import Platform, PlatformEnum

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
