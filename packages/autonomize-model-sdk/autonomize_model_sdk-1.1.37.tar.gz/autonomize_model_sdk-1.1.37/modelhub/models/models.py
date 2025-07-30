from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra


class ResourceRequests(BaseModel):
    """
    Represents the resource requests for a stage, accepting arbitrary fields.
    """

    class Config:
        extra = Extra.allow  # Allow any additional fields not defined explicitly


class ResourceLimits(BaseModel):
    """
    Represents the resource limits for a stage, accepting arbitrary fields.
    """

    class Config:
        extra = Extra.allow  # Allow any additional fields not defined explicitly


class Resources(BaseModel):
    """
    Represents the resources for a stage.
    """

    requests: Optional[ResourceRequests] = None
    limits: Optional[ResourceLimits] = None


class Toleration(BaseModel):
    """
    Represents a toleration for a stage.
    """

    key: str
    operator: str
    value: str
    effect: str


class BlobStorageConfig(BaseModel):
    """
    Represents the blob storage configuration for a stage.
    """

    container: str
    blob_url: str
    mount_path: str


class ArtifactConfig(BaseModel):
    name: str
    path: str
    archive: Optional[Dict[str, Any]] = None


class StageArtifacts(BaseModel):
    inputs: Optional[List[ArtifactConfig]] = None
    outputs: Optional[List[ArtifactConfig]] = None


class Stage(BaseModel):
    """
    Represents a stage in a pipeline.
    """

    name: str
    type: str
    params: Dict[str, str] = {}  # Changed from Optional[dict]
    depends_on: List[str] = []  # Changed from Optional[List[str]]
    script: Optional[str] = None
    requirements: Optional[str] = None
    resources: Optional[Resources] = None
    tolerations: List[Toleration] = []  # Changed from Optional[List]
    node_selector: Dict[str, str] = {}  # Changed from Optional[Dict]
    blob_storage_config: Optional[BlobStorageConfig] = None
    artifacts: Optional[StageArtifacts] = None


class PipelineCreateRequest(BaseModel):
    """
    Represents a request to create a pipeline.
    """

    name: str
    description: Optional[str] = None
    experiment_id: str
    pyproject: Optional[str] = None
    dataset_id: Optional[str] = None
    image_tag: str
    stages: List[Stage]


class Pipeline(BaseModel):
    """
    Represents a pipeline.
    """

    pipeline_id: str
    name: str
    description: Optional[str] = None
    experiment_id: str
    dataset_id: str
    image_tag: str
    stages: List[Stage]
    status: Optional[str] = None
    workflows: Optional[List[dict]] = []


class SubmitPipelineRequest(BaseModel):
    """Submit pipeline request model"""

    modelhub_base_url: Optional[str] = None
    modelhub_client_id: Optional[str] = None
    modelhub_client_secret: Optional[str] = None


class SearchModelsCriteria(BaseModel):
    """
    Model search criteria
    """

    max_results: int = 10
    filter_string: Optional[str] = None
    order_by: Optional[List[str]] = ["last_updated_timestamp"]
    page_token: Optional[str] = None


class Alias(BaseModel):
    """
    Alias data
    """

    aliases: List[str]
    version: int


class Tag(BaseModel):
    """
    Tag data
    """

    key: str
    value: str


class UpdatePromptVersionTagsRequest(BaseModel):
    version_metadata: List[Tag]
