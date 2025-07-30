"""
This module is the central point for initializing the http client,
and handling dependencies injection of the http client and eventual
api_keys, basic_auth_username, and basic_auth_password or url overrides.

It also abstracts the store logic for the api_key login and logout.
"""

from pydantic import Field
from pydantic_settings import BaseSettings

from qcogclient.httpclient import HttpClient, init_client
from qcogclient.store import GET, get


class HttpClientConfig(BaseSettings):
    api_key: str | None = Field(default=None, alias="QCOG_API_KEY")
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


env_config = HttpClientConfig()


class Initializer:
    def __init__(
        self,
        *,
        http_client: HttpClient | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        basic_auth_username: str | None = None,
        basic_auth_password: str | None = None,
        timeout: int = 3000,
    ) -> None:
        # If we have an http client, we can use it straight away.
        if http_client:
            self.client = http_client

        # If we have basic auth credentials, we can use them to authenticate.
        elif basic_auth_username and basic_auth_password:
            self.client = init_client(
                basic_auth_username=basic_auth_username,
                basic_auth_password=basic_auth_password,
                base_url=base_url,
                timeout=timeout,
            )

        # if an api key is provided, we can use it to authenticate.
        elif api_key:
            self.client = init_client(api_key=api_key, base_url=base_url)

        # Look for an API key in the .env file
        elif env_config.api_key:
            self.client = init_client(api_key=env_config.api_key, base_url=base_url)

        # Look for an API Key in the store.
        # store saves a json file in the user's home directory
        # and stores the api key unencrypted.
        # The events of the stores are defined in the
        # qcogclient.store module.
        # In the Initializer class we wrap the `get` function of the store
        # with a `api_key` property.
        elif self.api_key:
            self.client = init_client(api_key=self.api_key, base_url=base_url)

        else:
            raise ValueError(
                "No API key found. Either provide an API key or login first."
            )

    @property
    def api_key(self) -> str | None:
        """Retrieve the API key from the store"""
        partial_store = get({"api_key": GET})
        return partial_store.get("api_key", None)
