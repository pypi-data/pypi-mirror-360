import argparse
import asyncio

from qcogclient.logger import get_logger, setup_logger
from qcogclient.utils import get_version

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QCog CLI tool", prog="qcog")

    # Add global arguments
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument("--log-file", help="Log file to write to")

    parser.add_argument("--version", action="version", version=get_version())

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="Available commands"
    )

    # Import and register command parsers
    from cli.admin import register_admin_parser
    from cli.experiment import register_experiment_parser
    from cli.project import register_project_parser

    register_admin_parser(subparsers)
    register_project_parser(subparsers)
    register_experiment_parser(subparsers)

    return parser


async def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging based on arguments
    setup_logger(level=args.log_level, log_file=args.log_file)

    # Import and dispatch to command handlers
    if args.command == "admin":
        from cli.admin import handle_admin_command

        await handle_admin_command(args)

    elif args.command == "project":
        from cli.project import handle_project_command

        await handle_project_command(args)

    elif args.command == "experiment":
        from cli.experiment import handle_experiment_command

        await handle_experiment_command(args)
    else:
        parser.print_help()


def entrypoint() -> None:
    asyncio.run(main())
