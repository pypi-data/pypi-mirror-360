"""
pyfwimagebuilder CLI: "fwimagebuilder"
"""
import sys
import logging
import argparse
import os
import textwrap
from pathlib import Path

from logging import getLogger
from logging.config import dictConfig
from appdirs import user_log_dir
import yaml
from yaml.scanner import ScannerError

from . import pyfwimagebuilder_main
from .status_codes import STATUS_SUCCESS

try:
    from . import __version__ as VERSION
    from . import BUILD_DATE, COMMIT_ID
except ImportError:
    VERSION = "0.0.0"
    COMMIT_ID = "N/A"
    BUILD_DATE = "N/A"

def setup_logging(user_requested_level=logging.WARNING, default_path='logging.yaml',
                  env_key='MICROCHIP_PYTHONTOOLS_CONFIG'):
    """
    Setup logging configuration for pyfwimagebuilder CLI
    """
    # Logging config YAML file can be specified via environment variable
    value = os.getenv(env_key, None)
    if value:
        path = value
    else:
        # Otherwise use the one shipped with this application
        path = os.path.join(os.path.dirname(__file__), default_path)
    # Load the YAML if possible
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding="utf-8") as file:
                # Load logging configfile from yaml
                configfile = yaml.safe_load(file)
                # File logging goes to user log directory under Microchip/modulename
                logdir = user_log_dir(__name__, "Microchip")
                # Look through all handlers, and prepend log directory to redirect all file loggers
                num_file_handlers = 0
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        configfile['handlers'][handler]['filename'] = os.path.join(
                            logdir, configfile['handlers'][handler]['filename'])
                        num_file_handlers += 1
                # If file logging is enabled, it needs a folder
                if num_file_handlers > 0:
                    # Create it if it does not exist
                    Path(logdir).mkdir(exist_ok=True, parents=True)
                # Console logging takes granularity argument from CLI user
                configfile['handlers']['console']['level'] = user_requested_level
                # Root logger must be the most verbose of the ALL YAML configurations and the CLI user argument
                most_verbose_logging = min(user_requested_level, getattr(logging, configfile['root']['level']))
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        level = getattr(logging, configfile['handlers'][handler]['level'])
                        most_verbose_logging = min(most_verbose_logging, level)
                configfile['root']['level'] = most_verbose_logging
            dictConfig(configfile)
            return
        except ScannerError:
            # Error while parsing YAML
            print(f"Error parsing logging config file '{path}'")
        except KeyError as keyerror:
            # Error looking for custom fields in YAML
            print(f"Key {keyerror} not found in logging config file")
    else:
        # Config specified by environment variable not found
        print(f"Unable to open logging config file '{path}'")

    # If all else fails, revert to basic logging at specified level for this application
    print("Reverting to basic logging.")
    logging.basicConfig(level=user_requested_level)

def main():
    """
    Entrypoint for installable CLI

    Configures the CLI and parses the arguments
    """
    # Shared switches.  These are inherited by subcommands (and root) using parents=[]
    common_argument_parser = argparse.ArgumentParser(add_help=False)
    common_argument_parser.add_argument("-v", "--verbose",
                                        default="info",
                                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                                        help="Logging verbosity/severity level")
    # Action-less switches.  These are all "do X and exit"
    common_argument_parser.add_argument("-V", "--version", action="store_true",
                        help="Print pyfwimagebuilder version number and exit")
    common_argument_parser.add_argument("-R", "--release-info", action="store_true",
                        help="Print pyfwimagebuilder release details and exit")

    # Parse out what is seen this far for later use
    common_args, _ = common_argument_parser.parse_known_args()

    parser = argparse.ArgumentParser(
        parents=[common_argument_parser],
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''\
    pyfwimagebuilder: a command line interface for building images compatible with Microchip mfdu bootloaders

    basic usage:
        - pyfwimagebuilder build -i <input hex file> -c <input config file> -o <output image file>
        - pyfwimagebuilder decode -i <input image file> -c <input configuration file> -o <output decoded text file>

    available actions:
        - build: builds an image
        - decode: decodes an image
            '''),
        epilog=textwrap.dedent('''usage examples:

        - pyfwimagebuilder build -i app.hex -c bootconf.toml -o app.image
        - pyfwimagebuilder decode -i app.image -c bootconf.toml -o app.txt
    '''))

    subparsers = parser.add_subparsers(
        title='actions',
        dest='action',
        required = not (common_args.version or common_args.release_info),
        description="use one and only one of these actions",
        help="for additional help use pwfwimagebuilder <action> --help")

    # Action subparsers
    build_parser = subparsers.add_parser(
        name='build',
        formatter_class=argparse.RawTextHelpFormatter,
        help='Build firmware image',
        parents=[common_argument_parser])

    # Image-building switches
    build_parser.add_argument(
        "-i", "--input", required=True, metavar="application.hex",
        help="Input application file to process, in Intel-hex format")

    build_parser.add_argument(
        "-o", "--output", metavar="image.img",
        help="Output image file to generate")

    build_parser.add_argument(
        "-c", "--config", required=True, metavar="config.toml",
        help="Bootloader configuration file to use")

    build_parser.add_argument(
        "-e", "--include-empty-blocks",
        action = "store_true",
        help="Include empty blocks in image file. WARNING: may cause large file")

    build_parser.add_argument(
        "-D", "--dump", metavar="dump.txt",
        help="Dump additional human readable output to file")

    decode_parser = subparsers.add_parser(
        name='decode',
        formatter_class=argparse.RawTextHelpFormatter,
        help='Decode firmware image',
        parents=[common_argument_parser])

    decode_parser.add_argument(
        "-i", "--input", required=True, metavar="application.img",
        help="Input application image file to decode")

    decode_parser.add_argument(
        "-o", "--output", metavar="application.img.txt",
        help="Write decoded image to file instead of stdout.")
    
    decode_parser.add_argument(
        "-c", "--config", required=True, metavar="config.toml",
        help="Bootloader configuration file to use")

    # Handle action-less switches
    if common_args.version or common_args.release_info:
        print(f"pyfwimagebuilder version {VERSION}")
        if common_args.release_info:
            print(f"Build date:  {BUILD_DATE}")
            print(f"Commit ID:   {COMMIT_ID}")
            print(f"Installed in {os.path.abspath(os.path.dirname(__file__))}")
        return STATUS_SUCCESS

    # Setup logging
    setup_logging(user_requested_level=getattr(logging, common_args.verbose.upper()))
    logger = getLogger(__name__)
    # Main parse
    args = parser.parse_args()

    try:
        # Call the command handler with args
        return pyfwimagebuilder_main.pyfwimagebuilder(args)
    except Exception as exc: # pylint: disable=broad-exception-caught
        logger.error("Operation failed with %s: %s", type(exc).__name__, exc)
        logger.debug(exc, exc_info=True)    # get traceback if debug loglevel
        return 1

if __name__ == "__main__":
    sys.exit(main())
