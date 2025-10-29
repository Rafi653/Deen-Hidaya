#!/usr/bin/env python3
"""
Test script for new search and embedding implementations

Tests:
1. Embedding service with multiple backends
2. Search utilities with different methods
3. Performance comparisons
"""
import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import SessionLocal
from embedding_service_v2 import EmbeddingServiceV2
from search_utils_v2 import unified_search, fulltext_search, semantic_search, exact_search
from models import Verse


def test_embedding_service():
    """Test embedding service initialization and embedding generation"""
    print("=" * 70)
    print("Testing Embedding Service")
    print("=" * 70)
    
    # Test auto-detection
    print("\n1. Testing auto-detection...")
    service = EmbeddingServiceV2()
    print(f"   Backend: {service.backend_name}")
    print(f"   Model: {service.model_name}")
    print(f"   Dimension: {service.dimension}")
    print(f"   Enabled: {service.is_enabled}")
    
    if service.is_enabled:
        # Test single embedding
        print("\n2. Testing single embedding generation...")
        test_text = "And We will surely test you with something of fear and hunger"
        start = time.time()
        embedding = service.generate_embedding(test_text)
        elapsed = time.time() - start
        
        if embedding:
            print(f"   ✓ Generated embedding in {elapsed:.3f}s")
            print(f"   ✓ Dimension: {len(embedding)}")
            print(f"   ✓ First 5 values: {embedding[:5]}")
        else:
            print("   ✗ Failed to generate embedding")
        
        # Test batch embeddings
        print("\n3. Testing batch embedding generation...")
        test_texts = [
            "patience and gratitude",
            "prayer and charity",
            "mercy and forgiveness"
        ]
        start = time.time()
        embeddings = service.generate_embeddings_batch(test_texts)
        elapsed = time.time() - start
        
        print(f"   ✓ Generated {len(embeddings)} embeddings in {elapsed:.3f}s")
        print(f"   ✓ Speed: {len(embeddings)/elapsed:.1f} embeddings/sec")
    else:
        print("\n   ℹ Embeddings disabled - this is OK for FTS-only setup")
    
    return service


def test_search_methods(db):
    """Test different search methods"""
    print("\n" + "=" * 70)
    print("Testing Search Methods")
    print("=" * 70)
    
    # Count verses in database
    verse_count = db.query(Verse).count()
    print(f"\nDatabase contains {verse_count} verses")
    
    if verse_count == 0:
        print("⚠ No verses in database. Please run ingest_data.py first.")
        return
    
    # Test queries
    test_queries = [
        ("patience", "exact"),
        ("patience and faith", "fulltext"),
        ("what does quran say about prayer", "auto"),
    ]
    
    for query, search_type in test_queries:
        print(f"\n{'─' * 70}")
        print(f"Query: '{query}' (type: {search_type})")
        print('─' * 70)
        
        start = time.time()
        results = unified_search(db, query, language="en", search_type=search_type, limit=5)
        elapsed = time.time() - start
        
        print(f"Found {len(results)} results in {elapsed:.3f}s")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. Surah {result.surah_number}:{result.verse_number} - {result.surah_name}")
            print(f"   Score: {result.score:.3f} | Type: {result.match_type}")
            if result.translations:
                trans_text = result.translations[0].text
                preview = trans_text[:100] + "..." if len(trans_text) > 100 else trans_text
                print(f"   {preview}")


def test_performance_comparison(db):
    """Compare performance of different search methods"""
    print("\n" + "=" * 70)
    print("Performance Comparison")
    print("=" * 70)
    
    verse_count = db.query(Verse).count()
    if verse_count == 0:
        print("⚠ No verses in database. Skipping performance tests.")
        return
    
    query = "patience"
    
    # Test exact search
    print(f"\nQuery: '{query}'")
    print("─" * 70)
    
    methods = [
        ("Exact Search", lambda: exact_search(db, query, limit=10)),
        ("Full-Text Search", lambda: fulltext_search(db, query, limit=10)),
    ]
    
    # Add semantic search if embeddings are available
    embedding_service = EmbeddingServiceV2()
    if embedding_service.is_enabled:
        methods.append(
            ("Semantic Search", lambda: semantic_search(db, query, limit=10))
        )
    
    for method_name, method_func in methods:
        times = []
        for _ in range(3):
            start = time.time()
            results = method_func()
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        result_count = len(results) if results else 0
        
        print(f"{method_name:20s}: {avg_time*1000:6.1f}ms avg | {result_count:2d} results")


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("NEW SEARCH & EMBEDDING TEST SUITE")
    print("=" * 70)
    
    # Check environment
    print("\nEnvironment Configuration:")
    print(f"  EMBEDDING_BACKEND: {os.getenv('EMBEDDING_BACKEND', 'auto')}")
    print(f"  EMBEDDING_MODEL: {os.getenv('EMBEDDING_MODEL', 'default')}")
    print(f"  ENABLE_SEMANTIC_SEARCH: {os.getenv('ENABLE_SEMANTIC_SEARCH', 'false')}")
    
    # Test embedding service
    embedding_service = test_embedding_service()
    
    # Test search methods
    db = SessionLocal()
    try:
        test_search_methods(db)
        test_performance_comparison(db)
    finally:
        db.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"✓ Embedding Backend: {embedding_service.backend_name}")
    print(f"✓ Search Methods: Available")
    print("\nRecommendations:")
    
    if not embedding_service.is_enabled:
        print("  • Embeddings disabled - using full-text search only")
        print("  • To enable semantic search:")
        print("    1. pip install sentence-transformers")
        print("    2. export EMBEDDING_BACKEND=sentence-transformers")
        print("    3. python fix_embeddings.py")
    else:
        print(f"  • Using {embedding_service.backend_name} for embeddings")
        print("  • Run fix_embeddings.py to generate embeddings for all verses")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
