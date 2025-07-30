"""Tests for the experiment CLI commands."""

import argparse
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from cli.experiment import handle_experiment_command

from tests.conftest import MockHttpClient, parse_cli_args
from tests._patches import (
    INIT_CLIENT_PATCH,
    INITIALIZER_STORE_GET_PATCH,
)
from unittest.mock import MagicMock


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_list_runs(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment list-runs command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Setup mock response for list runs
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs",
        "GET",
        {
            "response": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "name": "test-run",
                    "status": "completed",
                }
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment list-runs --experiment-name test-experiment --limit 100 --skip 0",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 1
    assert result["response"][0]["name"] == "test-run"

    # Verify the API was called correctly
    assert len(mock_http_client.calls) == 2  # project ID + list runs
    url, method, data, params = mock_http_client.calls[-1]
    assert url == "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs"
    assert method == "GET"
    assert params == {
        "identifier": "name",
        "experiment_id": "test-experiment",
        "limit": 100,
        "skip": 0,
        "descending": "false",
    }


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_run(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment run command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment selection
    mock_http_client.set_response(
        "/experiments/test-experiment",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-experiment",
            }
        },
    )

    # Mock environment selection
    mock_http_client.set_response(
        "/environments/test-env",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "name": "test-env",
            }
        },
    )

    # Mock dataset selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/datasets/test-dataset",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "name": "test-dataset",
            }
        },
    )

    # Mock experiment run creation
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs",
        "POST",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174004",
                "name": "test-run",
                "status": "started",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment run "
        '--name "test-run" '
        '--description "A test run" '
        '--experiment "test-experiment" '
        '--environment "test-env" '
        '--dataset "test-dataset" '
        '--parameters \'{"hyperparameters": {"epochs": 1, "batch_size": 32, "learning_rate": 0.001}, "cpu_count": 1, "memory": 1024, "gpu_type": "T4"}\'',
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result
    assert "response" in result
    assert "status" in result["response"]
    assert result["response"]["status"] == "Experiment Started"

    # Verify the API was called correctly
    assert (
        len(mock_http_client.calls) == 5
    )  # whoami + experiment + environment + dataset + run


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_status_run(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment status-run command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment run selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/test-run",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
                "status": "completed",
            }
        },
    )

    # Mock experiment run status
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment status-run --run-name test-run",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result - the response structure is what gets returned from get_experiment_run
    assert "response" in result
    assert result["response"]["name"] == "test-run"
    assert result["response"]["status"] == "completed"


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_list_checkpoints(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment list-checkpoints command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment run selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/test-run",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
            }
        },
    )

    # Mock checkpoints listing
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/checkpoints",
        "GET",
        {
            "response": [
                {
                    "name": "checkpoint-1",
                    "path": "/path/to/checkpoint-1",
                },
                {
                    "name": "checkpoint-2",
                    "path": "/path/to/checkpoint-2",
                },
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment list-checkpoints --run-name test-run",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 2
    assert result["response"][0]["name"] == "checkpoint-1"
    assert result["response"][1]["name"] == "checkpoint-2"


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_deploy_checkpoint(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment deploy-checkpoint command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment run selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/test-run",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
                "status": "completed",
            }
        },
    )

    # Mock checkpoints listing for checkpoint selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/checkpoints",
        "GET",
        {
            "response": [
                {
                    "name": "checkpoint-1",
                    "path": "/path/to/checkpoint-1",
                }
            ],
        },
    )

    # Mock checkpoint deployment
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/checkpoints/deploy",
        "POST",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "deployment_name": "test-deployment",
                "version": "v1.0.0",
            }
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment deploy-checkpoint "
        "--run-name test-run "
        "--checkpoint-name checkpoint-1 "
        "--deployment-name test-deployment "
        "--version v1.0.0",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result
    assert "response" in result
    assert result["response"]["deployment_name"] == "test-deployment"
    assert result["response"]["version"] == "v1.0.0"


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_list_deployments(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment list-deployments command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment run selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/test-run",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
            }
        },
    )

    # Mock deployments listing
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/deployments",
        "GET",
        {
            "response": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "deployment_name": "test-deployment",
                    "version": "v1.0.0",
                }
            ],
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment list-deployments --run-name test-run",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the result
    assert "response" in result
    assert len(result["response"]) == 1
    assert result["response"][0]["deployment_name"] == "test-deployment"


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_run_inferences(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser, tmp_path
) -> None:
    """Test the experiment run-inferences command."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "123e4567-e89b-12d3-a456-426614174000"}},
    )

    # Mock experiment run selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/test-run",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "test-run",
            }
        },
    )

    # Mock deployment selection
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/deployments/test-deployment",
        "GET",
        {
            "response": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "deployment_name": "test-deployment",
            }
        },
    )

    # Mock inference run
    mock_http_client.set_response(
        "/projects/123e4567-e89b-12d3-a456-426614174000/experiment_runs/123e4567-e89b-12d3-a456-426614174001/deployments/123e4567-e89b-12d3-a456-426614174002/inferences",
        "POST",
        {
            "response": [
                {"prediction": "class_a", "confidence": 0.95},
                {"prediction": "class_b", "confidence": 0.87},
            ]
        },
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment run-inferences "
        "--dataset-path /path/to/test/data "
        "--run-name test-run "
        "--deployment-name test-deployment "
        "--params '{\"batch_size\": 32}'",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Change to tmp directory for file output
    import os

    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Patch the ExperimentClient to use our mock
        with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
            result = await handle_experiment_command(args)

        # Verify the result
        assert "response" in result
        assert result["response"]["status"] == "success"
        assert "predictions.json" in result["response"]["json"]

        # Verify the file was created
        assert (tmp_path / "predictions.json").exists()
    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_experiment_invalid_subcommand_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test handling of invalid experiment subcommands."""
    # Test the handler directly with an invalid subcommand
    args = SimpleNamespace(subcommand="invalid_command")

    # The CLI tool catches the ValueError and returns None instead of raising it
    result = await handle_experiment_command(args)

    # Verify that the result is None (indicating an error was caught and logged)
    assert result is None

    # Verify that the correct error message was logged
    assert "Unknown experiment subcommand: invalid_command" in caplog.text


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_list_runs_error(
    mock_get: MagicMock, mock_http_client: MockHttpClient, cli_parser
) -> None:
    """Test the experiment list-runs command with error response."""
    # Mock response for project ID via whoami
    mock_http_client.set_response(
        "/whoami",
        "GET",
        {"response": {"project_id": "proj-123"}},
    )

    # Setup mock error response for list runs
    mock_http_client.set_response(
        "/projects/proj-123/experiment_runs",
        "GET",
        {"error": "Experiment not found"},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment list-runs "
        "--experiment-name nonexistent-experiment "
        "--limit 100 "
        "--skip 0",
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the error is returned
    assert "error" in result
    assert result["error"] == "Experiment not found"


@patch(INITIALIZER_STORE_GET_PATCH)
@pytest.mark.asyncio
async def test_experiment_run_error(
    mock_get: MagicMock,
    mock_http_client: MockHttpClient,
    cli_parser,
    caplog,
) -> None:
    """Test the experiment run command with an error response."""
    # Mock error response for experiment selection
    mock_http_client.set_response(
        "/experiments/nonexistent-experiment",
        "GET",
        {"error": "Experiment not found"},
    )

    # Parse actual CLI command
    args = parse_cli_args(
        cli_parser,
        "experiment run "
        '--name "test-run" '
        '--experiment "nonexistent-experiment" '
        '--environment "test-env" '
        '--dataset "test-dataset" '
        '--parameters \'{"param1": "value1"}\'',
    )

    # Mock the store get to return a mock api key
    mock_get.return_value = {"api_key": "mock-api-key"}

    # Patch the ExperimentClient to use our mock
    with patch(INIT_CLIENT_PATCH, return_value=mock_http_client):
        result = await handle_experiment_command(args)

    # Verify the error is returned in the result
    assert "error" in result
    assert "Error fetching experiment: Experiment not found" in result["error"]

    # Verify the error message appears in the logs
    assert "Error fetching experiment: Experiment not found" in caplog.text
