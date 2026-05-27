"""OpenAI-compatible embedding server using FastAPI."""

import time
import logging
from contextlib import asynccontextmanager
from typing import List, Union

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from .config import EmbeddingServiceConfig
from .model_manager import ModelManager
from .schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingObject,
    UsageInfo,
    ModelListResponse,
    ModelInfo,
    HealthResponse
)

logger = logging.getLogger(__name__)

model_manager: ModelManager = None
config: EmbeddingServiceConfig = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global model_manager, config

    logger.info("Starting embedding service...")
    config = EmbeddingServiceConfig.from_env()

    model_manager = ModelManager(
        model_name=config.model_name,
        cache_dir=config.cache_dir,
        device=config.device
    )

    logger.info("Pre-loading model...")
    model_manager.load_model()
    logger.info(f"Model loaded. Embedding dimension: {model_manager.embedding_dimension}")
    logger.info(f"Max sequence length: {model_manager.max_sequence_length}")

    yield

    logger.info("Shutting down embedding service...")


app = FastAPI(
    title="Nomic Embed Text Service",
    description="OpenAI-compatible embedding API using nomic-embed-text model",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> bool:
    """Verify API key if configured."""
    if config and config.api_key and config.api_key != "dummy-key":
        if not credentials or credentials.credentials != config.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
    return True


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    return HealthResponse(
        status="ok",
        model=model_manager.model_name,
        device=model_manager.device,
        max_sequence_length=model_manager.max_sequence_length,
        embedding_dimension=model_manager.embedding_dimension
    )


@app.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    """List available models (OpenAI-compatible)."""
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    return ModelListResponse(
        data=[
            ModelInfo(
                id=model_manager.model_name,
                created=int(time.time()),
                owned_by="local"
            )
        ]
    )


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    _: bool = Depends(verify_api_key)
):
    """
    Create embeddings (OpenAI-compatible).

    This endpoint matches the OpenAI /v1/embeddings API format.
    """
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        if isinstance(request.input, str):
            texts = [request.input]
        else:
            texts = request.input

        if len(texts) > config.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size {len(texts)} exceeds maximum {config.max_batch_size}"
            )

        embeddings = model_manager.get_embeddings(texts)

        data = [
            EmbeddingObject(
                embedding=emb,
                index=i
            )
            for i, emb in enumerate(embeddings)
        ]

        total_chars = sum(len(text) for text in texts)
        estimated_tokens = total_chars // 4

        return EmbeddingResponse(
            data=data,
            model=model_manager.model_name,
            usage=UsageInfo(
                prompt_tokens=estimated_tokens,
                total_tokens=estimated_tokens
            )
        )

    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start_server():
    """Start the embedding service."""
    import uvicorn

    config = EmbeddingServiceConfig.from_env()
    uvicorn.run(
        "api.embedding_service.server:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()