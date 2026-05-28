"""Model manager for loading nomic-embed-text model."""

import os
import logging
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "nomic-embed-text")


class ModelManager:
    """Manages loading of embedding models from local path."""

    def __init__(
        self,
        model_name: str = None,
        device: str = "cpu",
        trust_remote_code: bool = True
    ):
        self.model_path = DEFAULT_LOCAL_MODEL_PATH
        self.device = device
        self.trust_remote_code = trust_remote_code
        self._model: Optional[SentenceTransformer] = None

        if not os.path.isdir(self.model_path):
            raise FileNotFoundError(
                f"Local model not found at {self.model_path}. "
                "Please download the model before starting the service."
            )
        logger.info(f"Using local model at: {self.model_path}")

    def load_model(self) -> SentenceTransformer:
        """
        Load the model from local path.

        Returns:
            SentenceTransformer: The loaded model
        """
        if self._model is not None:
            return self._model

        logger.info(f"Loading model from local path: {self.model_path}")
        self._model = SentenceTransformer(
            self.model_path,
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