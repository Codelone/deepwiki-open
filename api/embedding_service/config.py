"""Configuration for the embedding service."""

import os
from dataclasses import dataclass


@dataclass
class EmbeddingServiceConfig:
    """Configuration for the embedding service."""
    model_name: str = "nomic-ai/nomic-embed-text-v1.5"
    cache_dir: str = os.path.join(os.path.dirname(__file__), "models")
    device: str = "cpu"
    host: str = "0.0.0.0"
    port: int = 8002
    api_key: str = "dummy-key"
    max_batch_size: int = 32
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

    @classmethod
    def from_env(cls) -> "EmbeddingServiceConfig":
        """Load configuration from environment variables."""
        return cls(
            model_name=os.getenv("EMBEDDING_MODEL_NAME", cls.model_name),
            cache_dir=os.getenv("EMBEDDING_CACHE_DIR", cls.cache_dir),
            device=os.getenv("EMBEDDING_DEVICE", cls.device),
            host=os.getenv("EMBEDDING_HOST", cls.host),
            port=int(os.getenv("EMBEDDING_PORT", str(cls.port))),
            api_key=os.getenv("EMBEDDING_API_KEY", cls.api_key),
            max_batch_size=int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", str(cls.max_batch_size)))
        )