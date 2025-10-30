#!/usr/bin/env python3
"""
Demo script showing how to use the local embedding backend (SBERT + FAISS)
This demonstrates embedding generation and FAISS index usage without requiring OpenAI
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import numpy as np
from embeddings.sbert_faiss import EmbeddingServiceSBERT


def demo_basic_embeddings():
    """Demonstrate basic embedding generation"""
    print("="*70)
    print("DEMO: Basic Embedding Generation")
    print("="*70)
    
    # Initialize SBERT service
    print("\n1. Initializing SBERT service...")
    service = EmbeddingServiceSBERT()
    print(f"   Model: {service.model_name}")
    print(f"   Dimension: {service.dimension}")
    
    # Generate embeddings for sample texts
    print("\n2. Generating embeddings for sample Quran verses...")
    sample_texts = [
        "In the name of Allah, the Most Gracious, the Most Merciful",
        "All praise is due to Allah, Lord of the Worlds",
        "The Most Gracious, the Most Merciful",
        "Master of the Day of Judgment",
        "You alone we worship, and You alone we ask for help"
    ]
    
    embeddings = service.generate_embeddings(sample_texts)
    print(f"   Generated {len(embeddings)} embeddings")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    
    # Check normalization (for cosine similarity)
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"   Vector norms (should be ~1.0): {norms}")
    
    return service, embeddings, sample_texts


def demo_faiss_index(service, embeddings, texts):
    """Demonstrate FAISS index creation and search"""
    print("\n" + "="*70)
    print("DEMO: FAISS Index and Search")
    print("="*70)
    
    # Build FAISS index
    print("\n1. Building FAISS index...")
    index = service.build_faiss_index(embeddings)
    print(f"   Index type: {type(index)}")
    print(f"   Total vectors: {index.ntotal}")
    
    # Search for similar verses
    print("\n2. Searching for verses similar to a query...")
    query = "Praise be to God"
    print(f"   Query: '{query}'")
    
    query_embedding = service.generate_embeddings([query])[0]
    distances, indices = service.search(index, query_embedding, k=3)
    
    print(f"\n   Top 3 results:")
    for i, (dist, idx) in enumerate(zip(distances, indices), 1):
        print(f"   {i}. Distance: {dist:.4f} | {texts[idx]}")
    
    # Save and load index
    print("\n3. Saving and loading FAISS index...")
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".faiss") as f:
        index_path = f.name
    
    service.save_index(index, index_path)
    print(f"   Saved to: {index_path}")
    
    loaded_index = service.load_index(index_path)
    print(f"   Loaded index with {loaded_index.ntotal} vectors")
    
    # Clean up
    os.unlink(index_path)
    
    return index


def demo_multilingual():
    """Demonstrate multilingual support"""
    print("\n" + "="*70)
    print("DEMO: Multilingual Support")
    print("="*70)
    
    print("\n1. Testing Arabic text embedding...")
    service = EmbeddingServiceSBERT()
    
    arabic_texts = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",  # Bismillah
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",  # Alhamdulillah
    ]
    
    arabic_embeddings = service.generate_embeddings(arabic_texts)
    print(f"   Generated {len(arabic_embeddings)} Arabic embeddings")
    print(f"   Shape: {arabic_embeddings.shape}")
    
    # Compare with English
    english_texts = [
        "In the name of Allah, the Most Gracious, the Most Merciful",
        "All praise is due to Allah, Lord of the Worlds",
    ]
    
    english_embeddings = service.generate_embeddings(english_texts)
    
    # Calculate similarity between Arabic and English translations
    print("\n2. Comparing Arabic and English embeddings...")
    for i in range(len(arabic_texts)):
        # Cosine similarity = dot product (since vectors are normalized)
        similarity = np.dot(arabic_embeddings[i], english_embeddings[i])
        print(f"   Verse {i+1} similarity: {similarity:.4f}")
        print(f"      Arabic:  {arabic_texts[i][:50]}...")
        print(f"      English: {english_texts[i][:50]}...")


def demo_batch_performance():
    """Demonstrate batch processing performance"""
    print("\n" + "="*70)
    print("DEMO: Batch Processing Performance")
    print("="*70)
    
    import time
    
    service = EmbeddingServiceSBERT()
    
    # Generate sample texts
    sample_texts = [f"Sample verse number {i}" for i in range(100)]
    
    # Batch processing
    print("\n1. Processing 100 texts in batch...")
    start = time.time()
    embeddings = service.generate_embeddings(sample_texts)
    batch_time = time.time() - start
    print(f"   Time: {batch_time:.2f} seconds")
    print(f"   Throughput: {len(sample_texts) / batch_time:.1f} texts/second")
    
    # One-by-one processing
    print("\n2. Processing 10 texts one-by-one (for comparison)...")
    start = time.time()
    for text in sample_texts[:10]:
        service.generate_embedding(text)
    single_time = time.time() - start
    print(f"   Time: {single_time:.2f} seconds")
    print(f"   Throughput: {10 / single_time:.1f} texts/second")
    
    speedup = (single_time * 10) / batch_time
    print(f"\n   Batch processing is ~{speedup:.1f}x faster!")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("LOCAL EMBEDDING BACKEND DEMO")
    print("Using Sentence-Transformers + FAISS")
    print("="*70)
    
    try:
        # Check if sentence-transformers is installed
        try:
            import sentence_transformers
            print("✓ sentence-transformers is installed")
        except ImportError:
            print("✗ sentence-transformers not installed")
            print("\nPlease install with:")
            print("  pip install sentence-transformers")
            return 1
        
        # Check if faiss is installed
        try:
            import faiss
            print("✓ faiss-cpu is installed")
        except ImportError:
            print("✗ faiss-cpu not installed")
            print("\nPlease install with:")
            print("  pip install faiss-cpu")
            return 1
        
        # Run demos
        service, embeddings, texts = demo_basic_embeddings()
        demo_faiss_index(service, embeddings, texts)
        demo_multilingual()
        demo_batch_performance()
        
        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print("\nKey takeaways:")
        print("- Local embeddings work without any API keys")
        print("- Supports multilingual text (English, Arabic, etc.)")
        print("- FAISS enables fast similarity search")
        print("- Batch processing is much faster than one-by-one")
        print("- Embeddings are float32 and normalized for cosine similarity")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
