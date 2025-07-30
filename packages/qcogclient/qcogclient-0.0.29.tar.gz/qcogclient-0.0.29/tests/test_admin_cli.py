"""Tests for the admin CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cli.admin import handle_admin_command

from tests.conftest import MockHttpClient, parse_cli_args
import argparse

from tests._patches import (
    API_KEY_ATTRIBUTE_PATCH,
    INIT_CLIENT_PATCH,
    ADMIN_SET_API_KEY_PATCH,
    ADMIN_CLEAR_API_KEY_PATCH,
    ADMIN_CLEAR_STORE_PATCH,
)


@pytest.mark.asyncio
async def test_admin_login(
    mock_http_client: MockHttpClient,
    cli_parser,
) -> None:
    """Test the admin login command."""
    # Setup mock response
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"id": "123", "email": "test@example.com"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(cli_parser, "admin login --api-key test-api-key")
    # Patch the AdminClient to use our mock
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(ADMIN_SET_API_KEY_PATCH, return_value=None),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value={"api_key": "test-api-key"}),
    ):
        result = await handle_admin_command(args)

    # Verify the result

    assert "response" in result
    assert "Logged in as:" in result["response"]
    assert result["response"]["Logged in as:"] == {
        "id": "123",
        "email": "test@example.com",
    }

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/whoami"
    assert method == "GET"


@pytest.mark.asyncio
async def test_admin_logout(mock_http_client: MockHttpClient, cli_parser) -> None:
    """Test the admin logout command."""
    # Parse actual CLI command
    args = parse_cli_args(cli_parser, "admin logout")

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(ADMIN_CLEAR_API_KEY_PATCH, return_value=None),
        patch(ADMIN_CLEAR_STORE_PATCH, return_value=None),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"] == "Logged out"


@pytest.mark.asyncio
async def test_admin_whoami(mock_http_client: MockHttpClient, cli_parser) -> None:
    """Test the admin whoami command."""
    # Setup mock response
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"id": "123", "email": "test@example.com", "name": "Test User"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(cli_parser, "admin whoami")

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["id"] == "123"
    assert result["response"]["email"] == "test@example.com"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/whoami"
    assert method == "GET"


@pytest.mark.asyncio
async def test_admin_create_project_user_and_project_already_exist(
    mock_http_client: MockHttpClient,
    cli_parser: argparse.ArgumentParser,
) -> None:
    """Test the admin create project command."""
    # There are three api calls for this command:

    # First call
    mock_http_client.set_response(
        "/users",
        "GET",
        {"response": {"id": "123", "email": "test@example.com"}},
    )

    # Setup mock response
    mock_http_client.set_response(
        "/projects",
        "GET",
        {
            "response": {
                "id": "proj-123",
                "name": "test-project",
                "description": "A test project",
            }
        },
    )

    # Third call - API key generation
    mock_http_client.set_response(
        "/api_keys",
        "POST",
        {"response": {"id": "api-key-123", "key": "test-api-key"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        """admin project create
        --name="test-project"
        --description="A-test-project"
        --user-name="test-user"
        --user-email="test@example.com" """,
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result

    assert result["response"]["project"]["name"] == "test-project"
    assert result["response"]["project"]["description"] == "A test project"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 3

    call_1, call_2, call_3 = mock_http_client.calls

    assert call_1[0] == "/users"
    assert call_1[1] == "GET"

    assert call_2[0] == "/projects"
    assert call_2[1] == "GET"

    assert call_3[0] == "/api_keys"
    assert call_3[1] == "POST"


@pytest.mark.asyncio
async def test_admin_create_project_user_and_project_do_not_exist(
    mock_http_client: MockHttpClient,
    cli_parser: argparse.ArgumentParser,
) -> None:
    """Test the admin create project command."""
    # There are three api calls for this command:

    # First call - Get user
    mock_http_client.set_response(
        "/users",
        "GET",
        {"error": "Record not found"},
    )

    # Second call - Create user
    mock_http_client.set_response(
        "/users",
        "POST",
        {"response": {"id": "123", "email": "test@example.com"}},
    )

    # Third call - Get project
    mock_http_client.set_response(
        "/projects",
        "GET",
        {"error": "Record not found"},
    )

    # Fourth call - Create project
    mock_http_client.set_response(
        "/projects",
        "POST",
        {
            "response": {
                "id": "proj-123",
                "name": "test-project",
                "description": "A test project",
            }
        },
    )

    # Fifth call - Create API key
    mock_http_client.set_response(
        "/api_keys",
        "POST",
        {"response": {"id": "api-key-123", "key": "test-api-key"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        """admin project create
        --name="test-project"
        --description="A-test-project"
        --user-name="test-user"
        --user-email="test@example.com" """,
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result

    assert result["response"]["project"]["name"] == "test-project"
    assert result["response"]["project"]["description"] == "A test project"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 5

    call_1, call_2, call_3, call_4, call_5 = mock_http_client.calls

    assert call_1[0] == "/users"
    assert call_1[1] == "GET"

    assert call_2[0] == "/users"
    assert call_2[1] == "POST"

    assert call_3[0] == "/projects"
    assert call_3[1] == "GET"

    assert call_4[0] == "/projects"
    assert call_4[1] == "POST"

    assert call_5[0] == "/api_keys"
    assert call_5[1] == "POST"


@pytest.mark.asyncio
async def test_admin_list_projects(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin list projects command."""
    # Setup mock response
    mock_http_client.set_response(
        "/projects",
        "GET",
        {
            "response": [
                {
                    "id": "proj-123",
                    "name": "test-project",
                    "description": "A test project",
                }
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin project list --limit=100 --offset=0",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 1

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/projects"
    assert method == "GET"
    assert params == {"limit": 100, "offset": 0}


@pytest.mark.asyncio
async def test_admin_create_api_key_with_project_id(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin create API key command with project ID."""
    # Setup mock response
    mock_http_client.set_response(
        "/api_keys",
        "POST",
        {"response": {"id": "api-key-123", "key": "test-api-key"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin api-key create --user-id=user-123 --project-id=proj-123",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["key"] == "test-api-key"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/api_keys"
    assert method == "POST"
    assert data["user_id"] == "user-123"
    assert data["project_id"] == "proj-123"


@pytest.mark.asyncio
async def test_admin_create_api_key_with_basic_auth(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin create API key command with basic auth."""
    # Setup mock response
    mock_http_client.set_response(
        "/api_keys",
        "POST",
        {"response": {"id": "api-key-123", "key": "test-api-key"}},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin api-key create --user-id=user-123 --basic-username=admin --basic-password=secret",
    )

    # For basic auth, we don't need to patch the api_key since it uses a different http_client
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value=None),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["key"] == "test-api-key"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/api_keys"
    assert method == "POST"
    assert data["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_admin_create_environment(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin create environment command."""
    # Setup mock response
    mock_http_client.set_response(
        "/environments",
        "POST",
        {
            "response": {
                "id": "env-123",
                "name": "test-env",
                "description": "A test environment",
                "docker_image": "test-image:latest",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin environment create "
        "--name=test-env "
        "--description=A-test-environment "
        "--docker-image=test-image:latest "
        "--tag=latest "
        "--provider=modal "
        "--version=0.0.1",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["name"] == "test-env"
    assert result["response"]["docker_image"] == "test-image:latest"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/environments"
    assert method == "POST"


@pytest.mark.asyncio
async def test_admin_get_environment(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin get environment command."""
    # Setup mock response
    mock_http_client.set_response(
        "/environments/env-123",
        "GET",
        {
            "response": {
                "id": "env-123",
                "name": "test-env",
                "description": "A test environment",
                "docker_image": "test-image:latest",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin environment get --environment-id=env-123 --identifier=id",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["id"] == "env-123"
    assert result["response"]["name"] == "test-env"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/environments/env-123"
    assert method == "GET"
    assert params == {"identifier": "id"}


@pytest.mark.asyncio
async def test_admin_list_environments(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin list environments command."""
    # Setup mock response
    mock_http_client.set_response(
        "/environments",
        "GET",
        {
            "response": [
                {
                    "id": "env-123",
                    "name": "test-env",
                    "description": "A test environment",
                }
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin environment list --limit=100 --offset=0",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 1
    assert result["response"][0]["name"] == "test-env"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/environments"
    assert method == "GET"
    assert params == {"limit": 100, "offset": 0, "instance": None}


@pytest.mark.asyncio
async def test_admin_create_experiment(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin create experiment command."""
    # Setup mock response
    mock_http_client.set_response(
        "/experiments",
        "POST",
        {
            "response": {
                "id": "exp-123",
                "name": "test-experiment",
                "description": "A test experiment",
                "file_path": "/path/to/experiment.zip",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin experiment create "
        "--name=test-experiment "
        "--description=A-test-experiment "
        "--file-path=/path/to/experiment.zip "
        "--format=zip",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["name"] == "test-experiment"
    assert result["response"]["file_path"] == "/path/to/experiment.zip"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/experiments"
    assert method == "POST"
    assert data["name"] == "test-experiment"
    assert data["file_path"] == "/path/to/experiment.zip"


@pytest.mark.asyncio
async def test_admin_get_experiment(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin get experiment command."""
    # Setup mock response
    mock_http_client.set_response(
        "/experiments/exp-123",
        "GET",
        {
            "response": {
                "id": "exp-123",
                "name": "test-experiment",
                "description": "A test experiment",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin experiment get --experiment-id=exp-123 --identifier=id",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["id"] == "exp-123"
    assert result["response"]["name"] == "test-experiment"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/experiments/exp-123"
    assert method == "GET"
    assert params == {"identifier": "id"}


@pytest.mark.asyncio
async def test_admin_list_experiments(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin list experiments command."""
    # Setup mock response
    mock_http_client.set_response(
        "/experiments",
        "GET",
        {
            "response": [
                {
                    "id": "exp-123",
                    "name": "test-experiment",
                    "description": "A test experiment",
                }
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin experiment list --limit=100 --offset=0",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 1
    assert result["response"][0]["name"] == "test-experiment"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/experiments"
    assert method == "GET"
    assert params == {"limit": 100, "offset": 0}


@pytest.mark.asyncio
async def test_admin_get_admin_user(
    mock_http_client: MockHttpClient,
    cli_parser: argparse.ArgumentParser,
) -> None:
    """Test the admin get-admin-user command."""
    # Setup mock response
    mock_http_client.set_response(
        "/users/admin_user",
        "GET",
        {
            "response": {
                "id": "admin-123",
                "email": "admin@example.com",
                "name": "Admin User",
                "system_role": "admin",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin user get-admin-user --basic-username=admin --basic-password=secret",
    )

    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["id"] == "admin-123"
    assert result["response"]["email"] == "admin@example.com"
    assert result["response"]["system_role"] == "admin"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 1
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/users/admin_user"
    assert method == "GET"


@pytest.mark.asyncio
async def test_admin_create_user_without_project(
    mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the admin create user command without project assignment."""
    # Setup mock response for user creation
    mock_http_client.set_response(
        "/users",
        "GET",
        {"error": "Record not found"},
    )

    mock_http_client.set_response(
        "/users",
        "POST",
        {
            "response": {
                "id": "user-123",
                "email": "newuser@example.com",
                "name": "New-User",
                "system_role": "user",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin user create --name=New-User --email=newuser@example.com --system-role=user",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["id"] == "user-123"
    assert result["response"]["email"] == "newuser@example.com"
    assert result["response"]["name"] == "New-User"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 2

    # First call - try to get user
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/users"
    assert method == "GET"
    assert params == {"email": "newuser@example.com"}

    # Second call - create user
    url, method, data, params = mock_http_client.calls[1]
    assert url == "/users"
    assert method == "POST"
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New-User"


@pytest.mark.asyncio
async def test_admin_create_user_with_project(
    mock_http_client: MockHttpClient,
    cli_parser: argparse.ArgumentParser,
) -> None:
    """Test the admin create user command with project assignment."""
    # Setup mock response for user creation
    mock_http_client.set_response(
        "/users",
        "GET",
        {"error": "Record not found"},
    )

    mock_http_client.set_response(
        "/users",
        "POST",
        {
            "response": {
                "id": "user-123",
                "email": "newuser@example.com",
                "name": "New User",
                "system_role": "user",
            }
        },
    )

    # Setup mock response for adding user to project
    mock_http_client.set_response(
        "/user_projects",
        "POST",
        {
            "response": {
                "user_id": "user-123",
                "project_id": "proj-123",
                "role": "contributor",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "admin user create --name=New-User --email=newuser@example.com --system-role=user --project-id=proj-123 --project-role=contributor",
    )

    # Patch the AdminClient to use our mock and provide an API key
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(ADMIN_SET_API_KEY_PATCH, return_value=None),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value={"api_key": "test-api-key"}),
    ):
        result = await handle_admin_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["user_id"] == "user-123"
    assert result["response"]["project_id"] == "proj-123"
    assert result["response"]["role"] == "contributor"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 3

    # First call - try to get user
    url, method, data, params = mock_http_client.calls[0]
    assert url == "/users"
    assert method == "GET"

    # Second call - create user
    url, method, data, params = mock_http_client.calls[1]
    assert url == "/users"
    assert method == "POST"

    # Third call - add user to project
    url, method, data, params = mock_http_client.calls[2]
    assert url == "/user_projects"
    assert method == "POST"
    assert data["user_id"] == "user-123"
    assert data["project_id"] == "proj-123"
    assert data["role"] == "contributor"


# Error handling tests
@pytest.mark.asyncio
async def test_admin_login_error(mock_http_client: MockHttpClient, cli_parser) -> None:
    """Test the admin login command with error response."""
    # Setup mock error response
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"error": "Invalid API key"},
    )

    # Parse actual CLI command
    args = parse_cli_args(cli_parser, "admin login --api-key invalid-key")

    # Patch the AdminClient to use our mock
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(ADMIN_SET_API_KEY_PATCH, return_value=None),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value={"api_key": "test-api-key"}),
    ):
        result = await handle_admin_command(args)

    # Verify the error is returned
    assert "error" in result
    assert result["error"] == "Invalid API key"


@pytest.mark.asyncio
async def test_admin_create_api_key_missing_params_error(
    mock_http_client: MockHttpClient,
    cli_parser: argparse.ArgumentParser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the admin create API key command with missing required parameters."""
    # Parse actual CLI command (missing both project-id and basic auth)
    args = parse_cli_args(
        cli_parser,
        "admin api-key create --user-id=user-123",
    )

    # The CLI tool catches the ValueError and returns None instead of raising it
    with (
        patch(INIT_CLIENT_PATCH, return_value=mock_http_client),
        patch(API_KEY_ATTRIBUTE_PATCH, return_value="mock-api-key"),
    ):  # noqa: E501
        result = await handle_admin_command(args)

    # Verify that the result is None (indicating an error was caught and logged)
    assert result is None

    # Verify that the correct error message was logged
    assert (
        "Either --project-id or --basic-username and --basic-password must be provided"
        in caplog.text
    )  # noqa: E501


@pytest.mark.asyncio
async def test_admin_invalid_subcommand_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test handling of invalid admin subcommands."""
    # This would need to be tested differently since argparse would catch this before our handler
    # But we can test the handler directly
    from types import SimpleNamespace

    args = SimpleNamespace(subcommand="invalid_command")

    # The CLI tool catches the ValueError and returns None instead of raising it
    result = await handle_admin_command(args)

    # Verify that the result is None (indicating an error was caught and logged)
    assert result is None

    # Verify that the correct error message was logged
    assert "Unknown subcommand: invalid_command" in caplog.text
