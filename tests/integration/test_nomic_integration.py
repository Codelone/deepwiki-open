#!/usr/bin/env python3
"""
Integration test for nomic-embed-text with DeepWiki RAG system.
Tests the embedding service with actual project code processing.
"""

import os
import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_consistency():
    """Test that embeddings are consistent when loaded multiple times."""
    from api.embedding_service.model_manager import ModelManager
    import numpy as np

    logger.info("Testing embedding consistency...")

    test_text = "FastAPI is a modern web framework for building APIs"

    try:
        manager = ModelManager()

        # Get embedding twice
        embedding1 = manager.get_embedding(test_text)
        embedding2 = manager.get_embedding(test_text)

        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / \
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

        logger.info(f"Embedding consistency similarity: {similarity:.6f}")
        assert similarity > 0.999, f"Embeddings should be identical, got {similarity:.6f}"

        logger.info("Embedding consistency test passed")
        return True

    except Exception as e:
        logger.error(f"Embedding consistency test failed: {e}")
        return False


def test_code_similarity_semantics():
    """Test that similar code snippets have higher similarity scores."""
    from api.embedding_service.model_manager import ModelManager
    import numpy as np

    logger.info("Testing code similarity semantics...")

    try:
        manager = ModelManager()

        # Related code snippets (should be similar)
        similar_pairs = [
            (
                "def get_user(id: int) -> User:",
                "def get_item(id: int) -> Item:"
            ),
            (
                "if x > 0: return True",
                "if y < 0: return False"
            ),
            (
                "class UserManager:\n    def __init__(self):",
                "class ItemManager:\n    def __init__(self):"
            )
        ]

        # Unrelated code snippets (should be less similar)
        different_pairs = [
            (
                "def get_user(id: int) -> User:",
                "SELECT * FROM users WHERE id = 1"
            ),
            (
                "class UserManager:\n    def __init__(self):",
                "import React from 'react'"
            ),
            (
                "if x > 0: return True",
                "docker run -p 8080:80 nginx"
            )
        ]

        similar_scores = []
        different_scores = []

        for text1, text2 in similar_pairs:
            emb1 = manager.get_embedding(text1)
            emb2 = manager.get_embedding(text2)
            score = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            similar_scores.append(score)
            logger.info(f"  Similar pair: {score:.4f}")

        for text1, text2 in different_pairs:
            emb1 = manager.get_embedding(text1)
            emb2 = manager.get_embedding(text2)
            score = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            different_scores.append(score)
            logger.info(f"  Different pair: {score:.4f}")

        avg_similar = np.mean(similar_scores)
        avg_different = np.mean(different_scores)

        logger.info(f"Average similar score: {avg_similar:.4f}")
        logger.info(f"Average different score: {avg_different:.4f}")
        logger.info(f"Score gap: {avg_similar - avg_different:.4f}")

        # Similar code should have higher scores than different code
        assert avg_similar > avg_different, \
            f"Similar code should have higher scores: {avg_similar:.4f} vs {avg_different:.4f}"

        logger.info("Code similarity semantics test passed")
        return True

    except Exception as e:
        logger.error(f"Code similarity semantics test failed: {e}")
        return False


def test_batch_vs_single_embedding():
    """Test that batch and single embeddings produce same results."""
    from api.embedding_service.model_manager import ModelManager
    import numpy as np

    logger.info("Testing batch vs single embedding consistency...")

    try:
        manager = ModelManager()

        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]

        # Get single embeddings
        single_embeddings = [manager.get_embedding(text) for text in texts]

        # Get batch embeddings
        batch_embeddings = manager.get_embeddings(texts)

        # Compare each pair
        for i, (single, batch) in enumerate(zip(single_embeddings, batch_embeddings)):
            similarity = np.dot(single, batch) / (np.linalg.norm(single) * np.linalg.norm(batch))
            logger.info(f"  Text {i}: similarity = {similarity:.6f}")
            assert similarity > 0.999, f"Embedding {i} mismatch: {similarity:.6f}"

        logger.info("Batch vs single embedding test passed")
        return True

    except Exception as e:
        logger.error(f"Batch vs single embedding test failed: {e}")
        return False


def test_openai_compatible_api_format():
    """Test that the API response format matches OpenAI specification."""
    from api.embedding_service.schemas import EmbeddingResponse, EmbeddingObject, UsageInfo

    logger.info("Testing OpenAI-compatible API format...")

    try:
        # Create a sample response
        response = EmbeddingResponse(
            data=[
                EmbeddingObject(
                    embedding=[0.1, 0.2, 0.3],
                    index=0
                )
            ],
            model="nomic-ai/nomic-embed-text-v1.5",
            usage=UsageInfo(
                prompt_tokens=10,
                total_tokens=10
            )
        )

        # Verify structure
        assert response.object == "list"
        assert len(response.data) == 1
        assert response.data[0].object == "embedding"
        assert response.data[0].index == 0
        assert response.model == "nomic-ai/nomic-embed-text-v1.5"
        assert response.usage.prompt_tokens == 10
        assert response.usage.total_tokens == 10

        # Verify JSON serialization
        json_data = response.model_dump()
        assert "object" in json_data
        assert "data" in json_data
        assert "model" in json_data
        assert "usage" in json_data

        logger.info("OpenAI-compatible API format test passed")
        return True

    except Exception as e:
        logger.error(f"OpenAI-compatible API format test failed: {e}")
        return False


def run_integration_tests():
    """Run all integration tests."""
    logger.info("=" * 60)
    logger.info("Running Nomic Integration Tests")
    logger.info("=" * 60)

    tests = [
        ("Embedding Consistency", test_embedding_consistency),
        ("Code Similarity Semantics", test_code_similarity_semantics),
        ("Batch vs Single Embedding", test_batch_vs_single_embedding),
        ("OpenAI-compatible API Format", test_openai_compatible_api_format),
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
    logger.info("Integration Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "PASS" if success else "FAIL"
        logger.info(f"{status} - {name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)