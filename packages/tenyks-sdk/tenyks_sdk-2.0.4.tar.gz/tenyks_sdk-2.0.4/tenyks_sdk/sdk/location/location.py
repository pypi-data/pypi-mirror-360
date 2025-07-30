from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from tenyks_sdk.sdk.client import Client
from tenyks_sdk.sdk.livestream import Livestream
from tenyks_sdk.sdk.pipeline_configuration import PipelineConfiguration


class Location(BaseModel):
    """
    A location class representing a location in the Tenyks platform

    Attributes:
        client (Client): The client to interact with the Tenyks API.
        workspace_name (str): Name of the workspace the location belongs to.
        id (int): ID of the location.
        key (str): Key of the location.
        display_name (str): Display name of the location.
        timezone (str): Timezone of the location.
        created_at (datetime): Creation timestamp of the location.
        owner_email (str): Owner email of the location.
    """

    client: Client = Field(
        ..., description="The client to interact with the Tenyks API."
    )
    workspace_name: str = Field(
        description="Name of the workspace the location belongs to",
        examples=["my_workspace"],
    )
    id: int = Field(description="ID of the location", examples=[1])
    key: str = Field(description="Key of the location", examples=["my_location"])
    display_name: str = Field(
        description="Display name of the location", examples=["My Location"]
    )
    timezone: str | None = Field(
        description="Timezone of the location", examples=["Europe/London"], default=None
    )
    created_at: datetime = Field(
        description="Creation timestamp of the location",
        examples=["2025-01-01T00:00:00"],
    )
    owner_email: EmailStr = Field(
        description="Owner email of the location", examples=["user@mail.com"]
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_location_response(
        cls,
        location_response: dict,
        client: Client,
        workspace_name: str,
    ) -> "Location":

        created_at = datetime.strptime(
            location_response.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        return cls(
            client=client,
            workspace_name=workspace_name,
            id=location_response.get("id"),
            key=location_response.get("key"),
            display_name=location_response.get("display_name"),
            timezone=location_response.get("timezone"),
            created_at=created_at,
            owner_email=location_response.get("owner_email"),
        )

    def get_livestreams(
        self, page: int | None = None, page_size: int | None = None
    ) -> list[Livestream]:
        """
        Retrieve all livestreams for the location.

        Returns:
            list[Livestream]: A list of Livestream objects available in the location.
        """
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.key}/livestreams"
        if page is None and page_size is None:
            params = {}
        else:
            params = {"page": page, "size": page_size}
        livestreams_response = self.client.get(endpoint, params=params)
        return [
            Livestream.from_livestream_response(
                {**livestream},
                client=self.client,
                workspace_name=self.workspace_name,
                location_key=self.key,
            )
            for livestream in livestreams_response["livestreams"]
        ]

    def get_livestream_ids(
        self, page: int | None = None, page_size: int | None = None
    ) -> list[int]:
        """
        Retrieve the IDs of all livestreams for the location.

        Returns:
            list[int]: A list of livestream IDs available in the location.
        """
        livestreams = self.get_livestreams(page=page, page_size=page_size)
        return [livestream.id for livestream in livestreams]

    def get_number_of_livestreams(self) -> int:
        """
        Retrieve the total number of livestreams for the location.

        Returns:
            int: The total number of livestreams in the location.
        """
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.key}/livestreams"
        params = {"page": 1, "size": 1}
        livestreams_response = self.client.get(endpoint, params=params)
        return livestreams_response["total_count"]

    def get_livestream(self, id: int) -> Livestream:
        """
        Retrieve a specific livestream by its ID.

        Args:
            id (int): The ID of the livestream to retrieve.

        Returns:
            Livestream: The Livestream object corresponding to the specified ID.
        """
        endpoint = (
            f"/workspaces/{self.workspace_name}/datasets/{self.key}/livestreams/{id}"
        )
        livestream_response = self.client.get(endpoint)
        return Livestream.from_livestream_response(
            {**livestream_response},
            client=self.client,
            workspace_name=self.workspace_name,
            location_key=self.key,
        )

    def get_pipeline_configurations(
        self, page: int | None = None, page_size: int | None = None
    ) -> list[PipelineConfiguration]:
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.key}/pipeline_configurations"
        if page is None and page_size is None:
            params = {}
        else:
            params = {"page": page, "size": page_size}
        pipeline_configurations_response = self.client.get(endpoint, params=params)
        return [
            PipelineConfiguration(**pipeline_configuration)
            for pipeline_configuration in pipeline_configurations_response
        ]

    def add_livestream(
        self,
        url: str,
        display_name: str,
        timezone: str | None = None,
        description: str = "",
        type: str = "rtsp",
        verbose: bool = False,
    ) -> Livestream:
        """
        Add a new livestream to the location.

        Args:
            url (str): The URL of the livestream (e.g. rtsp://...).
            display_name (str): The display name of the livestream.
            timezone (str): The timezone of the livestream (e.g. "Europe/London").
            description (str): The description of the livestream.
            type (str): The type of the livestream (right now only "rtsp" is supported).

        Returns:
            Livestream: The Livestream object corresponding to the newly added livestream.
        """
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.key}/livestreams"
        body = {
            "url": url,
            "display_name": display_name,
            "description": description,
            "type": type,
            "timezone": timezone,
        }
        livestream_response = self.client.post(endpoint, body=body)
        livestream = Livestream.from_livestream_response(
            {**livestream_response},
            client=self.client,
            workspace_name=self.workspace_name,
            location_key=self.key,
        )
        if verbose:
            self.client.logger.info(
                f"Livestream {livestream.display_name} added successfully with ID {livestream.id}."
            )
        return livestream

    def delete_livestream(self, id: int, verbose: bool = False):
        endpoint = (
            f"/workspaces/{self.workspace_name}/datasets/{self.key}/livestreams/{id}"
        )
        self.client.delete(endpoint)
        if verbose:
            self.client.logger.info(
                f"Sent request to terminate and delete livestream {id} from location {self.key}."
            )
        return True
