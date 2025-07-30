from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from qcogclient.httpclient import HttpClient
from qcogclient.logger import get_logger
from qcogclient.qcog._initializer import Initializer
from qcogclient.qcog.events import (
    clear_api_key,
    clear_store,
    set_api_key,
)

logger = get_logger(__name__)


class AdminClient(Initializer):
    def __init__(
        self,
        http_client: HttpClient | None = None,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        basic_auth_username: str | None = None,
        basic_auth_password: str | None = None,
    ) -> None:
        super().__init__(
            http_client=http_client,
            base_url=base_url,
            api_key=api_key,
            basic_auth_username=basic_auth_username,
            basic_auth_password=basic_auth_password,
        )

        self._experiment_id: str | None = None
        self._environment_id: str | None = None

    @classmethod
    def login(
        cls,
        api_key: str,
    ) -> dict[str, Any]:
        """Set an API Key in the local store."""

        # Clean string of any whitespace and newlines
        api_key = api_key.strip()
        api_key = api_key.replace("\n", "")

        try:
            set_api_key(api_key)
            return {
                "response": "Login successful - Your API key is saved"  # noqa
            }
        except ValueError as e:
            logger.debug(f"Error setting API key: {e}")
            return {"error": "Another API Key is already set. Log out first."}

    @classmethod
    def logout(cls) -> None:
        clear_api_key()
        clear_store()

    @property
    def experiment_id(self) -> UUID:
        if not (attr := getattr(self, "_experiment_id", None)):
            raise ValueError("No experiment ID found. Get an experiment first.")
        return UUID(attr)

    @property
    def environment_id(self) -> UUID:
        if not (attr := getattr(self, "_environment_id", None)):
            raise ValueError("No environment ID found. Get an environment first.")
        return UUID(attr)

    async def one_time_create_api_key(self, user_id: str) -> dict[str, Any]:
        """Generates the System Admin API Key for the first time.

        Needs basic auth credentials and the ID of the SYSTEM ADMIN USER
        generated at database bootstrap.

        Parameters
        ----------
        user_id: str
            The ID of the SYSTEM ADMIN USER generated at database bootstrap.

        Returns
        -------
        dict[str, Any]
            The API key.
        """
        result = await self.client.exec("/api_keys", "POST", {"user_id": user_id})
        return {
            "response": result["x_api_key"],
        }

    async def create_user(
        self,
        *,
        email: str,
        system_role: Literal["admin", "user"],
        name: str,
    ) -> dict[str, Any]:
        # Make sure the client has the Basic Auth credentials
        # For this operation, we don't need the API key.
        return await self.client.exec(
            "/users",
            "POST",
            {
                "email": email,
                "system_role": system_role,
                "name": name,
            },
        )

    async def generate_api_key(
        self, user_id: str, project_id: str | None = None
    ) -> dict[str, Any]:
        """Generates an API key for a user.

        Parameters
        ----------
        user_id: str
            The ID of the user to generate the API key for.
        project_id: str | None
            The ID of the project to generate the API key for.
        """

        assert user_id

        return await self.client.exec(
            "/api_keys",
            "POST",
            {
                "user_id": user_id,
                "project_id": project_id,
            },
        )

    async def get_or_create_user(
        self,
        email: str,
        system_role: Literal["admin", "user"],
        name: str,
    ) -> dict[str, Any]:
        """Get a user by email. If the user does not exist, create it."""

        user: dict[str, Any] | None = None

        user_get_by_email_result = await self.client.exec(
            "/users",
            "GET",
            params={"email": email},
        )

        if error := user_get_by_email_result.get("error"):
            if "not found" in str(error).lower():
                # Create the user
                user_create_result = await self.create_user(
                    email=email,
                    system_role=system_role,
                    name=name,
                )

                if error := user_create_result.get("error"):
                    logger.error("Error creating user: %s", error)
                    return {
                        "error": error,
                    }

                user = user_create_result["response"]
            else:
                logger.error("Error getting user: %s", error)
                return {
                    "error": error,
                }
        else:
            user = user_get_by_email_result["response"]

        assert user

        return {
            "response": user,
        }

    async def create_project(
        self,
        *,
        name: str,
        description: str,
        user_name: str,
        user_email: str,
    ) -> dict[str, Any]:
        """Creates a project with a user owner associated with it.

        It also generates an API Key for the user and the project.

        Parameters
        ----------
        name: str
            The name of the project to create.
        description: str
            The description of the project to create.
        user_name: str
            The name of the user to add to the project.
        user_email: str
            The email of the user to add to the project.

        Returns
        -------
        dict[str, Any]
            The project.
        """

        # Get or create the user
        user_result = await self.get_or_create_user(
            email=user_email,
            system_role="user",
            name=user_name,
        )

        if error := user_result.get("error"):
            logger.error("Error creating user: %s", error)

            return {
                "error": error,
            }

        user = user_result["response"]

        project_result = await self.get_or_create_project(
            name=name,
            description=description,
            user_id=user["id"],
        )

        if error := project_result.get("error"):
            logger.error(f"Error creating project: {error}")
            return {
                "error": error,
            }

        project = project_result["response"]

        # Generate the API Key

        api_key_result = await self.generate_api_key(
            user_id=user["id"],
            project_id=project["id"],
        )

        if error := api_key_result.get("error"):
            logger.error(f"Error generating API key: {error}")
            return {
                "error": error,
            }

        api_key = api_key_result["response"]

        return {
            "response": {
                "user": user,
                "project": project,
                "api_key": api_key,
            }
        }

    async def whoami(self) -> dict[str, Any]:
        """Returns the current user."""
        return await self.client.exec("/whoami", "GET")

    async def get_or_create_project(
        self,
        *,
        name: str,
        description: str,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Get or create a project.

        Parameters
        ----------
        name: str
            The name of the project to create.
        description: str
            The description of the project to create.
        user_id: str | None
            The ID of the user to add to the project. If this is provided,
            the user will be added to the project as a owner.

        Returns
        -------
        dict[str, Any]
            The project.
        """

        project: dict[str, Any] | None = None

        project_get_by_name_result = await self.client.exec(
            "/projects",
            "GET",
            params={"project_name": name},
        )

        if error := project_get_by_name_result.get("error"):
            if "not found" in str(error).lower():
                # Create the project
                project_create_result = await self.client.exec(
                    "/projects",
                    "POST",
                    {
                        "name": name,
                        "description": description,
                        "user_associated": [
                            {"user_id": user_id, "project_role": "owner"},
                        ],
                    },
                )

                if error := project_create_result.get("error"):
                    logger.error(f"Error creating project: {error}")
                    return {
                        "error": error,
                    }

                project = project_create_result["response"]
            else:
                logger.error(f"Error getting project: {error}")
                return {
                    "error": error,
                }
        else:
            project = project_get_by_name_result["response"]

        assert project

        return {
            "response": project,
        }

    async def create_environment(
        self,
        name: str,
        *,
        docker_image: str,
        tag: str,
        description: str | None = None,
        provider: Literal["modal"] = "modal",
        version: str = "0.0.1",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Creates an environment."""
        return await self.client.exec(
            "/environments",
            "POST",
            {
                "name": name,
                "description": description,
                "configuration": {
                    "provider": provider,
                    "version": version,
                    "docker_image": docker_image,
                    "tag": tag,
                },
                "metadata": metadata,
            },
        )

    async def get_environment(
        self,
        environment_id: str | UUID,
        identifier: Literal["id", "name"],
        load: bool = False,
    ) -> dict[str, Any]:
        """Get an environment by ID or name."""
        result = await self.client.exec(
            f"/environments/{environment_id}",
            "GET",
            params={"identifier": identifier},
        )

        if load:
            if result.get("response"):
                self._environment_id = result["response"]["id"]

        return result

    async def list_environments(
        self,
        limit: int = 100,
        offset: int = 0,
        instance: Literal["gpu", "cpu"] | None = None,
    ) -> dict[str, Any]:
        """List all environments."""
        return await self.client.exec(
            "/environments",
            "GET",
            params={"limit": limit, "offset": offset, "instance": instance},
        )

    async def create_experiment(
        self,
        name: str,
        *,
        file_path: str,
        description: str | None = None,
        format: Literal["zip"] = "zip",
    ) -> dict[str, Any]:
        """Create an experiment."""
        return await self.client.exec(
            "/experiments",
            "POST",
            {
                "name": name,
                "description": description,
                "file_path": file_path,
                "format": format,
            },
        )

    async def get_experiment(
        self,
        experiment_id: str | UUID,
        identifier: Literal["id", "name"],
        load: bool = False,
    ) -> dict[str, Any]:
        """Get an experiment by ID or name."""
        result = await self.client.exec(
            f"/experiments/{experiment_id}",
            "GET",
            params={"identifier": identifier},
        )

        if load:
            if result.get("response"):
                self._experiment_id = result["response"]["id"]

        return result

    async def list_experiments(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List all experiments."""
        return await self.client.exec(
            "/experiments",
            "GET",
            params={"limit": limit, "offset": offset},
        )

    async def get_admin_user(self) -> dict[str, Any]:
        """Get the admin user."""
        return await self.client.exec("/users/admin_user", "GET")

    async def list_projects(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List all projects."""
        return await self.client.exec(
            "/projects",
            "GET",
            params={"limit": limit, "offset": offset},
        )

    async def add_user_to_project(
        self,
        user_id: str,
        project_id: str,
        project_role: Literal["viewer", "contributor", "owner"],
    ) -> dict[str, Any]:
        """Add a user to a project."""
        return await self.client.exec(
            "/user_projects",
            "POST",
            {
                "user_id": user_id,
                "project_id": project_id,
                "role": project_role,
            },
        )
