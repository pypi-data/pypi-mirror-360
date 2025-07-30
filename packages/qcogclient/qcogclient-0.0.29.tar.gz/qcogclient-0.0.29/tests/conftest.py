"""Test fixtures for qcog client tests."""

from argparse import ArgumentParser
import os
import shlex
from typing import Any, AsyncGenerator
import pytest
from cli.main import create_parser
from qcogclient.httpclient import HttpClient


class MockHttpClient(HttpClient):
    """A mock HTTP client that returns predefined responses."""

    def __init__(self) -> None:
        self.responses: dict[str, Any] = {}
        self.calls: list[tuple[str, str, dict | None, dict | None]] = []
        super().__init__()

    def set_response(self, url: str, method: str, response: dict[str, Any]) -> None:
        """Set a predefined response for a URL."""
        self.responses[(url, method)] = response

    async def exec(
        self,
        url: str,
        method: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Mock execution that returns predefined responses."""
        self.calls.append((url, method, data, params))
        print(">>> MOCK HTTP CALL")
        print(">>> URL", url)
        print(">>> METHOD", method)
        print(">>> DATA", data)
        print(">>> PARAMS", params)

        if (url, method) in self.responses:
            return self.responses[(url, method)]
        return {"response": {"mock": "data"}}


@pytest.fixture
async def mock_http_client() -> AsyncGenerator[MockHttpClient, None]:
    """Fixture that provides a mock HTTP client."""
    print(">>> MOCK HTTP CLIENT")
    client = MockHttpClient()
    client.base_url = "http://mock-server"
    client.api_version = "v1"
    yield client


@pytest.fixture
def cli_parser() -> ArgumentParser:
    """Fixture that provides the CLI parser."""
    return create_parser()


@pytest.fixture(scope="session", autouse=True)
def QCOG_ENV() -> None:
    """Fixture that sets the QCOG_ENV environment variable."""
    os.environ["QCOG_ENV"] = "TEST"
    os.environ["QCOG_DEBUG"] = "1"
    yield
    del os.environ["QCOG_ENV"]
    del os.environ["QCOG_DEBUG"]


def parse_cli_args(parser: ArgumentParser, command: str) -> Any:
    """Parse a CLI command string into arguments.

    Args:
        parser: The argument parser to use
        command: The command string to parse (e.g. "admin login --api-key 'my key with spaces'")
    """  # noqa: E501
    # Use shlex.split to properly handle quoted strings and spaces
    args = shlex.split(command)
    print(">>> ARGS", args)
    return parser.parse_args(args)
