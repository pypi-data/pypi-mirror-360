"""
Python firmware image builder main
"""

from pathlib import Path
from logging import getLogger
from .builder import build
from .status_codes import STATUS_SUCCESS
from .decoder import decode

def run_build(args):
    """Build an image

    :param args: Parsed command line arguments
    :type args: dict
    """
    logger = getLogger(__name__)
    if args.output:
        imagefilename = args.output
    else:
        imagefilename = Path(args.input).stem + '.img'

    logger.debug("Input hex file: '%s'", args.input)
    logger.debug("Config file: '%s'", args.config)
    logger.debug("Output img file: '%s'", imagefilename)
    if args.dump:
        logger.debug("Hex dump file: '%s'", args.dump)
    build(args.input, args.config, imagefilename, args.dump, args.include_empty_blocks)

    logger.info("Image building complete")

def run_decode(args):
    """Decode a firmware image

    :param args: Parsed command line arguments
    :type args: dict
    :raises: ImageDecodingError For decoding errors
    :raises: FileNotFoundError When image file cannot be found
    """
    logger = getLogger(__name__)
    logger.debug("Input image file: '%s'", args.input)
    logger.debug("Configuration image file: '%s'", args.config)
    
    fwimage = decode(args.input, args.config)

    if args.output:
        logger.debug("Decoded image file: '%s'", args.output)
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(str(fwimage))
    else:
        print(fwimage)

def pyfwimagebuilder(args):
    """
    Main program
    """
    logger = getLogger(__name__)
    logger.info("pyfwimagebuilder - Python firmware image builder for Microchip MDFU bootloaders")
    status = STATUS_SUCCESS
    if args.action == "build":
        run_build(args)
    elif args.action == "decode":
        run_decode(args)

    return status
