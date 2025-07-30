"""Models for inference operations."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InputType(str, Enum):
    """Enum for input types in inference services."""

    TEXT = "text"
    JSON = "json"
    IMAGE = "png/jpeg"
    DOCUMENT = "document"


class TextInferenceRequest(BaseModel):
    """Model for text-based inference requests."""

    text: str = Field(..., description="Text input for the model")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for the inference"
    )


class InferenceResponse(BaseModel):
    """Model for inference responses."""

    result: Any = Field(..., description="The inference result")
    processing_time: Optional[float] = Field(
        None, description="Time taken to process the inference request in seconds"
    )
    model_version: Optional[str] = Field(
        None, description="Version of the model used for inference"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata about the inference"
    )
