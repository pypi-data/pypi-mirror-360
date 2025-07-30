from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class InputType(str, Enum):
    TEXT = "text"
    JSON = "json"
    IMAGE = "image"
    DOCUMENT = "document"

class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    IMAGE = "image"
    DOCUMENT = "document"

class InputSchema(BaseModel):
    """Schema for input specification"""
    type: InputType = Field(..., description="Type of input the model accepts")
    description: str = Field(..., description="Description of the input data")
    sample: str = Field(..., description="Sample input for the model")

class OutputSchema(BaseModel):
    """Schema for output specification"""
    format: OutputFormat = Field(..., description="Format of the model output")
    description: str = Field(..., description="Description of the output data")
    sample: str = Field(..., description="Sample output from the model")

class ModelSchema(BaseModel):
    """Schema for model architecture details"""
    name: str = Field(..., description="Name of the individual model")
    base_model: str = Field(..., description="Base model URL")
    class_labels: List[str] = Field([], description="List of class labels the model can predict")

class ArchitectureSchema(BaseModel):
    """Schema for architecture details"""
    type: str = Field(..., description="Type of model architecture")
    description: str = Field(..., description="Description of the model architecture")
    models: List[ModelSchema] = Field([], description="List of models used in the architecture")

class TrainingDataSplitSchema(BaseModel):
    """Schema for training data split information"""
    train: int = Field(0, description="Number of training samples")
    test: int = Field(0, description="Number of test samples")
    validation: int = Field(0, description="Number of validation samples")

class TrainingDataSchema(BaseModel):
    """Schema for training data information"""
    dataset: str = Field(..., description="Name of the dataset used for training")
    description: str = Field(..., description="Description of the training dataset")
    split: TrainingDataSplitSchema = Field(default_factory=TrainingDataSplitSchema)
    preprocessing: str = Field(..., description="Preprocessing steps applied to the data")

class OverallPerformanceSchema(BaseModel):
    """Schema for overall performance metrics"""
    precision: float = Field(0.0, description="Model precision score")
    recall: float = Field(0.0, description="Model recall score")
    f1_score: float = Field(0.0, description="Model F1 score")
    total_count: int = Field(0, description="Total count of test samples")

class PerformanceSchema(BaseModel):
    """Schema for performance metrics"""
    overall: OverallPerformanceSchema = Field(default_factory=OverallPerformanceSchema)

class ContactSchema(BaseModel):
    """Schema for contact information"""
    name: str = Field(..., description="Name of the contact person")
    email: str = Field(..., description="Email of the contact person")
    repository: str = Field(..., description="Repository URL")

class InferenceSchema(BaseModel):
    """Schema for inference endpoint information"""
    endpoint: str = Field(..., description="Endpoint URL for model inference")

class ModelCardSchema(BaseModel):
    """Pydantic schema for Model Card validation matching NestJS DTOs exactly"""
    name: str = Field(..., description="Model name")
    version: str = Field("1.0.0", description="Model version")
    title: str = Field(..., description="Model title")
    description: str = Field(..., description="Model description")
    input: InputSchema
    output: OutputSchema
    architecture: ArchitectureSchema
    training_data: TrainingDataSchema
    performance: PerformanceSchema
    contact: ContactSchema
    inference: InferenceSchema
    logo: Optional[str] = Field(None, description="Logo filename")
    is_deleted: bool = Field(False, description="Deletion status")