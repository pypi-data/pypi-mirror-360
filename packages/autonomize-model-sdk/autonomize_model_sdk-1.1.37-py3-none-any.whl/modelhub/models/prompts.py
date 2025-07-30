from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now():
    """
    Get the current UTC time.

    Returns:
        datetime: The current datetime in UTC timezone.
    """
    return datetime.now(timezone.utc)


def are_brackets_balanced(text: str) -> bool:
    """Checks if all parentheses, braces, and brackets are balanced."""
    stack = []
    brackets = {"(": ")", "{": "}", "[": "]"}
    for char in text:
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if not len(stack) or brackets[stack.pop()] != char:
                return False
    return not len(stack)


class BaseModelWithValidation(BaseModel):
    """Custom base model to apply template validation globally."""

    @field_validator("template", check_fields=False)
    def validate_template_brackets(cls, value: str):
        """Ensure brackets and braces are balanced in the template."""
        if not are_brackets_balanced(value):
            raise ValueError("Unbalanced brackets or braces in template.")
        return value


class Content(BaseModel):
    type: Literal["text", "image"]
    text: str


class Message(BaseModel):
    input_variables: List[str] = Field(default_factory=list)
    content: Content
    role: Literal["user", "system"]


class VersionBase(BaseModel):
    template: List[Message] = Field(default_factory=list)
    description: Optional[str] = Field(default=None)
    version: int = Field(default=1)
    user_id: Optional[str] = Field(default="")
    prompt_id: str
    tags: Optional[Dict[str, str]] = Field(default=None)
    name: str
    creation_timestamp: datetime = Field(
        default_factory=utc_now, description="Creation timestamp"
    )
    aliases: List[str] = Field(default_factory=list)
    last_updated_timestamp: datetime = Field(
        default_factory=utc_now, description="Last update timestamp"
    )
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class PromptBase(BaseModel):
    name: str = Field()
    description: Optional[str] = Field(default=None)
    aliases: Dict[str, int] = Field(default_factory=dict)
    tags: Optional[Dict[str, str]] = Field(default=None)
    creation_timestamp: datetime = Field(
        default_factory=utc_now, description="Creation timestamp"
    )
    last_updated_timestamp: datetime = Field(
        default_factory=utc_now, description="Last update timestamp"
    )
    latest_versions: List[VersionBase] = Field(default_factory=list)
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class Prompt(PromptBase):
    """MongoDB document model for prompts"""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier"
    )

    def to_data(self):
        """
        Serialize the object to a dictionary with specific keys.

        Returns:
            dict: A dictionary containing the serialized object data with selected fields.
        """
        serialized = self.model_dump()
        return {
            "id": serialized.pop("id"),
            "name": serialized.pop("name"),
            "description": serialized.pop("description"),
            "creation_timestamp": serialized.pop("creation_timestamp"),
            "last_updated_timestamp": serialized.pop("last_updated_timestamp"),
            "latest_versions": serialized.pop("latest_versions"),
            "tags": serialized.pop("tags"),
            "aliases": serialized.pop("aliases"),
        }


class PromptVersion(VersionBase):
    """MongoDB document model for prompts versions"""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier"
    )

    def to_data(self):
        """
        Serialize the object to a dictionary with specific keys.

        Returns:
            dict: A dictionary containing the serialized object data with selected fields.
        """
        serialized = self.model_dump()
        return {
            "id": serialized.pop("id"),
            "version": serialized.pop("version"),
            "name": serialized.pop("name"),
            "user_id": serialized.pop("user_id", ""),
            "template": serialized.pop("template"),
            "description": serialized.pop("description"),
            "prompt_id": serialized.pop("prompt_id"),
            "creation_timestamp": serialized.pop("creation_timestamp"),
            "aliases": serialized.pop("aliases"),
            "tags": serialized.pop("tags", {}),
            "last_updated_timestamp": serialized.pop("last_updated_timestamp"),
        }


class CreatePrompt(BaseModelWithValidation):
    name: str
    prompt_type: Optional[str]
    description: Optional[str] = None
    template: List[Message]


class PromptWithVersion(BaseModelWithValidation):
    name: str
    prompt_type: str
    description: Optional[str] = None
    template: List[Message]
    prompt_id: str
    id: Optional[str] = None
    version: str
    aliases: Optional[List[str]]


class CreatePromptVersion(BaseModelWithValidation):
    template: List[Message]


class ReadPrompt(PromptBase):
    id: str


class ReadPromptByName(PromptBase):
    name: str


class UpdatePrompt(BaseModel):
    name: Optional[str] = None
    prompt_type: Optional[str] = None
    description: Optional[str] = None


class UpdatePromptVersion(BaseModelWithValidation):
    template: Optional[List[Message]] = None


class PromptRequest(BaseModel):
    name: str
    template: List[Message]
    commit_message: Optional[str] = Field(default=None)
    version_metadata: Optional[Dict[str, str]] = Field(default=None)
    tags: Optional[Dict[str, str]] = Field(default=None)


class Tags(BaseModel):
    key: str
    value: str


class PromptCreation(BaseModel):
    name: str
    template: List[Message]
    commit_message: Optional[str] = Field(default=None)
    version_metadata: Optional[Dict[str, str]] = Field(default=None)
    tags: Optional[List[Tags]] = Field(default=None)


class UpdatePromptVersionRequest(BaseModel):
    template: List[Message]
    commit_message: Optional[str] = Field(default=None)
    version_metadata: Optional[Dict[str, str]] = Field(default=None)


class EvaluationInput(BaseModel):
    model: Optional[str] = Field(default=None)
    provider: str = Field(
        default="azure",
        description="The LLM provider to use (e.g., 'azure', 'openai', etc.)",
    )
    template: List[Message]
    temperature: Optional[float] = 0.1
    variables: Optional[Dict[str, Any]]


class CreateRunDto(BaseModel):
    prompt_version: Optional[int] = None
    prompt_name: Optional[str] = None
    template: Optional[List[Message]] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.1
    run_name: str
    dataset_id: str
    judge_model: Optional[str] = None
    judge_temperature: Optional[float] = 0.1
    judge_provider: Optional[str] = None
    dataset_version: int
    variables: Optional[Dict[str, Any]] = None
    provider: str = Field(
        default="azure",
        description="The LLM provider to use (e.g., 'azure', 'openai', etc.)",
    )
    column_mapping: Optional[Dict[str, str]] = Field(default=None)


class EvaluationResponse(BaseModel):
    metrics: Dict
    sample_prediction: str


class PromptRunTracesDto(BaseModel):
    experiment_ids: list[str]
    filter_string: Optional[str] = None
    max_results: Optional[int] = 10000
    order_by: Optional[list[str]] = None
    page_token: Optional[str] = None
    run_id: Optional[str] = None
