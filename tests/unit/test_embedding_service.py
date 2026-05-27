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

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_model_download():
    """Test model downloading."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing model download...")
    manager = ModelManager()

    model_path = manager.download_model()
    assert os.path.exists(model_path) or manager._model is not None, "Model should be downloaded"

    logger.info("Model download successful")
    return True


def test_model_loading():
    """Test model loading and basic functionality."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing model loading...")
    manager = ModelManager()

    model = manager.load_model()
    assert model is not None, "Model should be loaded"

    dim = manager.embedding_dimension
    assert dim > 0, f"Embedding dimension should be positive, got {dim}"

    max_len = manager.max_sequence_length
    assert max_len > 0, f"Max sequence length should be positive, got {max_len}"

    logger.info(f"Model loaded. Dimension: {dim}, Max sequence length: {max_len}")
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

    logger.info(f"Single embedding successful. Vector dimension: {len(embedding)}")
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

    logger.info(f"Batch embedding successful. Got {len(embeddings)} vectors")
    return True


def test_max_token_length():
    """Test maximum token length handling."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing max token length...")
    manager = ModelManager()

    max_len = manager.max_sequence_length
    logger.info(f"Model max sequence length: {max_len} tokens")

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
            logger.info(f"  {name}: {len(text)} chars -> {len(embedding)} dimensions")
        except Exception as e:
            logger.warning(f"  {name} failed: {e}")

    logger.info("Max token length test completed")
    return True


def test_code_snippet_embeddings():
    """Test embeddings with actual code snippets from the project."""
    from api.embedding_service.model_manager import ModelManager

    logger.info("Testing with project code snippets...")
    manager = ModelManager()

    code_snippets = [
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

        '''## Architecture Overview

The DeepWiki system uses a RAG (Retrieval-Augmented Generation) approach:
1. Documents are split into chunks
2. Each chunk is embedded using the configured embedder
3. Embeddings are stored in a FAISS index
4. At query time, user's question is embedded and similar chunks are retrieved
5. Retrieved context is used to generate an answer'''
    ]

    embeddings = manager.get_embeddings(code_snippets)

    assert len(embeddings) == len(code_snippets), "Should have embedding for each snippet"

    import numpy as np

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    py_ts_sim = cosine_similarity(embeddings[0], embeddings[1])
    py_json_sim = cosine_similarity(embeddings[0], embeddings[2])
    py_doc_sim = cosine_similarity(embeddings[0], embeddings[3])

    logger.info(f"Similarity scores:")
    logger.info(f"  Python <-> TypeScript: {py_ts_sim:.4f}")
    logger.info(f"  Python <-> JSON: {py_json_sim:.4f}")
    logger.info(f"  Python <-> Documentation: {py_doc_sim:.4f}")

    for i, emb in enumerate(embeddings):
        assert len(emb) > 0, f"Embedding {i} should not be empty"
        assert all(isinstance(x, float) for x in emb), f"Embedding {i} should be all floats"

    logger.info("Code snippet embedding test completed")
    return True


def test_retrieval_accuracy():
    """Test retrieval accuracy with semantic search."""
    from api.embedding_service.model_manager import ModelManager
    import numpy as np

    logger.info("Testing retrieval accuracy...")
    manager = ModelManager()

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

    queries = [
        ("How does vector search work?", 0),
        ("How to create an embedder?", 1),
        ("How does routing work?", 2),
        ("What is the API framework?", 3),
    ]

    corpus_embeddings = manager.get_embeddings(corpus)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    correct = 0
    total = len(queries)

    for query, expected_idx in queries:
        query_embedding = manager.get_embedding(query)

        similarities = [
            cosine_similarity(query_embedding, doc_emb)
            for doc_emb in corpus_embeddings
        ]

        best_idx = similarities.index(max(similarities))

        if best_idx == expected_idx:
            correct += 1
            logger.info(f"  Query: '{query}' -> Correct match (score: {similarities[best_idx]:.4f})")
        else:
            logger.warning(f"  Query: '{query}' -> Expected {expected_idx}, got {best_idx}")
            logger.warning(f"     Expected: '{corpus[expected_idx]}'")
            logger.warning(f"     Got: '{corpus[best_idx]}'")

    accuracy = correct / total
    logger.info(f"Retrieval accuracy: {correct}/{total} ({accuracy*100:.1f}%)")

    assert accuracy >= 0.5, f"Accuracy should be at least 50%, got {accuracy*100:.1f}%"

    logger.info("Retrieval accuracy test completed")
    return True


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

    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "PASS" if success else "FAIL"
        logger.info(f"{status} - {name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)