"""
Main Decoder Algorithm
"""
from logging import getLogger
import toml

from .mcu8builder import Mcu8FirmwareImage, Mcu8ImageBlockBase
from .pic18builder import FirmwareImagebuilderPic18
from .pic16builder import FirmwareImagebuilderPic16
from .avrbuilder import FirmwareImagebuilderAVR, AVR_ARCH_LIST
from .mcu32builder import Mcu32ImageBlockBase, FirmwareImageBuilderMcu32, Mcu32FirmwareImage, MCU32_ARCH_LIST

def image_block_factory(architecture: str, config):
    """Creates a image block class for a specific architecture

    :param architecture: Architecture type e.g. PIC18, PIC16, AVR, AVR_DA, TINY...
    :type architecture: string
    :param config: Image file configuration
    :type config: dict
    :raises NotImplementedError: For not supported architecture or format version
    :return: FirmwareImage instance
    :rtype: Instance of a FirmwareImage class
    """
    version = config['bootloader']['IMAGE_FORMAT_VERSION']
    if architecture == "PIC18":
        builder = FirmwareImagebuilderPic18
        image_block = Mcu8ImageBlockBase
    elif architecture == "PIC16":
        builder = FirmwareImagebuilderPic16
        image_block = Mcu8ImageBlockBase
    elif architecture in AVR_ARCH_LIST:
        builder = FirmwareImagebuilderAVR
        image_block = Mcu8ImageBlockBase
    elif architecture in MCU32_ARCH_LIST:
        builder = FirmwareImageBuilderMcu32
        image_block = Mcu32ImageBlockBase
    else:
        raise NotImplementedError (f"Unsupported architecture '{architecture}' for decoder")
    if not builder.is_valid_version(version):
        raise NotImplementedError(f"Requested format version {version} not supported, " +\
            f"decoder supports versions {builder.MIN_FORMAT_VERSION} - " +\
            f"{builder.MAX_FORMAT_VERSION}")
    return image_block

def fwimage_factory(architecture: str, config):
    """Creates a firmware image class for a specific architecture

    :param architecture: Architecture type e.g. PIC18, PIC16, AVR, AVR_DA, TINY...
    :type architecture: string
    :param config: Image file configuration
    :type config: dict
    :raises NotImplementedError: For not supported architecture or format version
    :return: FirmwareImage instance
    :rtype: Instance of a FirmwareImage class
    """
    version = config['bootloader']['IMAGE_FORMAT_VERSION']
    if architecture == "PIC18":
        builder = FirmwareImagebuilderPic18
        fwimage = Mcu8FirmwareImage
    elif architecture == "PIC16":
        builder = FirmwareImagebuilderPic16
        fwimage = Mcu8FirmwareImage
    elif architecture in AVR_ARCH_LIST:
        builder = FirmwareImagebuilderAVR
        fwimage = Mcu8FirmwareImage
    elif architecture in MCU32_ARCH_LIST:
        builder = FirmwareImageBuilderMcu32
        fwimage = Mcu32FirmwareImage
    else:
        raise NotImplementedError (f"Unsupported architecture '{architecture}' for decoder")
    if not builder.is_valid_version(version):
        raise NotImplementedError(f"Requested format version {version} not supported, " +\
            f"decoder supports versions {builder.MIN_FORMAT_VERSION} - " +\
            f"{builder.MAX_FORMAT_VERSION}")
    return fwimage

def decode(input_filename, config_filename):
    """Decode and return a firmware image as a string

    :param input_filename: Path to hexfile to build the image from
    :type input_filename: str
    :param config_filename: Path to configuration TOML file
    :type config_filename: str
    """
    logger = getLogger(__name__)

    # Read in config which was generated when this bootloader was built
    logger.debug("Loading bootloader config from %s", config_filename)
    bootloader_config = toml.load(config_filename)

    # Find out which architecture is used
    architecture = bootloader_config['bootloader']['ARCH']

    # Get the arch specific image classes
    firmware_image = fwimage_factory(architecture, bootloader_config)
    image_block = image_block_factory(architecture, bootloader_config)

    # Read and decode the image data
    with open(input_filename, "rb") as image_file:
        data = image_file.read()
        fwimage = firmware_image.from_bytes(image_block, data)
    return fwimage
