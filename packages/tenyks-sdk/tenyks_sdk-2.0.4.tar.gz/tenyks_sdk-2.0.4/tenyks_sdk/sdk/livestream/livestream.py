import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from tenyks_sdk.sdk.client import Client
from tenyks_sdk.sdk.livestream.utils import fill_gaps_with_no_data
from tenyks_sdk.sdk.pipeline_configuration import PipelineConfiguration
from tenyks_sdk.sdk.utils import download_file, get_no_data_ts_path


class Livestream(BaseModel):
    """
    Represents a livestream in the Tenyks platform

    Attributes:
        client (Client): The client to interact with the Tenyks API.
        workspace_name (str): Name of the workspace the livestream belongs to. Example: `"my_workspace"`.
        location_key (str): Key of the location the livestream belongs to. Example: `"my_location"`.
        id (int): ID of the livestream. Example: `1`.
        display_name (str): Display name of the livestream. Example: `"My Livestream"`.
        url (str): Source URL of the livestream. Example: `"rtsp://user:pwd@999.999.999.999:554/live/stream"`.
        created_at (datetime): Creation timestamp of the livestream. Example: `"2025-01-01T00:00:00.000000Z"`.
        timezone (str): Timezone of the livestream. Example: `"Europe/London"`.
        description (str): Description of the livestream. Example: `"My Livestream Description"`.
        status (str): Status of the livestream. Examples: `"RUNNING"`, `"PAUSED"`, `"ERROR"`, `"TERMINATED"`, `"STARTING"`.
    """

    client: Client = Field(
        ..., description="The client to interact with the Tenyks API."
    )
    workspace_name: str = Field(
        description="Name of the workspace the livestream belongs to",
        examples=["my_workspace"],
    )
    location_key: str = Field(
        description="Key of the location the livestream belongs to",
        examples=["my_location"],
    )
    id: int = Field(description="ID of the livestream", examples=[1])
    display_name: str = Field(
        description="Display name of the livestream", examples=["My Livestream"]
    )
    url: str = Field(
        description="Source URL of the livestream",
        examples=["rtsp://user:pwd@999.999.999.999:554/live/stream"],
    )
    created_at: datetime = Field(
        description="Creation timestamp of the livestream",
        examples=["2025-01-01T00:00:00.000000Z"],
    )
    timezone: str | None = Field(
        description="Timezone of the livestream",
        examples=["Europe/London"],
        default=None,
    )
    description: str = Field(
        description="Description of the livestream",
        examples=["My Livestream Description"],
    )
    status: str | None = Field(
        description="Status of the livestream",
        examples=["RUNNING", "PAUSED", "ERROR", "TERMINATED", "STARTING"],
        default=None,
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_livestream_response(
        cls,
        livestream_response: dict,
        client: Client,
        workspace_name: str,
        location_key: str,
    ) -> "Livestream":
        try:
            created_at = datetime.strptime(
                livestream_response["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except ValueError:
            created_at = datetime.fromisoformat(livestream_response["created_at"])
        return cls(
            client=client,
            workspace_name=workspace_name,
            location_key=location_key,
            id=livestream_response.get("id"),
            display_name=livestream_response.get("display_name"),
            url=livestream_response.get("url"),
            created_at=created_at,
            timezone=livestream_response.get("timezone"),
            description=livestream_response.get("description"),
            status=livestream_response.get("status"),
        )

    def start(
        self,
        use_v2: bool = False,
        skip_processing: bool = False,
        pipeline_config: dict | None = None,
        verbose: bool = False,
    ):
        body = {
            "use_v2": use_v2,
            "skip_processing": skip_processing,
        }

        if pipeline_config:
            body["pipeline_config"] = pipeline_config

        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/start"
        response = self.client.post(endpoint, body=body)
        if verbose:
            self.client.logger.info(
                f"Sent request to start livestream {self.id} ({self.display_name})."
            )
        return response

    def pause(self, verbose: bool = False):
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/pause"
        response = self.client.post(endpoint)
        if verbose:
            self.client.logger.info(
                f"Sent request to pause livestream {self.id} ({self.display_name})."
            )
        return response

    def resume(self, verbose: bool = False):
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/resume"
        response = self.client.post(endpoint)
        if verbose:
            self.client.logger.info(
                f"Sent request to resume livestream {self.id} ({self.display_name})."
            )
        return response

    def update_pipeline(self, pipeline_config: dict, verbose: bool = False):
        body = {"pipeline_config": pipeline_config}
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/update_params"
        response = self.client.post(endpoint, body=body)
        if verbose:
            self.client.logger.info(
                f"Sent request to update pipeline of livestream {self.id} ({self.display_name})."
            )
        return response

    def restart(self, verbose: bool = False):
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/restart_latest"
        response = self.client.post(endpoint)
        if verbose:
            self.client.logger.info(
                f"Sent request to restart livestream {self.id} ({self.display_name})."
            )
        return response

    def get_hls_segments(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        page: int = 1,
        page_size: int = 300,
    ) -> dict:
        """
        Fetch signed HLS segments from the API for a given time window.

        Args:
            start_timestamp (datetime): Start of the time range (UTC).
            end_timestamp (datetime): End of the time range (UTC).
            page (int): Page number for pagination (default: 1).
            size (int): Number of segments per page (default: 100, max: 1000).

        Returns:
            dict: Dictionary containing the HLS segments, the total number of segments and pagination metadata.
        """
        if end_timestamp <= start_timestamp:
            raise ValueError("End timestamp must be greater than start timestamp")

        if end_timestamp - start_timestamp > timedelta(hours=1):
            raise ValueError("Time range must be less or equal to 1 hour")

        endpoint = (
            f"/workspaces/{self.workspace_name}/datasets/{self.location_key}"
            f"/livestreams/{self.id}/hls_segments"
        )
        params = {
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "page": page,
            "size": page_size,
        }
        response = self.client.get(endpoint, params=params)
        return response

    def get_pipeline_configuration(self) -> PipelineConfiguration:
        endpoint = (
            f"/workspaces/{self.workspace_name}/datasets/{self.location_key}"
            f"/livestreams/{self.id}/pipeline_configuration"
        )
        response = self.client.get(endpoint)
        return PipelineConfiguration(**response)

    def get_predictions(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        page_size: int = 1000,
        flatten: bool = False,
        model_name: str | None = None,
        model_version: int | None = None,
    ) -> list[dict]:
        """
        Fetches predictions for all models within a given time range.

        Args:
            start_timestamp (datetime): UTC start time.
            end_timestamp (datetime): UTC end time.
            page_size (int): Number of frames per page (default 1000).
            flatten (bool): If True, flattens predictions into one row per object.

        Returns:
            list[dict]: List of frames (with predictions) or flattened predictions.
        """
        if end_timestamp < start_timestamp:
            raise ValueError("End timestamp must be after start timestamp")

        if end_timestamp - start_timestamp > timedelta(hours=1):
            raise ValueError("Time range must be 1 hour or less")

        if (model_name is not None) != (model_version is not None):
            raise ValueError(
                "If model_name or model_version is not None, both must be provided"
            )

        all_frames = []
        page = 1

        if model_name and model_version:
            endpoint = (
                f"/workspaces/{self.workspace_name}/datasets/{self.location_key}"
                f"/livestreams/{self.id}/frames"
            )
            params = {
                "start_timestamp": start_timestamp.isoformat(),
                "end_timestamp": end_timestamp.isoformat(),
                "page": page,
                "size": page_size,
                "model_name": model_name,
                "model_version": model_version,
            }
        else:
            endpoint = (
                f"/workspaces/{self.workspace_name}/datasets/{self.location_key}"
                f"/livestreams/{self.id}/frames_for_all_models"
            )
            params = {
                "start_timestamp": start_timestamp.isoformat(),
                "end_timestamp": end_timestamp.isoformat(),
                "page": page,
                "size": page_size,
            }

        while True:
            response = self.client.get(endpoint, params=params)
            if not isinstance(response, list):
                raise ValueError("Unexpected API response format")

            if not response:
                break

            all_frames.extend(response)

            # If less than page_size returned, assume last page
            if len(response) < page_size:
                break

            page += 1
            params["page"] = page

        if flatten:
            flat_predictions = []
            for frame in all_frames:
                for pred in frame.get("predictions", []):
                    flat_predictions.append(
                        {
                            "timestamp": frame["timestamp"],
                            "model_name": frame["model_name"],
                            "model_version": frame["model_version"],
                            "livestream_id": frame["livestream_id"],
                            **pred,
                        }
                    )
            return flat_predictions

        return all_frames

    def add_predictions(
        self, model_name: str, model_version: int, predictions: list[dict]
    ):
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/frames"
        params = {
            "model_name": model_name,
            "model_version": model_version,
        }
        response = self.client.post(endpoint, body=predictions, params=params)
        return response

    def delete_predictions(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        model_name: str | None = None,
        model_version: int | None = None,
    ):
        endpoint = f"/workspaces/{self.workspace_name}/datasets/{self.location_key}/livestreams/{self.id}/frames"
        params = {
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
        }
        if model_name:
            params["model_name"] = model_name
        if model_version:
            params["model_version"] = model_version
        response = self.client.delete(endpoint, params=params)
        return response

    def to_mp4(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        output_path: str,
        segment_duration: float = 2.0,
        page_size: int = 1000,
        verbose: bool = False,
    ) -> str:
        """
        Export a time window of this livestream as a single .mp4 file.

        Args:
            start_timestamp (datetime): UTC start time.
            end_timestamp (datetime): UTC end time.
            output_path (str): Final output .mp4 file path.
            segment_duration (float): Expected segment duration (default 2.0s).
            page_size (int): Max segments to fetch per page.
            verbose (bool): Whether to show download progress using `rich`.

        Returns:
            str: Path to the generated .mp4 file.
        """
        response = self.get_hls_segments(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            page=1,
            page_size=page_size,
        )
        segments = response["segments"]

        filled_segments = fill_gaps_with_no_data(
            segments=segments,
            no_data_path=get_no_data_ts_path(),
            segment_duration=segment_duration,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            input_txt_path = os.path.join(temp_dir, "input.txt")
            segment_paths = []

            progress = None
            download_task = convert_task = None

            if verbose:
                progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("{task.completed}/{task.total}"),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                    transient=True,
                )
                progress.start()

            download_jobs = []
            for i, segment in enumerate(filled_segments):
                seg_path = os.path.join(temp_dir, f"segment_{i}.ts")
                segment_paths.append(seg_path)

                if segment.get("is_filler"):
                    os.link(segment["local_path"], seg_path)
                else:
                    download_jobs.append((segment["signed_url"], seg_path))

            if verbose and progress:
                download_task = progress.add_task(
                    "Downloading segments...", total=len(download_jobs)
                )

            if download_jobs:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = {
                        executor.submit(download_file, url, path): path
                        for url, path in download_jobs
                    }
                    for future in as_completed(futures):
                        future.result()
                        if verbose and progress:
                            progress.update(download_task, advance=1)

            with open(input_txt_path, "w") as f:
                for path in segment_paths:
                    f.write(f"file '{path}'\n")

            if verbose and progress:
                convert_task = progress.add_task("Converting to mp4...", total=1)

            cmd = [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                input_txt_path,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                output_path,
            ]

            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if verbose and progress:
                progress.update(convert_task, advance=1)
                progress.stop()

        return output_path
