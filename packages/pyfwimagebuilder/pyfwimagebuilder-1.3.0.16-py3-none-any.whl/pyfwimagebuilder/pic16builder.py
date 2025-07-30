"""
Firmware Builder functions for PIC16
"""
from packaging.version import Version
from .mcu8builder import FirmwareImageBuilderMcu8, FlashWriteBlock, MetaDataBlock

class FirmwareImagebuilderPic16 (FirmwareImageBuilderMcu8):
    """
    Image Builder functions for PIC16
    """
    UNDEFINED_SEQUENCE = 0x3FFF
    UNDEFINED_SEQUENCE_BYTE_LENGTH = 2
    def __init__(self, config, firmware_image_cls):
        """
        Override Initialization
        """
        super().__init__(config, firmware_image_cls)
        # Convert the default values to support PIC16
        self.write_block_size = self.write_block_size * 2

    def empty_block(self, size):
        """
        Override:
        Return platform-specific empty byte pattern block with given size in bytes
        For PIC16, empty block is filled with 0x3fff *words*.
        Keyword arguments:
            size -- the byte size of the block
        """
        if size != self.write_block_size:
            raise ValueError(f"PIC16 devices can only write complete flash pages, requested a write size of {size} " +
                                f"but page size was specified as {self.write_block_size}")
        return int(size/2) * self.UNDEFINED_SEQUENCE.to_bytes(self.UNDEFINED_SEQUENCE_BYTE_LENGTH, 'little')

    def include_segment(self, start_address, end_address):
        """
        Override:
        Returns true if the segment must be included.
        
        :param start_address: First byte address of the segment.
        :type start_address: int
        :param end_address: Last byte address of the segment.
        :type end_address: int

        Note: PIC16 variant needs to multiple the configured address by
        2 in order to correct the byte vs. word differences.
        """
        parser_end = self.config['bootloader']['FLASH_END'] * 2
        parser_start = self.config['bootloader']['FLASH_START'] * 2
        if(
            # The target start address of the parse action must fall within the range of the segment
            (parser_start < end_address and parser_start >= start_address) and
            # The segment end address must be less than or equal to the target parse end address 
            # and the target parser end address must be greater than the start address of the parse action
            (end_address <= parser_end and parser_end > parser_start)):
            return True
        return False

    def _generate_flash_write_block(self, address, data):
        pic16_address = int(address / 2)
        block = FlashWriteBlock(pic16_address,
                      self.config["bootloader"]["PAGE_ERASE_KEY"],
                      self.config["bootloader"]["PAGE_WRITE_KEY"],
                      self.config["bootloader"]["BYTE_WRITE_KEY"],
                      self.config["bootloader"]["PAGE_READ_KEY"],
                      data)
        if data == self.empty_block(len(data)):
            block.empty = True
        else:
            block.empty = False
        return block

    def _generate_metadata_block(self):
        version = Version(self.config["bootloader"]["IMAGE_FORMAT_VERSION"])

        flash_write_size = self.config["bootloader"]["WRITE_BLOCK_SIZE"] * 2
        return MetaDataBlock(version,
                      self.config["bootloader"]["DEVICE_ID"],
                      flash_write_size,
                      self.config["bootloader"]["FLASH_START"],
                      self.config["bootloader"]["PAGE_ERASE_KEY"],
                      self.config["bootloader"]["PAGE_WRITE_KEY"],
                      self.config["bootloader"]["BYTE_WRITE_KEY"],
                      self.config["bootloader"]["PAGE_READ_KEY"]
                      )
