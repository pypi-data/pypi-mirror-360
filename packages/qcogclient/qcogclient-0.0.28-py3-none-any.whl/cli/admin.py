import argparse
from typing import cast

from cli.pretty import display
from qcogclient.logger import get_logger
from qcogclient.qcog.admin import AdminClient
from qcogclient.qcog.typ import is_error

logger = get_logger(__name__)


def register_admin_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the admin command parser.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object to register the admin parser with
    """
    # Add admin command parser
    admin_parser = subparsers.add_parser("admin", help="Administrative commands")

    admin_subparsers = admin_parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="Available admin subcommands",
        required=True,
    )

    # REGISTER HERE admin subcommands

    # admin project
    register_project_commands(admin_subparsers)

    # admin login
    register_login_commands(admin_subparsers)

    # admin logout
    register_logout_commands(admin_subparsers)

    # admin whoami
    register_whoami_commands(admin_subparsers)

    # admin api-key
    register_api_key_commands(admin_subparsers)

    # admin environment
    register_environment_commands(admin_subparsers)

    # admin experiment
    register_experiment_commands(admin_subparsers)

    # admin user
    register_user_commands(admin_subparsers)


@display(logger, async_=True)
async def handle_admin_command(args: argparse.Namespace) -> dict:
    """Handle admin commands.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed command line arguments
    """
    # Here you can add command handlers by checking args.subcommand
    # and dispatching to the appropriate handler function
    subcommand = args.subcommand

    if subcommand == "project":
        return await handle_project(args)
    elif subcommand == "login":
        return await handle_login(args)
    elif subcommand == "logout":
        return await handle_logout(args)
    elif subcommand == "whoami":
        return await handle_whoami(args)
    elif subcommand == "api-key":
        return await handle_api_key(args)
    elif subcommand == "environment":
        return await handle_environment(args)
    elif subcommand == "experiment":
        return await handle_experiment(args)
    elif subcommand == "user":
        return await handle_user(args)
    else:
        raise ValueError(f"Unknown subcommand: {subcommand}")


############################################################
# Subcommands parsers
############################################################


def register_project_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register project commands.

    Parameters
    ----------
    subparsers : argparse._SubParsersAction
        The subparsers object to register the create token parser with
    """
    project_parser: argparse.ArgumentParser = subparsers.add_parser(
        name="project", help="Project operations"
    )

    project_subparsers = project_parser.add_subparsers(
        title="project subcommands",
        dest="project_subcommand",
        help="Available project subcommands",
        required=True,
    )

    ######### Create Project ###########
    create_project_parser = project_subparsers.add_parser(
        name="create", help="Create a new project"
    )

    create_project_parser.add_argument(
        "--name", type=str, help="The name of the project to create", required=True
    )

    create_project_parser.add_argument(
        "--description",
        type=str,
        help="The description of the project to create",
        required=True,
    )

    create_project_parser.add_argument(
        "--user-name", type=str, help="The name of the user to create", required=True
    )

    create_project_parser.add_argument(
        "--user-email", type=str, help="The email of the user to create", required=True
    )

    ######### List Projects ###########
    list_projects_parser = project_subparsers.add_parser(
        name="list", help="List all projects"
    )

    list_projects_parser.add_argument(
        "--limit",
        type=int,
        help="The limit of projects to list",
        required=False,
        default=100,
    )

    list_projects_parser.add_argument(
        "--offset",
        type=int,
        help="The offset of projects to list",
        required=False,
        default=0,
    )


## Environment Commands
def register_environment_commands(subparsers: argparse._SubParsersAction) -> None:
    environment_parser: argparse.ArgumentParser = subparsers.add_parser(
        name="environment", help="Environment operations"
    )

    environment_subparsers = environment_parser.add_subparsers(
        title="environment subcommands",
        dest="environment_subcommand",
        help="Available environment subcommands",
        required=True,
    )

    ######### Create Environment ###########
    create_environment_parser = environment_subparsers.add_parser(
        name="create", help="Create a new environment"
    )

    create_environment_parser.add_argument(
        "--name",
        type=str,
        help="The name of the environment to create",
        required=True,
    )

    create_environment_parser.add_argument(
        "--description",
        type=str,
        help="The description of the environment to create",
        required=False,
    )

    create_environment_parser.add_argument(
        "--docker-image",
        type=str,
        help="The docker image to use for the environment",
        required=True,
    )

    create_environment_parser.add_argument(
        "--tag",
        type=str,
        help="The tag of the environment to create",
        required=True,
    )

    create_environment_parser.add_argument(
        "--provider",
        type=str,
        help="The provider of the environment to create",
        required=False,
        default="modal",
    )

    create_environment_parser.add_argument(
        "--version",
        type=str,
        help="The version of the environment to create",
        required=False,
        default="0.0.1",
    )

    ######### Get Environment ###########
    get_environment_parser = environment_subparsers.add_parser(
        name="get", help="Get an environment"
    )

    get_environment_parser.add_argument(
        "--environment-id",
        type=str,
        help="The ID of the environment to get",
        required=True,
    )

    get_environment_parser.add_argument(
        "--identifier",
        type=str,
        help="The identifier of the environment to get",
        required=False,
        default="id",
    )

    ######### List Environments ###########
    list_environments_parser = environment_subparsers.add_parser(
        name="list", help="List all environments"
    )

    list_environments_parser.add_argument(
        "--limit",
        type=int,
        help="The limit of environments to list",
        required=False,
        default=100,
    )

    list_environments_parser.add_argument(
        "--offset",
        type=int,
        help="The offset of environments to list",
        required=False,
        default=0,
    )

    list_environments_parser.add_argument(
        "--instance",
        type=str,
        help="cpu or gpu",
        required=False,
        default=None,
        choices=["cpu", "gpu"],
    )


## Register API Key Commands
def register_api_key_commands(subparsers: argparse._SubParsersAction) -> None:
    api_key_parser = subparsers.add_parser("api-key", help="API key operations")

    api_key_subparsers = api_key_parser.add_subparsers(
        title="api-key subcommands",
        dest="api_key_subcommand",
        help="Available api-key subcommands",
        required=True,
    )

    ######### Create API Key ###########
    create_api_key_parser = api_key_subparsers.add_parser(
        name="create", help="Create a new API key"
    )

    create_api_key_parser.add_argument(
        "--user-id",
        type=str,
        help="The user ID to create the API key for",
        required=True,
    )

    create_api_key_parser.add_argument(
        "--project-id",
        type=str,
        help="The project ID to create the API key for",
        required=False,
    )

    create_api_key_parser.add_argument(
        "--basic-username",
        type=str,
        help="The username to use for basic authentication. Required if --project-id is not provided.",  # noqa
        required=False,
    )

    create_api_key_parser.add_argument(
        "--basic-password",
        type=str,
        help="The password to use for basic authentication. Required if --project-id is not provided.",  # noqa
        required=False,
    )


## Register Login Commands
def register_login_commands(subparsers: argparse._SubParsersAction) -> None:
    login_parser = subparsers.add_parser("login", help="Login to the admin API")

    login_parser.add_argument(
        "--api-key", type=str, help="The API key to login with", required=True
    )


## Register Logout Commands
def register_logout_commands(subparsers: argparse._SubParsersAction) -> None:
    subparsers.add_parser("logout", help="Logout from the admin API")


## Register Whoami Commands
def register_whoami_commands(subparsers: argparse._SubParsersAction) -> None:
    subparsers.add_parser("whoami", help="Show the current user")


## Register Experiment Commands
def register_experiment_commands(subparsers: argparse._SubParsersAction) -> None:
    experiment_parser = subparsers.add_parser(
        "experiment", help="Experiment operations"
    )

    experiment_subparsers = experiment_parser.add_subparsers(
        title="experiment subcommands",
        dest="experiment_subcommand",
        help="Available experiment subcommands",
        required=True,
    )

    ######### Create Experiment ###########
    create_experiment_parser = experiment_subparsers.add_parser(
        name="create", help="Create a new experiment"
    )

    create_experiment_parser.add_argument(
        "--name",
        type=str,
        help="The name of the experiment to create",
        required=True,
    )

    create_experiment_parser.add_argument(
        "--description",
        type=str,
        help="The description of the experiment to create",
        required=False,
    )

    create_experiment_parser.add_argument(
        "--file-path",
        type=str,
        help="The file path of the experiment to create",
        required=True,
    )

    create_experiment_parser.add_argument(
        "--format",
        type=str,
        help="The format of the experiment to create",
        required=False,
        default="zip",
    )

    ######### Get Experiment ###########
    get_experiment_parser = experiment_subparsers.add_parser(
        name="get", help="Get an experiment"
    )

    get_experiment_parser.add_argument(
        "--experiment-id",
        type=str,
        help="The ID of the experiment to get",
        required=True,
    )

    get_experiment_parser.add_argument(
        "--identifier",
        type=str,
        help="The identifier of the experiment to get",
        required=False,
        default="id",
        choices=["id", "name"],
    )

    ######### List Experiments ###########
    list_experiments_parser = experiment_subparsers.add_parser(
        name="list", help="List all experiments"
    )

    list_experiments_parser.add_argument(
        "--limit",
        type=int,
        help="The limit of experiments to list",
        required=False,
        default=100,
    )

    list_experiments_parser.add_argument(
        "--offset",
        type=int,
        help="The offset of experiments to list",
        required=False,
        default=0,
    )


## Register User Commands
def register_user_commands(subparsers: argparse._SubParsersAction) -> None:
    user_parser = subparsers.add_parser("user", help="User operations")

    user_subparsers = user_parser.add_subparsers(
        title="user subcommands",
        dest="user_subcommand",
        help="Available user subcommands",
        required=True,
    )

    ######### Get Admin User ###########
    get_admin_user_parser = user_subparsers.add_parser(
        name="get-admin-user", help="Get the admin user"
    )

    get_admin_user_parser.add_argument(
        "--basic-username",
        type=str,
        help="The username for basic authentication",
        required=True,
    )

    get_admin_user_parser.add_argument(
        "--basic-password",
        type=str,
        help="The password for basic authentication",
        required=True,
    )

    ######### Create User ###########
    create_user_parser = user_subparsers.add_parser(
        name="create", help="Create a new user"
    )

    create_user_parser.add_argument(
        "--name",
        type=str,
        help="The name of the user to create",
        required=True,
    )

    create_user_parser.add_argument(
        "--email",
        type=str,
        help="The email of the user to create",
        required=True,
    )

    create_user_parser.add_argument(
        "--project-id",
        type=str,
        help="The project ID to create the user for",
        required=False,
    )

    create_user_parser.add_argument(
        "--project-role",
        type=str,
        help="The project role of the user to create",
        required=False,
        default="viewer",
        choices=["viewer", "contributor", "owner"],
    )

    create_user_parser.add_argument(
        "--system-role",
        type=str,
        help="The system role of the user to create",
        choices=["admin", "user"],
        required=False,
        default="user",
    )


#########################################
# Handlers
#########################################
async def handle_whoami(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.whoami()
    return result


async def handle_login(args: argparse.Namespace) -> dict:
    try:
        response = AdminClient.login(api_key=args.api_key)
        error = response.get("error", None)
        if error:
            return {"error": error}

        client = AdminClient()
        whoami_result = await client.whoami()
    except Exception as e:
        return {"error": f"Failed to login: {e}"}

    if is_error(whoami_result):
        return {"error": whoami_result["error"]}

    return {"response": {"Logged in as:": whoami_result["response"]}}


async def handle_logout(args: argparse.Namespace) -> dict:
    try:
        AdminClient.logout()
        return {"response": "Logged out"}
    except Exception as e:
        return {"error": f"Failed to logout: {e}"}


############################################################
# Project Commands
############################################################


async def handle_project(args: argparse.Namespace) -> dict:
    project_subcommand = args.project_subcommand

    if project_subcommand == "create":
        return await handle_create_project(args)
    elif project_subcommand == "list":
        return await handle_list_projects(args)
    else:
        raise ValueError(f"Unknown project subcommand: {project_subcommand}")


async def handle_create_project(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.create_project(
        name=args.name,
        description=args.description,
        user_name=args.user_name,
        user_email=args.user_email,
    )
    return result


async def handle_list_projects(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.list_projects(
        limit=args.limit, offset=args.offset
    )
    return result


############################################################
# API Key Commands
############################################################


async def handle_api_key(args: argparse.Namespace) -> dict:
    api_key_subcommand = args.api_key_subcommand

    if api_key_subcommand == "create":
        return await handle_create_api_key(args)
    else:
        raise ValueError(f"Unknown api-key subcommand: {api_key_subcommand}")


async def handle_create_api_key(args: argparse.Namespace) -> dict:
    if not getattr(args, "project_id", None) and not (
        args.basic_username and args.basic_password
    ):
        raise ValueError(
            "Either --project-id or --basic-username and --basic-password must be provided"  # noqa
        )

    admin_client = AdminClient(
        basic_auth_username=args.basic_username,
        basic_auth_password=args.basic_password,
    )

    result = await admin_client.generate_api_key(
        user_id=args.user_id,
        project_id=args.project_id,
    )
    return result


############################################################
# Environment Commands
############################################################


async def handle_environment(args: argparse.Namespace) -> dict:
    environment_subcommand = args.environment_subcommand

    if environment_subcommand == "create":
        return await handle_create_environment(args)
    elif environment_subcommand == "list":
        return await handle_list_environments(args)
    elif environment_subcommand == "get":
        return await handle_get_environment(args)
    else:
        raise ValueError(f"Unknown environment subcommand: {environment_subcommand}")


async def handle_get_environment(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.get_environment(
        environment_id=args.environment_id,
        identifier=args.identifier,
    )
    return result


async def handle_create_environment(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.create_environment(
        name=args.name,
        description=args.description,
        tag=args.tag,
        docker_image=args.docker_image,
        provider=args.provider,
        version=args.version,
    )
    return result


async def handle_list_environments(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result: dict = await admin_client.list_environments(
        limit=args.limit,
        offset=args.offset,
        instance=args.instance,
    )
    return result


############################################################
# Experiment Commands
############################################################


async def handle_experiment(args: argparse.Namespace) -> dict:
    experiment_subcommand = args.experiment_subcommand

    if experiment_subcommand == "create":
        return await handle_create_experiment(args)
    elif experiment_subcommand == "list":
        return await handle_list_experiments(args)
    elif experiment_subcommand == "get":
        return await handle_get_experiment(args)
    else:
        raise ValueError(f"Unknown experiment subcommand: {experiment_subcommand}")


async def handle_create_experiment(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result = await admin_client.create_experiment(
        name=args.name,
        description=args.description,
        file_path=args.file_path,
        format=args.format,
    )
    return cast(dict, result)


async def handle_get_experiment(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result = await admin_client.get_experiment(
        experiment_id=args.experiment_id,
        identifier=args.identifier,
    )
    return result


async def handle_list_experiments(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result = await admin_client.list_experiments(limit=args.limit, offset=args.offset)
    return cast(dict, result)


############################################################
# User Commands
############################################################


async def handle_user(args: argparse.Namespace) -> dict:
    user_subcommand = args.user_subcommand

    if user_subcommand == "get-admin-user":
        return await handle_get_admin_user(args)
    elif user_subcommand == "create":
        return await handle_create_user(args)
    else:
        raise ValueError(f"Unknown user subcommand: {user_subcommand}")


async def handle_get_admin_user(args: argparse.Namespace) -> dict:
    admin_client = AdminClient(
        basic_auth_username=args.basic_username,
        basic_auth_password=args.basic_password,
    )
    result = await admin_client.get_admin_user()
    return result


async def handle_create_user(args: argparse.Namespace) -> dict:
    admin_client = AdminClient()
    result = await admin_client.get_or_create_user(
        name=args.name,
        email=args.email,
        system_role=args.system_role,
    )

    if args.project_id:
        result = await admin_client.add_user_to_project(
            user_id=result["response"]["id"],
            project_id=args.project_id,
            project_role=args.project_role,
        )

    return result
