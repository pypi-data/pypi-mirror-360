import sys

from scenery import logger, config
from scenery.common import Framework
from scenery.cli import parse_args, command
import scenery.commands

def main() -> bool:

    # out: dict[str, dict[str, int | str | dict[str, typing.Any]]] = {}
    success = True
    args = parse_args()

    logger.debug(args)

    # SETUP

    
    if args.command in ["integration", "load"] :
        success &= command(scenery.commands.scenery_setup)(args)
        if config.framework == Framework.DJANGO.value:
            success &= command(scenery.commands.django_setup)(args)

    # MAIN COMMAND

    if args.command == "integration":
        success &= command(scenery.commands.integration_tests)(args)
    elif args.command == "load":
        success &= command(scenery.commands.load_tests)(args)
    elif args.command == "inspect":
        success &= command(scenery.commands.inspect_code)(args)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)