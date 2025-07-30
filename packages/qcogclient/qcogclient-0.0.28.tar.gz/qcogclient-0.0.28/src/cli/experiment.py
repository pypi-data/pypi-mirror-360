import argparse
import json
from typing import cast

from cli.pretty import display
from qcogclient.logger import get_logger
from qcogclient.qcog.experiment import DictResponse, ExperimentClient, is_error

logger = get_logger(__name__)


def register_experiment_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the experiment command parser."""

    experiment_parser = subparsers.add_parser("experiment", help="Experiment commands")

    experiment_subparsers = experiment_parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="Available experiment subcommands",
        required=True,
    )

    # REGISTER HERE project subcommands
    register_experiment_commands(experiment_subparsers)


##########################################
# SUBCOMMANDS
##########################################


def register_experiment_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register the experiment command parser."""
    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run an experiment")

    run_parser.add_argument(
        "--name",
        type=str,
        help="Name for the run",
        required=True,
    )

    run_parser.add_argument(
        "--description",
        type=str,
        help="Description of the experiment run",
        required=False,
    )

    run_parser.add_argument(
        "--experiment",
        type=str,
        help="Select the experiment",
        required=True,
    )

    run_parser.add_argument(
        "--environment",
        type=str,
        help="Name of the environment to run the experiment in",
        required=True,
    )

    run_parser.add_argument(
        "--dataset",
        type=str,
        help="Name of the dataset to run the experiment on",
        required=True,
    )

    def parse_json(s: str) -> dict:
        # Remove any leading/trailing whitespace
        s = s.strip()
        try:
            return cast(dict, json.loads(s))
        except json.JSONDecodeError as e:
            raise argparse.ArgumentTypeError(f"Invalid JSON format: {str(e)}") from e

    run_parser.add_argument(
        "--parameters",
        type=parse_json,
        help="Parameters to run the experiment with as a JSON object",
        required=True,
    )

    # Status subcommand
    status_run_parser = subparsers.add_parser(
        "status-run", help="Get the status of an experiment run"
    )
    status_run_parser.add_argument(
        "--run-name",
        type=str,
        help="Name of the experiment run to get the status of",
    )

    # List subcommand
    list_runs_parser = subparsers.add_parser(
        "list-runs", help="List all experiment runs"
    )
    list_runs_parser.add_argument(
        "--experiment-name",
        type=str,
        help="Name of the experiment to list the runs for",
        default=None,
    )
    list_runs_parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of runs to list",
        default=100,
    )
    list_runs_parser.add_argument(
        "--skip",
        type=int,
        help="Skip the first N runs",
        default=0,
    )

    list_runs_parser.add_argument(
        "--desc",
        action="store_true",
        help="Sort the runs in descending order (default is ascending)",
        default=False,
    )

    # List checkpoints subcommand
    list_checkpoints_parser = subparsers.add_parser(
        "list-checkpoints", help="List all checkpoints for an experiment run"
    )
    list_checkpoints_parser.add_argument(
        "--run-name",
        type=str,
        help="Name of the experiment run to list the checkpoints for",
    )

    # Get checkpoint subcommand
    get_checkpoint_parser = subparsers.add_parser(
        "get-checkpoint", help="Get a checkpoint for an experiment run"
    )
    get_checkpoint_parser.add_argument(
        "--run-name",
    )
    get_checkpoint_parser.add_argument(
        "--checkpoint-name",
        type=str,
        help="Name of the checkpoint to get",
        required=True,
    )

    # Deploy checkpoint subcommand
    deploy_checkpoint_parser = subparsers.add_parser(
        "deploy-checkpoint", help="Deploy a checkpoint for an experiment run"
    )
    deploy_checkpoint_parser.add_argument(
        "--run-name",
        type=str,
        help="Name of the experiment run to deploy the checkpoint for",
        required=True,
    )
    deploy_checkpoint_parser.add_argument(
        "--checkpoint-name",
        type=str,
        help="Name of the checkpoint to deploy",
        required=True,
    )
    deploy_checkpoint_parser.add_argument(
        "--deployment-name",
        type=str,
        help="Name of the deployment",
        required=False,
        default=None,
    )
    deploy_checkpoint_parser.add_argument(
        "--release-notes",
        type=str,
        help="Release notes for the deployment",
        required=False,
        default=None,
    )
    deploy_checkpoint_parser.add_argument(
        "--version",
        type=str,
        help="Version of the deployment as a valid semver string (e.g. v0.0.1)",
        default="v0.0.1",
    )

    # List deployments subcommand
    list_deployments_parser = subparsers.add_parser(
        "list-deployments", help="List all deployments for an experiment run"
    )
    list_deployments_parser.add_argument(
        "--run-name",
        type=str,
        help="Name of the experiment run to list the deployments for",
    )
    list_deployments_parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of deployments to list",
        default=100,
    )
    list_deployments_parser.add_argument(
        "--skip",
        type=int,
        help="Skip the first N deployments",
        default=0,
    )

    # Run inferences subcommand
    run_inferences_parser = subparsers.add_parser(
        "run-inferences", help="Run inferences for an experiment run"
    )

    run_inferences_parser.add_argument(
        "--dataset-path",
        type=str,
        help="Path to the dataset to run inferences on",
        required=True,
    )

    run_inferences_parser.add_argument(
        "--params",
        type=parse_json,
        help="Parameters to run inferences with as a JSON object",
        required=False,
        default=None,
    )

    run_inferences_parser.add_argument(
        "--run-name",
        type=str,
        help="Name of the experiment run to run inferences for",
        required=True,
    )

    run_inferences_parser.add_argument(
        "--deployment-name",
        type=str,
        help="Name of the deployment to run inferences for",
        required=False,
        default=None,
    )

    run_inferences_parser.add_argument(
        "--file-name",
        type=str,
        help="Name of the file to save the inferences to",
        required=False,
    )


##########################################
# MAIN HANDLER
##########################################


@display(logger, async_=True)
async def handle_experiment_command(args: argparse.Namespace) -> DictResponse:
    """Handle the experiment command."""
    subcommand = args.subcommand

    if subcommand == "run":
        return await handle_run_experiment(args)
    elif subcommand == "list-runs":
        return await handle_list_experiment_runs(args)
    elif subcommand == "status-run":
        return await handle_status_experiment_run(args)
    elif subcommand == "list-checkpoints":
        return await handle_list_experiment_run_checkpoints(args)
    elif subcommand == "get-checkpoint":
        return await handle_get_experiment_run_checkpoint(args)
    elif subcommand == "deploy-checkpoint":
        return await handle_deploy_checkpoint(args)
    elif subcommand == "list-deployments":
        return await handle_list_experiment_run_deployments(args)
    elif subcommand == "run-inferences":
        return await handle_run_inferences(args)
    else:
        raise ValueError(f"Unknown experiment subcommand: {subcommand}")


async def handle_get_experiment_run_checkpoint(
    args: argparse.Namespace,
) -> DictResponse:
    """Handle the get experiment run checkpoint command."""
    client = ExperimentClient()
    return await client.select_experiment_run_checkpoint(
        run_name=args.run_name,
        checkpoint_name=args.checkpoint_name,
    )


async def handle_list_experiment_run_deployments(
    args: argparse.Namespace,
) -> DictResponse:
    """Handle the list experiment run deployments command."""
    client = ExperimentClient()
    return await client.list_deployments(run_name=args.run_name)


async def handle_status_experiment_run(args: argparse.Namespace) -> DictResponse:
    """Handle the status experiment run command."""
    client = ExperimentClient()
    result = await client.get_experiment_run(run_name=args.run_name)

    if is_error(result):
        return DictResponse(
            error=result["error"],
        )

    return DictResponse(
        response=result["response"],
    )


async def handle_run_experiment(args: argparse.Namespace) -> DictResponse:
    """Handle the run experiment command."""
    client = ExperimentClient()

    try:
        return await client.run_experiment(  # type: ignore
            name=args.name,
            description=args.description,
            experiment_name=args.experiment,
            environment_name=args.environment,
            dataset_name=args.dataset,
            parameters=args.parameters,
        )

    except Exception as e:
        return DictResponse(
            error=f"Experiment failed: {str(e)}",
        )


async def handle_list_experiment_runs(args: argparse.Namespace) -> DictResponse:
    """Handle the list experiment runs command."""
    client = ExperimentClient()
    return await client.get_experiment_runs(
        experiment_name=args.experiment_name,
        limit=args.limit,
        skip=args.skip,
        descending=args.desc,
    )


async def handle_list_experiment_run_checkpoints(
    args: argparse.Namespace,
) -> DictResponse:
    """Handle the list experiment run checkpoints command."""
    client = ExperimentClient()
    return await client.list_experiment_run_checkpoints(run_name=args.run_name)


async def handle_deploy_checkpoint(args: argparse.Namespace) -> DictResponse:
    """Handle the deploy checkpoint command."""
    client = ExperimentClient()
    deployment_name = args.deployment_name or f"deployment-{args.version}"  # noqa: E501
    release_notes = (
        args.release_notes or f"Deployed {args.checkpoint_name} from {args.run_name}"
    )  # noqa: E501

    try:
        return await client.deploy_checkpoint(
            run_name=args.run_name,
            checkpoint_name=args.checkpoint_name,
            deployment_name=deployment_name,
            release_notes=release_notes,
            version=args.version,
        )

    except Exception as e:
        return DictResponse(
            error=f"Experiment failed: {str(e)}",
        )


async def handle_run_inferences(args: argparse.Namespace) -> DictResponse:
    """Handle the run inferences command."""
    client = ExperimentClient()

    try:
        response = await client.run_inferences(
            dataset_path=args.dataset_path,
            params=args.params,
            run_name=args.run_name,
            deployment_name=args.deployment_name,
        )

    except Exception as e:
        return DictResponse(
            error=f"Experiment failed: {str(e)}",
        )

    file_path = args.file_name or "predictions"

    json_file_path = f"{file_path}.json"

    with open(json_file_path, "w") as f:
        json.dump(response["response"], f, indent=2)

    return DictResponse(
        response={
            "status": "success",
            "json": json_file_path,
        }
    )
