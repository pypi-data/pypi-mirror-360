"""Image builders common functionality"""

from abc import ABC, abstractmethod
from enum import Enum
from logging import getLogger
import textwrap
from packaging.version import parse as version_parse

logger = getLogger(__name__)

class ImageDecodingError(Exception):
    """Generic image decoding error exception"""

class BlockType(Enum):
    """
    Default Block Types

    The default firmware image format contains block types that help to define the data inside of the blocks and how the bootloader should
    interact with that data block. These interactions could include validating metadata inside of the block or writing the data in the 
    block to a specified region of the device's memory. This class (enumeration) will define the group of suggested block types for each image format.

    - 0: Nothing has been set. Ideally, bootloaders should never use a block type of zero.
    - 1: Metadata block, used as a simple data block that can store implementation specific data. For the default format, this is used to store some
        data elements that have been passed by the configuration file.
    - 2: Flash data operation block, used to transfer bytes that appear in the flash data region of the hex file. For the default file format this
        range is defined in the configuration file from FLASH_START and FLASH_END.
    - 3: EEPROM data operation block, used to transfer bytes that appear in the eeprom data region of the hex file. For the default file format this
        range is defined in the configuration file from EEPROM_START and EEPROM_END. *Not supported yet*
    """
    UNINITIALIZED = 0
    METADATA = 1
    FLASH_OPERATION = 2

class FirmwareImage(ABC):
    """Firmware image object
    
    The default firmware image class that defined the most basic use case for all currently supported image formats. The default image
    format includes 1 metadata block at the start of the image followed by any number of other blocks.
    
    Attributes:
        block_size : int
            The size of each of the blocks that are held inside of the file block array
        blocks : List[ImageBlockBase]
            The List of ImageBlockBase or Children of the ImageBlockBase class that make up a complete firmware image
        
    """
    def __init__(self, image_block_base_cls):
        self.block_size = 0
        self.blocks = []
        """
        Internal variable for managing the functions that use various implementations of the basic FirmwareImage class.
            This allows us to call the same function for all classes that use the default image block layout
        """
        self.image_block_base = image_block_base_cls

    def __str__(self):
        """String representation of a firmware image
        
        This implementation relies on the fact that any image block class defined will implement it's own __str__ function.
        """
        txt = ""
        for i, block in enumerate(self.blocks):
            txt += f"Block - {i}\n"
            block_text = textwrap.indent(str(block), '  ')
            txt += block_text
            txt += "\n"
        return txt

    def add_block(self, block):
        """Add a block to the image

        :param block: Image block
        :type block: Inherited classes from ImageBlockBase
        """
        self.blocks.append(block)

    def to_bytes(self):
        """Create image

        :return: Image as bytes like object
        :rtype: bytearray
        """
        image = bytearray()
        for block in self.blocks:
            image.extend(block.to_bytes())
        return image

    @classmethod
    def from_bytes(cls, image_block_base, data):
        """Create a firmware image object from a bytes object

        :param image_block_base: Firmware image bytes
        :type image_block_base: ImageBlockBase or child of ImageBlockBase
        :param data: Firmware image bytes
        :type data: bytes | bytearray
        :return: Object representing the firmware image
        :rtype: Child class of FirmwareImage
        :raises ImageDecodingError: For image decoding errors.
        """
        fwimage = cls(image_block_base)
        fwimage.decode(data)
        return fwimage

    def decode(self, data: bytes | bytearray):
        """Decode image from bytes object.

        :param data: Image object
        :type data: bytes | bytearray
        :raises ImageDecodingError: For image decoding errors.
        """
        logger.debug("Attempting to decode firmware image")
        self.blocks = []
        try:
            # Decode only block size and type of the first block
            self.block_size, block_type = self.image_block_base.decode_block_header(data, verify_length=False)
            # Verify that first block is a metadata block
            if BlockType.METADATA != block_type:
                txt = f"Invalid block type detected. Expected {BlockType.METADATA.name} " + \
                    f"(0x{BlockType.METADATA.value:02X}) but got 0x{block_type.value:02X}"
                logger.error(txt)
                raise ValueError(txt)

            blocks_count = len(data) // self.block_size
            logger.debug("Block size %i", self.block_size)
            logger.debug("Number of blocks in image %i", blocks_count)
            # Ensure that the image can be divided into a whole number of blocks with a lenght of block_size
            if len(data) % self.block_size:
                raise ValueError(f"Data can not be split into an even number of bocks with size of {self.block_size}")
            for i in range(blocks_count):
                block_start = 0 + i * self.block_size
                block_end = block_start + self.block_size
                logger.debug("Decoding block %i", i)
                block = self.image_block_base.from_bytes(data[block_start:block_end])
                self.blocks.append(block)
        except (ValueError, TypeError) as err:
            raise ImageDecodingError(f"Image decoding failed. {err}") from err

class ImageBlockBase(ABC):
    """
    Base class for firmware image blocks.
    
    The default image block class that defines the default block format for the supported builders. The default block
    includes 2 bytes and the start of the block that defines the entire length of the block and byte immediately following
    that defines the type of data held in the block using one of the BlockType values.
    
    """
    BLOCK_TYPE_LENGTH = 1
    BLOCK_SIZE_LENGTH = 2
    BLOCK_HEADER_SIZE = BLOCK_SIZE_LENGTH + BLOCK_TYPE_LENGTH
    
    @staticmethod
    def decode_block_header(data, verify_length=True):
        """
        Decode the default block header from the given data.

        :param data: The data containing the block header.
        :type data: bytes
        :param verify_length: Check that the data length matches the decoded block length
        :type verify_length: bool
        :return: A tuple containing the block size and block type.
        :rtype: tuple(int, BlockType)
        :raises ValueError: If the decoded block size does not match the actual block size.
        :raises TypeError: If the block type is invalid.
        """
        block_size = int.from_bytes(data[0:2], "little")
        if verify_length and block_size != len(data):
            raise ValueError(f"Decoded block size {block_size} does not match actual block size {len(data)}")
        try:
            block_type = BlockType(data[2])
        except ValueError as exc:
            raise ValueError(f"Invalid block type {data[2]:0x} detected") from exc
        return block_size, block_type

    def _pad_to_hex(self, value, bit_count):
        """
        Pads an integer value into a hexadecimal string with a specified bit count.

        :param value: The integer value to convert.
        :type value: int
        :param bit_count: The total number of bits for the hexadecimal representation.
        :type bit_count: int
        :return: The padded hexadecimal string.
        :rtype: str
        """
        # Calculate the number of hex digits needed
        hex_digits = bit_count // 4  # Each hex digit represents 4 bits

        # Format the value as a zero-padded hexadecimal string
        hex_string = f"0x{value:0{hex_digits}X}"

        return hex_string

    @abstractmethod
    def from_bytes(cls, data: bytes|bytearray):
        """
        Create an image block from the given byte data.

        Abstract function that must be defined by the specific firmware builder implementation

        :param data: The byte data to decode.
        :type data: bytes|bytearray
        :return: An instance of the appropriate image block subclass.
        :rtype: MetaDataBlock | FlashWriteBlock
        """
        
    @abstractmethod
    def to_bytes(cls, data: bytes|bytearray):
        """
        Convert the flash write operation block to bytes.

        :param data: The byte data to decode.
        :type data: bytes|bytearray
        :return: The byte representation of the flash write block.
        :rtype: bytes
        """
        
    @abstractmethod
    def __str__(self):
        """
        Return a string representation of the defined block.

        :return: A string representation of the defined block.
        :rtype: str
        """

    def _verify_padding(self, data):
        """
        Verify that the padding bytes in the block are all zeros.

        :param data: The padding data to verify.
        :type data: bytes
        :return: True if the padding is valid, False otherwise.
        :rtype: bool
        """
        for byte in data:
            if byte != 0x00:
                return False
        return True

    @property
    def empty(self):
        """Block data status

        :return: True if block contains empty data, otherwise False
        :rtype: Bool
        """
        return self._empty

    @empty.setter
    def empty(self, value):
        self._empty = value

class FirmwareImageBuilder(ABC):
    """
    Abstract class - that defines the builder API and common code between all image builders.
    """
    MAX_FORMAT_VERSION = "0.0.0"
    MIN_FORMAT_VERSION = "0.0.0"
    UNDEFINED_SEQUENCE = 0xFF
    UNDEFINED_SEQUENCE_BYTE_LENGTH = 1

    def __init__(self, config, firmware_image_cls):
        self.config = config
        self.write_block_size = self.config['bootloader']['WRITE_BLOCK_SIZE']
        self.firmware_image = firmware_image_cls

    @abstractmethod
    def include_segment(self, start_address, end_address):
        """
        Test if the memory address is within a valid memory range for the
        builder. Returns true if the address is within a valid memory region
        otherwise False.

        :param start_address: First byte address of the segment.
        :type start_address: int
        :param end_address: Last byte address of the segment.
        :type end_address: int
        """

    @classmethod
    def is_valid_version(cls, version):
        """
        Return true when the requested version is equal to or between the min and max version values of the class.

        This function can be overridden by the inheriting class if special version checks are required that do not meet this definition.

        :param: version: semver string.
        """
        requested_version =  version_parse(version)
        max_version = version_parse(cls.MAX_FORMAT_VERSION)
        min_version = version_parse(cls.MIN_FORMAT_VERSION)
        result = bool(min_version <= requested_version <= max_version)
        return result

    def versiontobytes(self, version):
        """
        Convert a major.minor.micro version string to little-endian bytes representation
        
        This function can be overridden by the inheriting class if special version checks are required that do not meet this definition.
        :param version: Semver string that defines the file format.
        :type version: string
        """
        format_version = version_parse(version)
        return ((int(format_version.major) << 16) +
                (int(format_version.minor) << 8) +
                (int(format_version.micro))).to_bytes(3, 'little')

    def empty_block(self, size):
        """
        Return platform-specific empty byte pattern block with given size in bytes.

        param: size: size of the block in bytes.
        type: size: int
        """
        return size * self.UNDEFINED_SEQUENCE.to_bytes(self.UNDEFINED_SEQUENCE_BYTE_LENGTH, 'little')

    @abstractmethod
    def _generate_metadata_block(self):
        """Stub function that defines the default meta data block format used by the default file definition.

        *This function must be overridden by the specific implementation*
        
        :return: MetaDataBlock is the default class defined but could be any child of the ImageBlockBase class. None, if the metadata is not needed
        :rtype: Child of the ImageBlockBase | None
        """

    @abstractmethod
    def _generate_flash_write_block(self, address, data):
        """Stub function that defines the default flash block format.

        *This function must be overridden by the specific implementation*

        param: address Start address of the data block
        type: address int
        param: data block data that must be placed inside the flash block format
        type: data bytearray | bytes
        :return: FlashWriteBlock is the default class defined but could be any child of the ImageBlockBase class.
        :rtype: Child of the ImageBlockBase
        """

    def build(self, hexfile, include_empty_blocks=False):
        """Build firmware image

        :param builder: Firmware image builder
        :type builder: Implementation of FirmwareImageBuilder
        :param hexfile: Source hexfile
        :type hexfile: IntelHex
        :param include_empty_blocks: Include empty memory blocks in image, defaults to False
        :type include_empty_blocks: bool, optional
        :return: Firmware image
        :rtype: FirmwareImage
        """
        # Generate a new firmware image based on what has been defined by the inheriting class
        image = self.firmware_image()
        # Generate the first block and add it if the block exists
        metadata_block = self._generate_metadata_block()
        # If None then skip the block write because the inheriting class does not use it
        if metadata_block != None:
            image.add_block(metadata_block)

        # Parse the hexfile
        segments = hexfile.segments()
        for segment in segments:
            segment_start, segment_stop = segment
            logger.debug("Segment from 0x%08X to 0x%08X", segment_start, segment_stop)

            # Check if this segment is relevant
            if not self.include_segment(segment_start, segment_stop):
                txt = f"Skipping segment from 0x{segment_start:08X} to 0x{segment_stop:08X} "+\
                    "that is outside defined segments for this architecture"
                logger.warning(txt)
                continue

            # Extract data for this segment
            segment_data = bytes(hexfile.tobinarray(start=segment_start, end=segment_stop-1))
            logger.debug("Adding segment of length: %d", len(segment_data))

            address = segment_start
            # Loop through the segment creating blocks
            while segment_data:
                # Set the block address
                logger.debug("Address: 0x%X", address)
                if len(segment_data) >= self.write_block_size:
                    block_data = segment_data[:self.write_block_size]
                    segment_data = segment_data[self.write_block_size:]
                else:
                    block_data = segment_data
                    segment_data = []
                block = self._generate_flash_write_block(address, block_data)

                # Add block to image, adjust remaining data and counters
                if include_empty_blocks or not block.empty:
                    image.add_block(block)
                else:
                    logger.debug("Skipping empty block at address 0x%08x", address)

                logger.debug("Data remaining: %d", len(segment_data))
                address += len(block_data)
        return image
