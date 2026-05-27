"""Pydantic schemas for OpenAI-compatible embedding API."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Request model for /v1/embeddings endpoint."""
    input: Union[str, List[str]] = Field(..., description="Text(s) to embed")
    model: str = Field(default="nomic-embed-text", description="Model name")
    encoding_format: Optional[str] = Field(default="float", description="Encoding format")


class EmbeddingObject(BaseModel):
    """Single embedding object."""
    object: str = "embedding"
    embedding: List[float] = Field(..., description="The embedding vector")
    index: int = Field(..., description="Index in the batch")


class UsageInfo(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    """Response model for /v1/embeddings endpoint."""
    object: str = "list"
    data: List[EmbeddingObject]
    model: str
    usage: UsageInfo


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "local"


class ModelListResponse(BaseModel):
    """Response model for /v1/models endpoint."""
    object: str = "list"
    data: List[ModelInfo]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    model: str
    device: str
    max_sequence_length: int
    embedding_dimension: int