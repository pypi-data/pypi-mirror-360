from pydantic import BaseModel, Field


class Region(BaseModel):
    name: str | None = Field(
        description="Name of the region.", examples=["backflip"], default=None
    )
    coordinates: list[list[float]] | None = Field(
        description="Coordinates of the region.",
        examples=[[0, 0, 100, 100]],
        default=None,
    )
    description: str | None = Field(
        description="Description of the region.",
        examples=["backflip"],
        default=None,
    )


class RtspToHls(BaseModel):
    hls_segment_duration: int | None = Field(
        description="HLS segment duration", examples=[2], default=None
    )
    hls_list_size: int | None = Field(
        description="HLS list size", examples=[10], default=None
    )
    max_fps: int | None = Field(description="Max FPS", examples=[20], default=None)
    max_width: int | None = Field(
        description="Max width", examples=[1280], default=None
    )
    max_height: int | None = Field(
        description="Max height", examples=[720], default=None
    )
    skip_processing: bool | None = Field(
        description="Skip ML processing of the stream.", examples=[False], default=None
    )
    use_v2: bool | None = Field(
        description="Use RTSP Stage v2.", examples=[False], default=None
    )


class HlsToFrames(BaseModel):
    target_fps: int | None = Field(
        description="Target FPS, extracted frames per second to feed to the model.",
        examples=[5],
        default=None,
    )


class MLInference(BaseModel):
    model_name: str | None = Field(
        description="Name of the model used for inference.",
        examples=["backflip-detector"],
        default=None,
    )
    model_parameters: dict | None = Field(
        description="Model parameters.",
        examples=[{"confidence_threshold": 0.7, "nms_threshold": 0.5}],
        default=None,
    )
    tracking_enabled: bool | None = Field(
        description="Tracking of the objects enabled?", examples=[True], default=None
    )
    tracking_method: str | None = Field(
        description="Tracking method to use.",
        examples=["supervision_bytetrack"],
        default=None,
    )
    tracking_parameters: dict | None = Field(
        description="Tracking parameters.", default=None
    )


class Evaluator(BaseModel):
    name: str = Field(
        description="Name of the evaluator.", examples=["object_count_evaluator"]
    )
    parameters: dict = Field(
        description="Parameters of the evaluator.",
        examples={"zones": {"All": {"classes": ["person"]}}},
    )


class Evaluation(BaseModel):
    evaluators: list[Evaluator] | None = Field(
        description="Evaluators.",
        default=None,
    )


class PipelineConfiguration(BaseModel):
    livestream_id: int = Field(description="ID of the livestream.", examples=[1])
    pipeline_id: int = Field(description="ID of the livestream pipeline.", examples=[1])
    status: str = Field(
        description="Status of the livestream pipeline.", examples=["PAUSED"]
    )
    regions: list[Region] | None = Field(
        description="Monitored regions in the livestream.",
        default=None,
    )
    rtsp_to_hls: RtspToHls | None = Field(
        description="RTSP to HLS configuration", default=None
    )
    hls_to_frames: HlsToFrames | None = Field(
        description="HLS to frames configuration", default=None
    )
    ml_inference: list[MLInference] | None = Field(
        description="ML inference configuration", default=None
    )
    evaluation: Evaluation | None = Field(
        description="Evaluation configuration", default=None
    )

    @property
    def region_names(self) -> list[str]:
        return [region.name for region in self.regions]

    @property
    def target_fps(self) -> int:
        return self.hls_to_frames.target_fps
