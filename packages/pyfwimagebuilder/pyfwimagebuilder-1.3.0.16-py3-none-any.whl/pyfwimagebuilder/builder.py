"""
Main Builder Algorithm
"""
from logging import getLogger
import toml
from intelhex import IntelHex

from .mcu8builder import Mcu8FirmwareImage
from .pic18builder import FirmwareImagebuilderPic18
from .pic16builder import FirmwareImagebuilderPic16
from .avrbuilder import FirmwareImagebuilderAVR, AVR_ARCH_LIST
from .mcu32builder import FirmwareImageBuilderMcu32, Mcu32FirmwareImage, MCU32_ARCH_LIST

def firmware_image_factory(architecture: str):
    """Retrieve the required firmware image class

    :param architecture: Architecture type e.g. PIC18, PIC16, AVR, AVR_DA, TINY, M0+...
    :type architecture: string

    :raises NotImplementedError: For not supported architecture or format version
    :return: FirmwareImage instance
    :rtype: Instance of FirmwareImage subclass
    """
    fwimage = None
    if architecture in ["PIC18", "PIC16"] or architecture in AVR_ARCH_LIST:
        fwimage = Mcu8FirmwareImage
    elif architecture in MCU32_ARCH_LIST:
        fwimage = Mcu32FirmwareImage
    else:
        raise NotImplementedError (f"Unsupported architecture '{architecture}'")
    return fwimage

def builder_factory(architecture: str, config):
    """Creates a builder for a specific architecture

    :param architecture: Architecture type e.g. PIC18, PIC16, AVR, AVR_DA, TINY, M0+...
    :type architecture: string
    :param config: Image file configuration
    :type config: dict
    :raises NotImplementedError: For not supported architecture or format version
    :return: Image builder instance
    :rtype: Instance of ImageBuilder subclass
    """
    version = config['bootloader']['IMAGE_FORMAT_VERSION']
    if architecture == "PIC18":
        builder = FirmwareImagebuilderPic18
    elif architecture == "PIC16":
        builder = FirmwareImagebuilderPic16
    elif architecture in AVR_ARCH_LIST:
        builder = FirmwareImagebuilderAVR
    elif architecture in MCU32_ARCH_LIST:
        builder = FirmwareImageBuilderMcu32
    else:
        raise NotImplementedError (f"Unsupported architecture '{architecture}'")
    if not builder.is_valid_version(version):
        raise NotImplementedError(f"Requested format version {version} not supported, " +\
            f"builder supports versions {builder.MIN_FORMAT_VERSION} - " +\
            f"{builder.MAX_FORMAT_VERSION}")
    firmware_image_cls = firmware_image_factory(architecture)
    return builder(config, firmware_image_cls)

def build(input_filename, config_filename, output_filename, hexdump_filename=None, include_empty_blocks=False):
    """Builds and saves a firmware image

    :param input_filename: Path to hexfile to build the image from
    :type input_filename: str
    :param config_filename: Path to configuration TOML file
    :type config_filename: str
    :param output_filename: Image file name
    :type output_filename: str
    :param hexdump_filename: Filename for a hexdump of the image, defaults to None
    :type hexdump_filename: str, optional
    :param include_empty_blocks: Defines if empty blocks should be included, defaults to False
    :type include_empty_blocks: bool, optional
    """
    logger = getLogger(__name__)
    # Read in hex file for conversion
    hexfile = IntelHex()
    hexfile.fromfile(input_filename, format='hex')

    # Read in config which was generated when this bootloader was built
    logger.debug("Loading bootloader config from %s", config_filename)
    bootloader_config = toml.load(config_filename)

    # Find out which architecture is used
    architecture = bootloader_config['bootloader']['ARCH']
    builder = builder_factory(architecture, bootloader_config)
    image = builder.build(hexfile, include_empty_blocks=include_empty_blocks)

    # Save to target image file
    if output_filename:
        with open(output_filename, "wb") as outfile:
            outfile.write(image.to_bytes())
        logger.info("Image written to '%s'", output_filename)

    # Return human readable form for display
    if hexdump_filename:
        with open(hexdump_filename, "w", encoding="utf-8") as dumpfile:
            dumpfile.write(str(image))
        logger.info("Ascii version of image written to '%s'", hexdump_filename)
