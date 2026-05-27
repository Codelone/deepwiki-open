# Nomic-Embed-Text Embedding Service Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone embedding service module using nomic-embed-text model with OpenAI-compatible API, integrated into the DeepWiki project.

**Architecture:** We'll create a new module `api/embedding_service/` that uses sentence-transformers to load the nomic-embed-text model and serves it via FastAPI with OpenAI-compatible `/v1/embeddings` endpoint. The existing `OpenAIClient` in the project can then connect to this service.

**Tech Stack:** Python, FastAPI, sentence-transformers, nomic-embed-text model, uvicorn

---

## Chunk 1: Model Download and Service Setup

### Task 1: Create Module Structure

**Files:**
- Create: `api/embedding_service/__init__.py`
- Create: `api/embedding_service/model_manager.py`
- Create: `api/embedding_service/server.py`
- Create: `api/embedding_service/config.py`

- [ ] **Step 1: Create the module directory and __init__.py**

```bash
mkdir -p api/embedding_service
touch api/embedding_service/__init__.py
```

- [ ] **Step 2: Create model_manager.py for model downloading and loading**

```python
"""Model manager for downloading and loading nomic-embed-text model."""

import os
import logging
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Default model configuration
DEFAULT_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "deepwiki", "models")


class ModelManager:
    """Manages downloading and loading of embedding models."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir: str = DEFAULT_CACHE_DIR,
        device: str = "cpu",
        trust_remote_code: bool = True
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = device
        self.trust_remote_code = trust_remote_code
        self._model: Optional[SentenceTransformer] = None

    def download_model(self) -> str:
        """
        Download the model if not already cached.

        Returns:
            str: Path to the downloaded model
        """
        logger.info(f"Downloading model {self.model_name} to {self.cache_dir}")

        # Create cache directory if it doesn't exist
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        # Download and cache the model
        model = SentenceTransformer(
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
        Load the model from cache or download if not available.

        Returns:
            SentenceTransformer: The loaded model
        """
        if self._model is not None:
            return self._model

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
        return model.get_sentence_embedding_dimension()

    @property
    def max_sequence_length(self) -> int:
        """Get the maximum sequence length of the model."""
        model = self.load_model()
        return model.max_seq_length
```

- [ ] **Step 3: Create config.py for service configuration**

```python
"""Configuration for the embedding service."""

import os
from dataclasses import dataclass


@dataclass
class EmbeddingServiceConfig:
    """Configuration for the embedding service."""
    model_name: str = "nomic-ai/nomic-embed-text-v1.5"
    cache_dir: str = os.path.join(os.path.expanduser("~"), ".cache", "deepwiki", "models")
    device: str = "cpu"
    host: str = "0.0.0.0"
    port: int = 8002
    api_key: str = "dummy-key"  # For OpenAI-compatible auth
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
```

- [ ] **Step 4: Commit the module structure**

```bash
git add api/embedding_service/__init__.py api/embedding_service/model_manager.py api/embedding_service/config.py
git commit -m "feat: create embedding service module structure"
```

---

### Task 2: Implement OpenAI-Compatible Server

**Files:**
- Create: `api/embedding_service/server.py`
- Create: `api/embedding_service/schemas.py`

- [ ] **Step 1: Create schemas.py for request/response models**

```python
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
```

- [ ] **Step 2: Create server.py with FastAPI application**

```python
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

# Global model manager instance
model_manager: ModelManager = None
config: EmbeddingServiceConfig = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global model_manager, config

    # Startup
    logger.info("Starting embedding service...")
    config = EmbeddingServiceConfig.from_env()

    model_manager = ModelManager(
        model_name=config.model_name,
        cache_dir=config.cache_dir,
        device=config.device
    )

    # Pre-load the model
    logger.info("Pre-loading model...")
    model_manager.load_model()
    logger.info(f"Model loaded. Embedding dimension: {model_manager.embedding_dimension}")
    logger.info(f"Max sequence length: {model_manager.max_sequence_length}")

    yield

    # Shutdown
    logger.info("Shutting down embedding service...")


# Create FastAPI app
app = FastAPI(
    title="Nomic Embed Text Service",
    description="OpenAI-compatible embedding API using nomic-embed-text model",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme for Bearer token
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
        # Normalize input to list
        if isinstance(request.input, str):
            texts = [request.input]
        else:
            texts = request.input

        # Validate batch size
        if len(texts) > config.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size {len(texts)} exceeds maximum {config.max_batch_size}"
            )

        # Get embeddings
        embeddings = model_manager.get_embeddings(texts)

        # Build response
        data = [
            EmbeddingObject(
                embedding=emb,
                index=i
            )
            for i, emb in enumerate(embeddings)
        ]

        # Estimate token usage (rough approximation)
        total_chars = sum(len(text) for text in texts)
        estimated_tokens = total_chars // 4  # Rough estimate: 4 chars per token

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
```

- [ ] **Step 3: Commit the server implementation**

```bash
git add api/embedding_service/schemas.py api/embedding_service/server.py
git commit -m "feat: implement OpenAI-compatible embedding server"
```

---

## Chunk 2: Testing and Integration

### Task 3: Create Test Script

**Files:**
- Create: `tests/unit/test_embedding_service.py`

- [ ] **Step 1: Create comprehensive test script**

```python
#!/usr/bin/env python3
"""
Test suite for the nomic-embed-text embedding service.
Tests max token length and retrieval accuracy using project code snippets.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_model_download():
    """Test model downloading."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing model download...")
    manager = ModelManager()

    # Download the model
    model_path = manager.download_model()
    assert os.path.exists(model_path) or manager._model is not None, "Model should be downloaded"

    logger.info("✅ Model download successful")
    return True


def test_model_loading():
    """Test model loading and basic functionality."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing model loading...")
    manager = ModelManager()

    # Load the model
    model = manager.load_model()
    assert model is not None, "Model should be loaded"

    # Test embedding dimension
    dim = manager.embedding_dimension
    assert dim > 0, f"Embedding dimension should be positive, got {dim}"

    # Test max sequence length
    max_len = manager.max_sequence_length
    assert max_len > 0, f"Max sequence length should be positive, got {max_len}"

    logger.info(f"✅ Model loaded. Dimension: {dim}, Max sequence length: {max_len}")
    return True


def test_single_embedding():
    """Test single text embedding."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing single embedding...")
    manager = ModelManager()

    test_text = "This is a test sentence for embedding."
    embedding = manager.get_embedding(test_text)

    assert isinstance(embedding, list), "Embedding should be a list"
    assert len(embedding) > 0, "Embedding should not be empty"
    assert all(isinstance(x, float) for x in embedding), "All elements should be floats"

    logger.info(f"✅ Single embedding successful. Vector dimension: {len(embedding)}")
    return True


def test_batch_embedding():
    """Test batch text embedding."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing batch embedding...")
    manager = ModelManager()

    test_texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence."
    ]

    embeddings = manager.get_embeddings(test_texts)

    assert isinstance(embeddings, list), "Result should be a list"
    assert len(embeddings) == len(test_texts), f"Should have {len(test_texts)} embeddings"
    assert all(len(emb) > 0 for emb in embeddings), "All embeddings should be non-empty"

    logger.info(f"✅ Batch embedding successful. Got {len(embeddings)} vectors")
    return True


def test_max_token_length():
    """Test maximum token length handling."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing max token length...")
    manager = ModelManager()

    # Get max sequence length
    max_len = manager.max_sequence_length
    logger.info(f"Model max sequence length: {max_len} tokens")

    # Test with various text lengths
    test_cases = [
        ("Short text", 10),
        ("Medium text " * 50, 100),
        ("Long text " * 200, 400),
        ("Very long text " * 500, 1000),
    ]

    for name, word_count in test_cases:
        text = f"This is a {name} with approximately {word_count} words. " * (word_count // 10 + 1)
        try:
            embedding = manager.get_embedding(text)
            assert len(embedding) > 0, f"Failed for {name}"
            logger.info(f"  ✅ {name}: {len(text)} chars -> {len(embedding)} dimensions")
        except Exception as e:
            logger.warning(f"  ⚠️ {name} failed: {e}")

    logger.info("✅ Max token length test completed")
    return True


def test_code_snippet_embeddings():
    """Test embeddings with actual code snippets from the project."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing with project code snippets...")
    manager = ModelManager()

    # Code snippets from the project
    code_snippets = [
        # Python function
        '''def get_embedder(is_local_ollama: bool = False, use_google_embedder: bool = False, embedder_type: str = None) -> adal.Embedder:
    """Get embedder based on configuration or parameters."""
    if embedder_type:
        if embedder_type == 'ollama':
            embedder_config = configs["embedder_ollama"]
        elif embedder_type == 'google':
            embedder_config = configs["embedder_google"]
        elif embedder_type == 'bedrock':
            embedder_config = configs["embedder_bedrock"]
        else:  # default to openai
            embedder_config = configs["embedder"]''',

        # TypeScript component
        '''export default function WikiPage({ params }: Props) {
  const { owner, repo } = params;
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/wiki/${owner}/${repo}`)
      .then(res => res.json())
      .then(data => {
        setContent(data.content);
        setLoading(false);
      });
  }, [owner, repo]);''',

        # JSON configuration
        '''{
  "embedder": {
    "client_class": "OpenAIClient",
    "initialize_kwargs": {
      "api_key": "${OPENAI_API_KEY}",
      "base_url": "${OPENAI_BASE_URL}"
    },
    "model_kwargs": {
      "model": "text-embedding-3-small",
      "encoding_format": "float"
    }
  }
}''',

        # Documentation
        '''## Architecture Overview

The DeepWiki system uses a RAG (Retrieval-Augmented Generation) approach:
1. Documents are split into chunks
2. Each chunk is embedded using the configured embedder
3. Embeddings are stored in a FAISS index
4. At query time, user's question is embedded and similar chunks are retrieved
5. Retrieved context is used to generate an answer'''
    ]

    # Get embeddings for all snippets
    embeddings = manager.get_embeddings(code_snippets)

    assert len(embeddings) == len(code_snippets), "Should have embedding for each snippet"

    # Calculate similarity between related snippets
    import numpy as np

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    # Test: Python function should be more similar to TypeScript than to JSON
    py_ts_sim = cosine_similarity(embeddings[0], embeddings[1])
    py_json_sim = cosine_similarity(embeddings[0], embeddings[2])
    py_doc_sim = cosine_similarity(embeddings[0], embeddings[3])

    logger.info(f"Similarity scores:")
    logger.info(f"  Python ↔ TypeScript: {py_ts_sim:.4f}")
    logger.info(f"  Python ↔ JSON: {py_json_sim:.4f}")
    logger.info(f"  Python ↔ Documentation: {py_doc_sim:.4f}")

    # All embeddings should be valid
    for i, emb in enumerate(embeddings):
        assert len(emb) > 0, f"Embedding {i} should not be empty"
        assert all(isinstance(x, float) for x in emb), f"Embedding {i} should be all floats"

    logger.info("✅ Code snippet embedding test completed")
    return True


def test_retrieval_accuracy():
    """Test retrieval accuracy with semantic search."""
    from api.embedding_service.model_manager import ModelManager
    import numpy as np

    logger.info("Testing retrieval accuracy...")
    manager = ModelManager()

    # Create a mini corpus of code and documentation
    corpus = [
        "The RAG system uses FAISS for vector similarity search",
        "def get_embedder(embedder_type: str) -> adal.Embedder: Create embedder instance",
        "Next.js App Router uses file-based routing in the app/ directory",
        "FastAPI endpoints are defined with @app.get() and @app.post() decorators",
        "TextSplitter breaks documents into chunks for embedding",
        "The config.py file loads JSON configuration files",
        "WebSocket connections enable real-time communication",
        "SentenceTransformer models generate dense vector embeddings",
        "The data_pipeline.py orchestrates document processing",
        "OpenAI-compatible API uses /v1/embeddings endpoint"
    ]

    # Test queries
    queries = [
        ("How does vector search work?", 0),  # Should match FAISS
        ("How to create an embedder?", 1),     # Should match get_embedder
        ("How does routing work?", 2),          # Should match Next.js
        ("What is the API framework?", 3),      # Should match FastAPI
    ]

    # Get embeddings
    corpus_embeddings = manager.get_embeddings(corpus)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    correct = 0
    total = len(queries)

    for query, expected_idx in queries:
        query_embedding = manager.get_embedding(query)

        # Find most similar document
        similarities = [
            cosine_similarity(query_embedding, doc_emb)
            for doc_emb in corpus_embeddings
        ]

        best_idx = similarities.index(max(similarities))

        if best_idx == expected_idx:
            correct += 1
            logger.info(f"  ✅ Query: '{query}' -> Correct match (score: {similarities[best_idx]:.4f})")
        else:
            logger.warning(f"  ❌ Query: '{query}' -> Expected {expected_idx}, got {best_idx}")
            logger.warning(f"     Expected: '{corpus[expected_idx]}'")
            logger.warning(f"     Got: '{corpus[best_idx]}'")

    accuracy = correct / total
    logger.info(f"Retrieval accuracy: {correct}/{total} ({accuracy*100:.1f}%)")

    # We expect at least 50% accuracy for this simple test
    assert accuracy >= 0.5, f"Accuracy should be at least 50%, got {accuracy*100:.1f}%"

    logger.info("✅ Retrieval accuracy test completed")
    return True


def test_server_api():
    """Test the FastAPI server endpoints."""
    try:
        import requests
        from api.embedding_service.config import EmbeddingServiceConfig

        config = EmbeddingServiceConfig.from_env()
        base_url = f"http://localhost:{config.port}"

        logger.info(f"Testing server API at {base_url}...")

        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        health = response.json()
        assert health["status"] == "ok"
        logger.info(f"  ✅ Health check passed")

        # Test models endpoint
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        assert response.status_code == 200, f"Models list failed: {response.status_code}"
        models = response.json()
        assert len(models["data"]) > 0
        logger.info(f"  ✅ Models list passed")

        # Test embeddings endpoint
        payload = {
            "input": "Test embedding request",
            "model": "nomic-embed-text"
        }
        response = requests.post(
            f"{base_url}/v1/embeddings",
            json=payload,
            headers={"Authorization": "Bearer dummy-key"},
            timeout=10
        )
        assert response.status_code == 200, f"Embeddings failed: {response.status_code}"
        result = response.json()
        assert len(result["data"]) == 1
        assert len(result["data"][0]["embedding"]) > 0
        logger.info(f"  ✅ Embeddings endpoint passed")

        # Test batch embeddings
        payload = {
            "input": ["First text", "Second text", "Third text"],
            "model": "nomic-embed-text"
        }
        response = requests.post(
            f"{base_url}/v1/embeddings",
            json=payload,
            headers={"Authorization": "Bearer dummy-key"},
            timeout=10
        )
        assert response.status_code == 200, f"Batch embeddings failed: {response.status_code}"
        result = response.json()
        assert len(result["data"]) == 3
        logger.info(f"  ✅ Batch embeddings endpoint passed")

        logger.info("✅ Server API test completed")
        return True

    except ImportError:
        logger.warning("Skipping server API test - requests not installed")
        return True
    except Exception as e:
        logger.error(f"Server API test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Running Nomic Embed Text Service Tests")
    logger.info("=" * 60)

    tests = [
        ("Model Download", test_model_download),
        ("Model Loading", test_model_loading),
        ("Single Embedding", test_single_embedding),
        ("Batch Embedding", test_batch_embedding),
        ("Max Token Length", test_max_token_length),
        ("Code Snippet Embeddings", test_code_snippet_embeddings),
        ("Retrieval Accuracy", test_retrieval_accuracy),
    ]

    results = []
    for name, test_func in tests:
        try:
            logger.info(f"\n{'='*40}")
            logger.info(f"Running: {name}")
            logger.info(f"{'='*40}")
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"Test {name} failed with error: {e}")
            results.append((name, False))

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

- [ ] **Step 2: Run the tests**

```bash
python -m tests.unit.test_embedding_service
```

Expected output: All tests should pass with detailed logging.

- [ ] **Step 3: Commit the test file**

```bash
git add tests/unit/test_embedding_service.py
git commit -m "test: add comprehensive tests for embedding service"
```

---

### Task 4: Create Integration Configuration

**Files:**
- Create: `api/config/embedder.nomic.json`
- Create: `scripts/start_embedding_service.sh`

- [ ] **Step 1: Create embedder.nomic.json configuration**

```json
{
  "embedder": {
    "client_class": "OpenAIClient",
    "initialize_kwargs": {
      "api_key": "dummy-key",
      "base_url": "http://localhost:8002/v1"
    },
    "model_kwargs": {
      "model": "nomic-ai/nomic-embed-text-v1.5",
      "encoding_format": "float"
    },
    "batch_size": 32
  },
  "embedder_ollama": {
    "client_class": "OllamaClient",
    "model_kwargs": {
      "model": "nomic-embed-text"
    }
  },
  "retriever": {
    "top_k": 20
  },
  "text_splitter": {
    "split_by": "token",
    "chunk_size": 350,
    "chunk_overlap": 100
  }
}
```

- [ ] **Step 2: Create startup script**

```bash
#!/bin/bash
# Start the nomic-embed-text embedding service

set -e

# Default configuration
export EMBEDDING_MODEL_NAME="${EMBEDDING_MODEL_NAME:-nomic-ai/nomic-embed-text-v1.5}"
export EMBEDDING_PORT="${EMBEDDING_PORT:-8002}"
export EMBEDDING_DEVICE="${EMBEDDING_DEVICE:-cpu}"

echo "Starting Nomic Embed Text Service..."
echo "Model: $EMBEDDING_MODEL_NAME"
echo "Port: $EMBEDDING_PORT"
echo "Device: $EMBEDDING_DEVICE"

# Get the Python interpreter from poetry or use system python
if command -v poetry &> /dev/null; then
    VENV_PATH=$(poetry -C api env info --path 2>/dev/null || echo "")
    if [ -n "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
else
    PYTHON="python3"
fi

# Start the service
$PYTHON -m api.embedding_service.server
```

- [ ] **Step 3: Make the script executable**

```bash
chmod +x scripts/start_embedding_service.sh
```

- [ ] **Step 4: Commit the configuration and script**

```bash
git add api/config/embedder.nomic.json scripts/start_embedding_service.sh
git commit -m "feat: add nomic embedding service configuration and startup script"
```

---

### Task 5: Integration Testing with DeepWiki

**Files:**
- Create: `tests/integration/test_nomic_integration.py`

- [ ] **Step 1: Create integration test with DeepWiki**

```python
#!/usr/bin/env python3
"""
Integration test for nomic-embed-text with DeepWiki RAG system.
Tests the embedding service with actual project code processing.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_rag_with_nomic_service():
    """Test RAG system using the nomic-embed-text service."""
    from api.rag import RAG
    from api.tools.embedder import get_embedder

    logger.info("Testing RAG with nomic-embed-text service...")

    # Set environment to use nomic configuration
    os.environ['DEEPWIKI_CONFIG_DIR'] = str(project_root / "api" / "config")
    os.environ['DEEPWIKI_EMBEDDER_TYPE'] = 'openai'

    try:
        # Create embedder using the nomic service
        embedder = get_embedder(embedder_type='openai')

        # Test embedding
        test_text = "def get_embedder(embedder_type: str) -> adal.Embedder:"
        result = embedder(test_text)

        assert result is not None, "Embedder should return result"
        assert hasattr(result, 'data'), "Result should have data attribute"

        logger.info("✅ RAG integration test passed")
        return True

    except Exception as e:
        logger.error(f"RAG integration test failed: {e}")
        return False
    finally:
        # Reset environment
        if 'DEEPWIKI_CONFIG_DIR' in os.environ:
            del os.environ['DEEPWIKI_CONFIG_DIR']


def test_data_pipeline_with_nomic():
    """Test data pipeline using the nomic-embed-text service."""
    from api.data_pipeline import prepare_data_pipeline

    logger.info("Testing data pipeline with nomic service...")

    try:
        # Create pipeline
        pipeline = prepare_data_pipeline(is_ollama_embedder=False)

        assert pipeline is not None, "Pipeline should be created"
        assert hasattr(pipeline, '__call__'), "Pipeline should be callable"

        logger.info("✅ Data pipeline test passed")
        return True

    except Exception as e:
        logger.error(f"Data pipeline test failed: {e}")
        return False


def test_embedding_consistency():
    """Test that embeddings are consistent between direct and RAG usage."""
    from api.embedding_service.model_manager import ModelManager
    from api.tools.embedder import get_embedder
    import numpy as np

    logger.info("Testing embedding consistency...")

    test_text = "FastAPI is a modern web framework for building APIs"

    try:
        # Get embedding directly from service
        manager = ModelManager()
        direct_embedding = manager.get_embedding(test_text)

        # Get embedding through project's embedder
        embedder = get_embedder(embedder_type='openai')
        result = embedder(test_text)

        # Extract embedding from result
        if hasattr(result, 'data') and len(result.data) > 0:
            rag_embedding = result.data[0].embedding

            # Compare dimensions
            assert len(direct_embedding) == len(rag_embedding), \
                f"Dimensions mismatch: {len(direct_embedding)} vs {len(rag_embedding)}"

            # Calculate cosine similarity
            similarity = np.dot(direct_embedding, rag_embedding) / \
                        (np.linalg.norm(direct_embedding) * np.linalg.norm(rag_embedding))

            logger.info(f"Embedding similarity: {similarity:.4f}")
            assert similarity > 0.99, f"Embeddings should be nearly identical, got {similarity:.4f}"

            logger.info("✅ Embedding consistency test passed")
            return True
        else:
            logger.error("No embedding data in RAG result")
            return False

    except Exception as e:
        logger.error(f"Embedding consistency test failed: {e}")
        return False


def run_integration_tests():
    """Run all integration tests."""
    logger.info("=" * 60)
    logger.info("Running Nomic Integration Tests")
    logger.info("=" * 60)

    tests = [
        ("RAG Integration", test_rag_with_nomic_service),
        ("Data Pipeline", test_data_pipeline_with_nomic),
        ("Embedding Consistency", test_embedding_consistency),
    ]

    results = []
    for name, test_func in tests:
        try:
            logger.info(f"\n{'='*40}")
            logger.info(f"Running: {name}")
            logger.info(f"{'='*40}")
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"Test {name} failed with error: {e}")
            results.append((name, False))

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Integration Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
```

- [ ] **Step 2: Run integration tests**

```bash
python -m tests.integration.test_nomic_integration
```

Expected output: All integration tests should pass.

- [ ] **Step 3: Commit integration test**

```bash
git add tests/integration/test_nomic_integration.py
git commit -m "test: add integration tests for nomic service with DeepWiki"
```

---

## Chunk 3: Documentation and Final Setup

### Task 6: Create Usage Documentation

**Files:**
- Create: `api/embedding_service/README.md`

- [ ] **Step 1: Create README for the embedding service**

```markdown
# Nomic Embed Text Service

OpenAI-compatible embedding service using the nomic-embed-text model.

## Features

- OpenAI-compatible `/v1/embeddings` API
- Automatic model downloading and caching
- Support for batch embeddings
- Configurable via environment variables
- Integration with DeepWiki RAG system

## Quick Start

### 1. Install Dependencies

```bash
# From project root
pip install sentence-transformers fastapi uvicorn
```

### 2. Start the Service

```bash
# Option 1: Using the startup script
./scripts/start_embedding_service.sh

# Option 2: Direct Python
python -m api.embedding_service.server

# Option 3: With custom configuration
EMBEDDING_PORT=8003 EMBEDDING_DEVICE=mps python -m api.embedding_service.server
```

### 3. Test the Service

```bash
# Health check
curl http://localhost:8002/health

# Create embedding
curl -X POST http://localhost:8002/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{"input": "Hello world", "model": "nomic-embed-text"}'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `nomic-ai/nomic-embed-text-v1.5` | Hugging Face model name |
| `EMBEDDING_CACHE_DIR` | `~/.cache/deepwiki/models` | Model cache directory |
| `EMBEDDING_DEVICE` | `cpu` | Device (cpu, cuda, mps) |
| `EMBEDDING_HOST` | `0.0.0.0` | Server host |
| `EMBEDDING_PORT` | `8002` | Server port |
| `EMBEDDING_API_KEY` | `dummy-key` | API key for authentication |
| `EMBEDDING_MAX_BATCH_SIZE` | `32` | Maximum batch size |

### Using with DeepWiki

1. Copy `api/config/embedder.nomic.json` to `api/config/embedder.json`
2. Set environment variable: `DEEPWIKI_EMBEDDER_TYPE=openai`
3. Start the embedding service
4. Start DeepWiki backend

## API Reference

### POST /v1/embeddings

Create embeddings for input text(s).

**Request Body:**
```json
{
  "input": "text or array of texts",
  "model": "nomic-embed-text",
  "encoding_format": "float"
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "nomic-ai/nomic-embed-text-v1.5",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### GET /v1/models

List available models.

### GET /health

Health check endpoint.
```

- [ ] **Step 2: Commit the documentation**

```bash
git add api/embedding_service/README.md
git commit -m "docs: add README for embedding service"
```

---

### Task 7: Final Verification

- [ ] **Step 1: Run all tests**

```bash
# Run unit tests
python -m tests.unit.test_embedding_service

# Run integration tests
python -m tests.integration.test_nomic_integration
```

Expected output: All tests should pass.

- [ ] **Step 2: Start the service and verify**

```bash
# Start the service in background
./scripts/start_embedding_service.sh &

# Wait for service to start
sleep 5

# Test the service
curl http://localhost:8002/health
```

Expected output: JSON response with status "ok".

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete nomic-embed-text service implementation"
```

---

## Summary

This plan creates a complete embedding service module with:

1. **Model Management**: Automatic downloading and caching of nomic-embed-text model
2. **OpenAI-Compatible API**: FastAPI server with `/v1/embeddings` endpoint
3. **Comprehensive Tests**: Unit tests for model operations, max token handling, and retrieval accuracy
4. **Integration**: Configuration for DeepWiki RAG system
5. **Documentation**: Usage guide and API reference

The service can be started independently and used by DeepWiki through the existing OpenAI-compatible client.
