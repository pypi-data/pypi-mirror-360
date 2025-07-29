import torch

from .interface import Platform, PlatformEnum


class RblnPlatform(Platform):
    _enum = PlatformEnum.RBLN

    @staticmethod
    def inference_mode():
        return torch.no_grad()
