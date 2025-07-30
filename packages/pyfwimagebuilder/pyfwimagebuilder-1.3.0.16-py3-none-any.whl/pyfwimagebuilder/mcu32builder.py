"""
Common Firmware Builder functions for 32-bit bootloader image builders.
"""
from logging import getLogger
from packaging.version import Version
from .imagebuilder import FirmwareImageBuilder, BlockType, ImageBlockBase, FirmwareImage

MCU32_ARCH_LIST = ["M0+"]

logger = getLogger(__name__)

class Mcu32ImageBlockBase(ImageBlockBase):
    """
    Base class for firmware image blocks.
    """
    @classmethod
    def from_bytes(cls, data: bytes|bytearray):
        """
        Create an image block from the given byte data.

        :param data: The byte data to decode.
        :type data: bytes|bytearray
        :return: An instance of the appropriate image block subclass.
        :rtype: MetaDataBlock | FlashWriteBlock
        """
        _, block_type = cls.decode_block_header(data)
        block = None
        if block_type == BlockType.METADATA:
            block = MetaDataBlock.from_bytes(data)
        elif block_type == BlockType.FLASH_OPERATION:
            block = FlashWriteBlock.from_bytes(data)

        return block

# pylint: disable=too-many-instance-attributes
class FlashWriteBlock(Mcu32ImageBlockBase):
    """
    Class representing a flash write operation block.

    :param address: The start address for the flash write operation.
    :type address: int
    :param data: The data to be written to flash. Must be padded to
    flash block write size.
    :type data: bytes
    """
    ADDRESS_LENGTH = 4
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, address, data):
        self.block_size = self.BLOCK_SIZE_LENGTH + self.BLOCK_TYPE_LENGTH +\
            self.ADDRESS_LENGTH + len(data)
        self.address = address
        self.data = data
        self._empty = False

    def __str__(self):
        """
        Return a string representation of the flash write block.

        :return: A string representation of the flash write block.
        :rtype: str
        """
        block_size_bit_size = self.BLOCK_SIZE_LENGTH * 8
        address_bit_size = self.ADDRESS_LENGTH * 8
        txt = f"""\
Block size: {self._pad_to_hex(self.block_size, block_size_bit_size)} ({self.block_size})
Block type: {BlockType.FLASH_OPERATION.name} (0x{BlockType.FLASH_OPERATION.value:X})
Start address: {self._pad_to_hex(self.address , address_bit_size)}
Data bytes: 0x{len(self.data):X} ({len(self.data)})
"""
        data_txt = "Address   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n"
        full_blocks = len(self.data) // 16

        for i in range(full_blocks):
            address = self.address + i * 16
            data_txt += f"{address:08X} "
            tmp = self.data[16*i:16*(i+1)]
            for byte in tmp:
                data_txt += f" {byte:02X}"
            data_txt += "\n"

        # Handle remaining bytes
        remaining_bytes = len(self.data) % 16
        if remaining_bytes > 0:
            address = self.address + full_blocks * 16
            data_txt += f"{address:08X}  "
            tmp = self.data[full_blocks * 16:]
            for byte in tmp:
                data_txt += f" {byte:02X}"
            data_txt += "\n"
        return txt + data_txt

    @classmethod
    def from_bytes(cls, data: bytes|bytearray):
        """
        Create a flash write block from the given byte data.

        :param data: The byte data to decode.
        :type data: bytes|bytearray
        :return: An instance of FlashWriteBlock.
        :rtype: FlashWriteBlock
        :raises ValueError: If the block type is not FLASH_OPERATION.
        """
        _, block_type = cls.decode_block_header(data)
        if block_type != BlockType.FLASH_OPERATION:
            raise ValueError(f"Expected {BlockType.FLASH_OPERATION.name} (0x{BlockType.FLASH_OPERATION.value:02X}) "+ \
                            f"block type but got 0x{block_type.value:02X}")
        data = data[3:]
        address = int.from_bytes(data[:cls.ADDRESS_LENGTH], byteorder="little")
        # Add all components of the flash header here. For 32-bit image format, we only use the address for writing
        flash_header_size = cls.ADDRESS_LENGTH
        flash_data = data[flash_header_size:]
        flash_block = cls(address, flash_data)
        return flash_block

    def to_bytes(self):
        """
        Convert the flash write operation block to bytes.

        :return: The byte representation of the flash write block.
        :rtype: bytes
        """
        block = self.block_size.to_bytes(self.BLOCK_SIZE_LENGTH, byteorder="little") + \
            bytes([BlockType.FLASH_OPERATION.value]) + \
            self.address.to_bytes(self.ADDRESS_LENGTH, byteorder="little") + \
            self.data
        return block

# pylint: disable=too-many-instance-attributes
class MetaDataBlock(Mcu32ImageBlockBase):
    """
    Class representing a metadata block.

    :param block_size: The size of the block.
    :type block_size: int
    :param version: The version of the metadata.
    :type version: Version
    :param device_id: The device ID.
    :type device_id: int
    :param write_block_size: The flash write size per block.
    :type write_block_size: int
    :param address: The start address for the write operation.
    :type address: int
    """
    METADATA_LENGTH = 13
    ADDRESS_LENGTH = 4
    FLASH_WRITE_LENGTH = 2
    DEVICE_ID_LENGTH = 4
    FLASH_WRITE_HEADER_LENGTH = 7
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, version: Version, device_id, write_block_size, address):
        self.block_type = BlockType.METADATA
        self.block_size = self.FLASH_WRITE_HEADER_LENGTH + write_block_size
        self.version = version
        self.device_id = device_id
        self.write_block_size = write_block_size
        self.address = address
        self.padding = None

    @classmethod
    def from_bytes(cls, data: bytes|bytearray):
        """
        Create a metadata block from the given byte data.

        :param data: The byte data to decode.
        :type data: bytes|bytearray
        :return: An instance of MetaDataBlock.
        :rtype: MetaDataBlock
        :raises ValueError: If there is not enough data to decode the metadata.
        """
        block_size, block_type = cls.decode_block_header(data)
        if block_size != len(data):
            raise ValueError(f"Block size ({block_size})does not match actual block length ({len(data)})")
        if block_type != BlockType.METADATA:
            raise ValueError("Block type is not a metadata block")
        data = data[3:]
        if len(data) < cls.METADATA_LENGTH:
            raise ValueError("Not enough data to decode metadata. " +
                             f"Need {cls.METADATA_LENGTH} bytes but got {len(data)}")
        version = Version(f"{data[2]}.{data[1]}.{data[0]}")
        device_id = int.from_bytes(data[3:7], "little")
        write_block_size = int.from_bytes(data[7:9], "little")
        address = int.from_bytes(data[9:13], "little")
        padding = data[13:]

        meta_block = cls(version, device_id, write_block_size, address)
        meta_block.padding = padding
        return meta_block

    def to_bytes(self):
        """
        Convert the metadata block to bytes.

        :return: The byte representation of the metadata block.
        :rtype: bytes
        """

        padding = self.block_size - self.BLOCK_HEADER_SIZE - self.METADATA_LENGTH
        block = self.block_size.to_bytes(self.BLOCK_SIZE_LENGTH, byteorder="little") + \
            bytes([BlockType.METADATA.value]) + \
            bytes([self.version.micro, self.version.minor, self.version.major]) + \
            self.device_id.to_bytes(self.DEVICE_ID_LENGTH, byteorder="little") + \
            self.write_block_size.to_bytes(self.FLASH_WRITE_LENGTH, byteorder="little") + \
            self.address.to_bytes(self.ADDRESS_LENGTH, "little") + \
            bytes(padding)
        return block

    def __str__(self):
        """
        Return a string representation of the metadata block.

        :return: A string representation of the metadata block.
        :rtype: str
        """
        block_size_bit_size = self.BLOCK_SIZE_LENGTH * 8
        device_id_bit_size = self.DEVICE_ID_LENGTH * 8
        address_bit_size = self.ADDRESS_LENGTH * 8
        flash_write_size_bit_size = self.FLASH_WRITE_LENGTH * 8
        txt = f"""\
Block size: {self._pad_to_hex(self.block_size, block_size_bit_size)} ({self.block_size})
Block type: {self.block_type.name} (0x{self.block_type.value:X})
Version: {self.version}
Device ID: {self._pad_to_hex(self.device_id, device_id_bit_size)}
Write block size: {self._pad_to_hex(self.write_block_size, flash_write_size_bit_size)}
Start address: {self._pad_to_hex(self.address, address_bit_size)}"""
        pad_txt = ""
        if self.padding is not None and self._verify_padding(self.padding):
            pad_txt = f"\nBlock padded with {len(self.padding)} zeros"
        return txt + pad_txt

class Mcu32FirmwareImage(FirmwareImage):
    """Firmware image object
    """
    def __init__(self, block_base_cls=Mcu32ImageBlockBase):
        super().__init__(block_base_cls)

class FirmwareImageBuilderMcu32 (FirmwareImageBuilder):
    """Image builder
    """
    UNDEFINED_SEQUENCE = 0xFF
    UNDEFINED_SEQUENCE_BYTE_LENGTH = 1
    MAX_FORMAT_VERSION = "1.0.0"
    MIN_FORMAT_VERSION = "1.0.0"

    def include_segment(self, start_address, end_address):
        """
        Returns true if the segment must be included.

        :param start_address: First byte address of the segment.
        :type start_address: int
        :param end_address: Last byte address of the segment.
        :type end_address: int
        """
        parser_start = self.config['bootloader']['FLASH_START']
        parser_end = self.config['bootloader']['FLASH_END']
        if(
            # The target start address of the parse action must fall within the range of the segment
            (parser_start < end_address and parser_start >= start_address) and
            # The segment end address must be less than or equal to the target parse end address 
            # and the target parser end address must be greater than the start address of the parse action
            (end_address <= parser_end and parser_end > parser_start)):
            return True
        return False

    def _generate_flash_write_block(self, address, data):
        block = FlashWriteBlock(address, data)
        if data == self.empty_block(len(data)):
            block.empty = True
        else:
            block.empty = False
        return block

    def _generate_metadata_block(self):
        version = Version(self.config["bootloader"]["IMAGE_FORMAT_VERSION"])
        return MetaDataBlock(version,
                      self.config["bootloader"]["DEVICE_ID"],
                      self.config["bootloader"]["WRITE_BLOCK_SIZE"],
                      self.config["bootloader"]["FLASH_START"]
                      )
