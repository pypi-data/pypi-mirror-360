"""
Firmware Builder functions for AVR
"""
from .mcu8builder import FirmwareImageBuilderMcu8

AVR_ARCH_LIST = ["AVR", "AVR_DA", "TINY"]

class FirmwareImagebuilderAVR (FirmwareImageBuilderMcu8):
    """
    Image Builder functions for AVR
    """
    # No special implementation needed *yet* for AVR
