import argparse

from cli.pretty import display
from qcogclient.logger import get_logger
from qcogclient.qcog.project import ProjectClient

logger = get_logger(__name__)


def register_project_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the project command parser."""

    project_parser = subparsers.add_parser("project", help="Project commands")

    project_subparsers = project_parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="Available project subcommands",
        required=True,
    )

    # REGISTER HERE project subcommands
    register_dataset_commands(project_subparsers)
    register_experiment_run_commands(project_subparsers)


@display(logger, async_=True)
async def handle_project_command(args: argparse.Namespace) -> dict:
    """Handle the project command."""
    subcommand = args.subcommand

    if subcommand == "dataset":
        return await handle_dataset_command(args)
    elif subcommand == "experiment-run":
        return await handle_experiment_run_command(args)
    else:
        return {"error": f"Invalid subcommand: {subcommand}"}


#########################################
# Subcommands parsers
#########################################


# Dataset subcommands
def register_dataset_commands(subparser: argparse._SubParsersAction) -> None:
    """Register the dataset subcommands."""
    dataset_parser = subparser.add_parser("dataset", help="Dataset commands")

    DATASET_SUBPARSER = dataset_parser.add_subparsers(
        title="dataset subcommands",
        dest="dataset_subcommand",
        help="Available dataset subcommands",
        required=True,
    )

    # List dataset subcommand
    list_dataset_parser = DATASET_SUBPARSER.add_parser("list", help="List datasets")

    list_dataset_parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of datasets returned",
        default=100,
        required=False,
    )

    list_dataset_parser.add_argument(
        "--skip",
        type=int,
        help="Skip the first N datasets",
        default=0,
        required=False,
    )

    # Create dataset subcommand
    create_dataset_parser = DATASET_SUBPARSER.add_parser(
        "create", help="Create a dataset"
    )

    create_dataset_parser.add_argument(
        "--name",
        type=str,
        help="The name of the dataset to create",
        required=True,
    )

    create_dataset_parser.add_argument(
        "--location",
        type=str,
        help="The location of the dataset to create",
        required=True,
    )

    create_dataset_parser.add_argument(
        "--conf-name",
        type=str,
        help="The name of configuration to use",
        default="modal",
        required=False,
    )

    create_dataset_parser.add_argument(
        "--conf-version",
        type=str,
        help="The version of the configuration to use",
        default="0.0.1",
        required=False,
    )

    create_dataset_parser.add_argument(
        "--format",
        type=str,
        help="The format of the dataset to create",
        default="csv",
        required=False,
    )

    create_dataset_parser.add_argument(
        "--access-key",
        type=str,
        help="The access key of the dataset to create",
        required=True,
    )

    create_dataset_parser.add_argument(
        "--secret-key",
        type=str,
        help="The secret key of the dataset to create",
        required=True,
    )

    # Get dataset subcommand
    get_dataset_parser = DATASET_SUBPARSER.add_parser("get", help="Get a dataset")

    get_dataset_parser.add_argument(
        "--dataset-id",
        type=str,
        help="The ID of the dataset to get",
        required=True,
    )

    get_dataset_parser.add_argument(
        "--identifier",
        type=str,
        help="The identifier of the dataset to get",
        required=False,
        default="id",
    )

    get_dataset_parser.add_argument(
        "--load",
        type=bool,
        help="Load the dataset into the store. A loaded dataset will be available in the store as default dataset to run experiments.",  # noqa: E501
        required=False,
        default=False,
    )


# Experiment run subcommands
def register_experiment_run_commands(subparser: argparse._SubParsersAction) -> None:
    """Register the experiment run subcommands."""
    experiment_run_parser = subparser.add_parser(
        "experiment-run", help="Experiment run commands"
    )

    EXPERIMENT_RUN_SUBPARSER = experiment_run_parser.add_subparsers(
        title="experiment run subcommands",
        dest="experiment_run_subcommand",
        help="Available experiment run subcommands",
        required=True,
    )

    # Delete experiment run subcommand
    delete_run_parser = EXPERIMENT_RUN_SUBPARSER.add_parser(
        "delete", help="Delete an experiment run"
    )

    delete_run_parser.add_argument(
        "--run-id",
        type=str,
        help="The ID or name of the experiment run to delete",
        required=True,
    )

    delete_run_parser.add_argument(
        "--identifier",
        type=str,
        help="The identifier type (id or name)",
        choices=["id", "name"],
        default="id",
        required=False,
    )


async def handle_dataset_command(args: argparse.Namespace) -> dict:
    """Handle the dataset command."""

    result: dict | None = None

    dataset_subcommand = args.dataset_subcommand

    if dataset_subcommand == "create":
        project_client = ProjectClient()
        result = await project_client.create_dataset(
            name=args.name,
            dataset_location=args.location,
            credentials={
                "AWS_ACCESS_KEY_ID": args.access_key,
                "AWS_SECRET_ACCESS_KEY": args.secret_key,
            },
            dataset_format=args.format,
            conf_name=args.conf_name,
            conf_version=args.conf_version,
        )

    elif dataset_subcommand == "list":
        project_client = ProjectClient()
        result = await project_client.list_datasets(
            limit=args.limit,
            skip=args.skip,
        )

    elif dataset_subcommand == "get":
        project_client = ProjectClient()
        result = await project_client.get_dataset(
            dataset_id=args.dataset_id,
            identifier=args.identifier,
        )

    else:
        raise ValueError(f"Invalid subcommand: {args.subcommand}")

    assert result

    return result


async def handle_experiment_run_command(args: argparse.Namespace) -> dict:
    """Handle the experiment run command."""

    result: dict | None = None

    experiment_run_subcommand = args.experiment_run_subcommand

    if experiment_run_subcommand == "delete":
        project_client = ProjectClient()
        result = await project_client.delete_run(
            run_id=args.run_id,
            identifier=args.identifier,
        )

    else:
        raise ValueError(
            f"Invalid experiment run subcommand: {experiment_run_subcommand}"
        )

    assert result

    return result
