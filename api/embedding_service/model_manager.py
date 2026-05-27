"""Model manager for downloading and loading nomic-embed-text model."""

import os
import logging
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
DEFAULT_LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "nomic-embed-text")


class ModelManager:
    """Manages downloading and loading of embedding models."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir: str = None,
        device: str = "cpu",
        trust_remote_code: bool = True
    ):
        self.model_name = model_name
        self.device = device
        self.trust_remote_code = trust_remote_code
        self._model: Optional[SentenceTransformer] = None

        # Determine model path: local path first, then cache_dir, then download
        if os.path.isdir(DEFAULT_LOCAL_MODEL_PATH):
            self.model_path = DEFAULT_LOCAL_MODEL_PATH
            self.use_local = True
            logger.info(f"Using local model at: {self.model_path}")
        elif cache_dir:
            self.model_path = model_name
            self.cache_dir = cache_dir
            self.use_local = False
        else:
            self.model_path = model_name
            self.cache_dir = os.path.join(os.path.dirname(__file__), "models")
            self.use_local = False

    def download_model(self) -> str:
        """
        Download the model if not already cached.

        Returns:
            str: Path to the downloaded model
        """
        if self.use_local:
            logger.info(f"Local model already available at: {self.model_path}")
            return self.model_path

        logger.info(f"Downloading model {self.model_name} to {self.cache_dir}")
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        SentenceTransformer(
            self.model_name,
            cache_folder=self.cache_dir,
            trust_remote_code=self.trust_remote_code,
            device=self.device
        )

        model_path = os.path.join(self.cache_dir, self.model_name.replace("/", "_"))
        logger.info(f"Model downloaded to {model_path}")
        return model_path

    def load_model(self) -> SentenceTransformer:
        """
        Load the model from local path or cache.

        Returns:
            SentenceTransformer: The loaded model
        """
        if self._model is not None:
            return self._model

        if self.use_local:
            logger.info(f"Loading model from local path: {self.model_path}")
            self._model = SentenceTransformer(
                self.model_path,
                trust_remote_code=self.trust_remote_code,
                device=self.device
            )
        else:
            logger.info(f"Loading model {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_dir,
                trust_remote_code=self.trust_remote_code,
                device=self.device
            )

        logger.info(f"Model loaded successfully on device: {self.device}")
        return self._model

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            list[float]: Embedding vector
        """
        model = self.load_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of input texts to embed

        Returns:
            list[list[float]]: List of embedding vectors
        """
        model = self.load_model()
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()

    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension of the model."""
        model = self.load_model()
        return model.get_embedding_dimension()

    @property
    def max_sequence_length(self) -> int:
        """Get the maximum sequence length of the model."""
        model = self.load_model()
        return model.max_seq_length