from requests.exceptions import HTTPError

from tenyks_sdk.sdk.client import Client
from tenyks_sdk.sdk.exceptions import ClientError
from tenyks_sdk.sdk.location import Location
from tenyks_sdk.sdk.pipeline_configuration import PipelineConfiguration
from tenyks_sdk.sdk.workspace import Workspace


class Tenyks:

    def __init__(
        self,
        client: Client,
        workspace_name: str | None = None,
    ):
        self.client = client
        self.set_workspace(workspace_name, verbose=False)

    @classmethod
    def authenticate_with_api_key(
        cls,
        api_base_url: str,
        api_key: str,
        api_secret: str,
        workspace_name: str,
    ):
        """
        Authenticate using an API key.

        Args:
            api_base_url (str): The base URL of the Tenyks API.
            api_key (str): The API key provided for authentication.
            api_secret (str): The API secret corresponding to the API key.
            workspace_name (str): The name of the workspace to use after authentication.

        Raises:
            ClientError: If authentication fails due to invalid or expired credentials.
            e: Other HTTP errors raised during the request.

        Returns:
            Tenyks: An instance of the Tenyks class.
        """
        try:
            client = Client.authenticate_with_api_key(api_base_url, api_key, api_secret)
            client.logger.info("Successfully authenticated to the Tenyks API.")
            return cls(client, workspace_name)
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ClientError(
                    "Failed to authenticate to the Tenyks API. Credentials are invalid or expired."
                )
            else:
                raise e

    @classmethod
    def authenticate_with_login(
        cls,
        api_base_url: str,
        username: str,
        password: str,
        workspace_name: str,
    ):
        """
        Authenticate using a username and password.

        Args:
            api_base_url (str): The base URL of the Tenyks API.
            username (str): The username for authentication.
            password (str): The password for authentication.
            workspace_name (str): The name of the workspace to use after authentication.

        Raises:
            ClientError: If authentication fails due to invalid credentials.
            e: Other HTTP errors raised during the request.

        Returns:
            Tenyks: An instance of the Tenyks class.
        """
        try:
            client = Client.authenticate_with_login(api_base_url, username, password)
            client.logger.info("Successfully authenticated to the Tenyks API.")
            return cls(client, workspace_name)
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ClientError(
                    "Failed to authenticate to the Tenyks API. Credentials are invalid."
                )
            else:
                raise e

    def set_workspace(self, workspace_name: str, verbose: bool = True) -> None:
        """
        Set the active workspace.

        Args:
            workspace_name (str): The name of the workspace to set as active.
            verbose (Optional[bool], optional): Whether to log the change of workspace. Defaults to True.

        Raises:
            ValueError: If the workspace name is empty or the workspace does not exist.
        """
        if not workspace_name:
            raise ValueError("Workspace name cannot be empty.")

        workspaces = self.get_workspaces()

        # Check if the provided workspace_name is in the list of workspaces
        matching_workspace = None
        for workspace in workspaces:
            if workspace.name == workspace_name:
                matching_workspace = workspace
                break

        if matching_workspace:
            self.workspace_name = matching_workspace.name
            if verbose:
                self.client.logger.info(f"Workspace set to '{workspace_name}'.")
        else:
            raise ValueError(
                f"Workspace '{workspace_name}' is not accessible or does not exist."
            )

    def get_locations(self, page: int = 1, page_size: int = 20) -> list[Location]:
        """
        Retrieve a list of locations in the current workspace.

        Returns:
            list[Location]: A list of Location objects available in the workspace.
        """
        endpoint = f"/workspaces/{self.workspace_name}/locations"
        params = {"page": page, "size": page_size}
        locations_response = self.client.get(endpoint, params=params)
        return [
            Location.from_location_response(
                {**location}, client=self.client, workspace_name=self.workspace_name
            )
            for location in locations_response["datasets"]
        ]

    def get_location_keys(self, page: int = 1, page_size: int = 10) -> list[str]:
        """
        Retrieve the keys of locations in the current workspace.

        Returns:
            list[str]: A list of location keys available in the workspace.
        """
        locations = self.get_locations(page=page, page_size=page_size)
        return [location.key for location in locations]

    def get_number_of_locations(self) -> int:
        """
        Retrieve the total number of locations in the current workspace.

        Returns:
            int: The total number of locations in the workspace.
        """
        endpoint = f"/workspaces/{self.workspace_name}/locations"
        params = {"page": 1, "size": 1}
        locations_response = self.client.get(endpoint, params=params)
        return locations_response["total_count"]

    def get_location(self, key: str) -> Location:
        """
        Retrieve a specific location by its key.

        Args:
            key (str): The key of the location to retrieve.

        Returns:
            Location: The Location object corresponding to the specified key.
        """
        endpoint = f"/workspaces/{self.workspace_name}/locations/{key}"
        location_response = self.client.get(endpoint)
        return Location.from_location_response(
            {**location_response},
            client=self.client,
            workspace_name=self.workspace_name,
        )

    def get_workspaces(self, page: int = 1, page_size: int = 10) -> list[Workspace]:
        """
        Retrieve a list of workspaces accessible to the user.

        Args:
            page (int, optional): The page number for paginated results. Defaults to 1.
            page_size (int, optional): The number of workspaces to retrieve per page. Defaults to 10.

        Returns:
            List[Workspace]: A list of Workspace objects accessible to the user.
        """
        endpoint = "/workspaces"
        params = {"page": page, "page_size": page_size}
        workspaces_response_list = self.client.get(endpoint, params=params)
        return [
            Workspace(self.client, **workspace)
            for workspace in workspaces_response_list
        ]

    def get_pipeline_configurations(
        self, page: int | None = None, page_size: int | None = None
    ) -> list[PipelineConfiguration]:
        endpoint = f"/workspaces/{self.workspace_name}/pipeline_configurations"
        if page is None and page_size is None:
            params = {}
        else:
            params = {"page": page, "size": page_size}
        pipeline_configurations_response = self.client.get(endpoint, params=params)
        return [
            PipelineConfiguration(**pipeline_configuration)
            for pipeline_configuration in pipeline_configurations_response
        ]
