"""Pydantic models for request/response validation."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator

from rasa.cli.scaffold import ProjectTemplateName
from rasa.shared.core.trackers import DialogueStateTracker


class PromptRequest(BaseModel):
    """Request model for prompt-to-bot endpoint."""

    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="The skill description prompt"
    )
    client_id: Optional[str] = Field(
        None, max_length=255, description="Optional client identifier"
    )

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v.strip()


class TemplateRequest(BaseModel):
    """Request model for template-to-bot endpoint."""

    template_name: ProjectTemplateName = Field(
        ...,
        description=(
            f"The template name to use ({ProjectTemplateName.supported_values()})"
        ),
    )
    client_id: Optional[str] = Field(
        None, max_length=255, description="Optional client identifier"
    )

    @validator("template_name")
    def validate_template_name(cls, v):
        if v not in ProjectTemplateName:
            raise ValueError(
                f"Template name must be one of {ProjectTemplateName.supported_values()}"
            )
        return v


class ChatMessage(BaseModel):
    """Model for chat messages."""

    type: str = Field(..., pattern="^(user|assistant)$")
    content: Union[str, List[Dict[str, Any]]] = Field(...)


class LLMBuilderRequest(BaseModel):
    """Request model for LLM builder endpoint."""

    messages: List[ChatMessage] = Field(..., min_items=1, max_items=50)


class LLMBuilderContext(BaseModel):
    """Context model for LLM builder endpoint."""

    tracker: Optional[DialogueStateTracker] = Field(None)
    bot_logs: str = Field("")
    chat_bot_files: Dict[str, str] = Field({})
    chat_history: List[ChatMessage] = Field([])

    class Config:
        """Config for LLMBuilderContext."""

        arbitrary_types_allowed = True


class BotDataUpdateRequest(BaseModel):
    """Request model for bot data updates."""

    domain_yml: Optional[str] = Field(None, alias="domain.yml")
    flows_yml: Optional[str] = Field(None, alias="flows.yml")
    config_yml: Optional[str] = Field(None, alias="config.yml")

    class Config:
        """Config for BotDataUpdateRequest."""

        allow_population_by_field_name = True


class ContentBlock(BaseModel):
    """Base model for content blocks."""

    type: str = Field(...)


class TextBlock(ContentBlock):
    """Text content block."""

    type: Literal["text"] = "text"
    text: str = Field(...)


class CodeBlock(ContentBlock):
    """Code content block."""

    type: Literal["code"] = "code"
    text: str = Field(...)
    language: Optional[str] = Field(None)


class FileBlock(ContentBlock):
    """File content block."""

    type: Literal["file"] = "file"
    file: str = Field(...)
    content: str = Field(...)


class LinkBlock(ContentBlock):
    """Link content block."""

    type: Literal["link"] = "link"
    text: str = Field(..., pattern=r"^https?://")


class LLMHelperResponse(BaseModel):
    """Response model for LLM helper."""

    content_blocks: List[Union[TextBlock, CodeBlock, FileBlock, LinkBlock]] = Field(...)


class ApiResponse(BaseModel):
    """Standard API response model."""

    status: str = Field(...)
    message: Optional[str] = Field(None)
    data: Optional[Dict[str, Any]] = Field(None)


class ApiErrorResponse(BaseModel):
    """API error response model."""

    status: Literal["error"] = "error"
    error: str = Field(...)
    details: Optional[Dict[str, Any]] = Field(None)


class ServerSentEvent(BaseModel):
    """Server-sent event model."""

    event: str = Field(...)
    data: Dict[str, Any] = Field(...)

    def format(self) -> str:
        """Format as SSE string."""
        import json

        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"


class ValidationResult(BaseModel):
    """Result of validation operation."""

    is_valid: bool = Field(...)
    errors: Optional[List[str]] = Field(None)
    warnings: Optional[List[str]] = Field(None)


class TrainingResult(BaseModel):
    """Result of training operation."""

    success: bool = Field(...)
    model_path: Optional[str] = Field(None)
    error: Optional[str] = Field(None)
