#!/usr/bin/env python3
"""
Script to fix missing embeddings for Q&A functionality
Generates embeddings for verses using local SBERT or OpenAI API
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import SessionLocal
from models import Verse, Embedding, Translation
from embeddings.unified_service import UnifiedEmbeddingService


def check_embedding_backend():
    """Check which embedding backend is available and configured"""
    backend = os.getenv("EMBEDDING_BACKEND", "auto").lower()
    
    print(f"\nEmbedding backend: {backend}")
    
    # Check for SBERT (preferred)
    try:
        import sentence_transformers
        print("✓ sentence-transformers is installed (local embedding backend available)")
        has_sbert = True
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Install with: pip install sentence-transformers")
        has_sbert = False
    
    # Check for OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("sk-"):
            print(f"✓ OPENAI_API_KEY is configured (length: {len(api_key)} characters)")
            has_openai = True
        else:
            print(f"⚠ WARNING: OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
            has_openai = True
    else:
        print("✗ OPENAI_API_KEY not set")
        has_openai = False
    
    # Determine what will be used
    if backend == "sbert":
        if not has_sbert:
            print("\n⚠ ERROR: SBERT backend requested but sentence-transformers not installed!")
            return None
        print("\n✓ Will use SBERT (local) backend")
        return "sbert"
    elif backend == "openai":
        if not has_openai:
            print("\n⚠ ERROR: OpenAI backend requested but OPENAI_API_KEY not set!")
            return None
        print("\n✓ Will use OpenAI backend")
        return "openai"
    elif backend == "disabled":
        print("\n⚠ Embedding backend is disabled")
        return None
    else:  # auto
        if has_sbert:
            print("\n✓ Will use SBERT (local) backend (preferred)")
            return "sbert"
        elif has_openai:
            print("\n✓ Will use OpenAI backend (fallback)")
            return "openai"
        else:
            print("\n⚠ ERROR: No embedding backend available!")
            print("\nTo fix this, either:")
            print("1. Install sentence-transformers: pip install sentence-transformers")
            print("2. Or set OPENAI_API_KEY in your .env file")
            return None


def check_existing_embeddings():
    """Check current state of embeddings in database"""
    db = SessionLocal()
    try:
        total_embeddings = db.query(Embedding).count()
        total_verses = db.query(Verse).count()
        
        print(f"\nCurrent embeddings in database:")
        print(f"  Total embeddings: {total_embeddings}")
        print(f"  Total verses: {total_verses}")
        
        if total_embeddings > 0:
            # Get counts by language
            langs = db.query(Embedding.language, Embedding.model).distinct().all()
            print(f"  Languages/Models:")
            for lang, model in langs:
                count = db.query(Embedding).filter(
                    Embedding.language == lang,
                    Embedding.model == model
                ).count()
                print(f"    - {lang} ({model}): {count} embeddings")
        
        # Check translation availability
        total_translations = db.query(Translation).count()
        print(f"\n  Total translations: {total_translations}")
        
        if total_translations == 0:
            print("\n  ⚠ WARNING: No translations found!")
            print("    You need to fix translations first before generating embeddings.")
            print("    Run: python fix_translations.py")
        
        return total_embeddings, total_verses, total_translations
    finally:
        db.close()


def generate_embeddings(language="en", batch_size=100, start_verse_id=None, max_verses=None):
    """
    Generate embeddings for verses
    
    Args:
        language: Language code for translations (default: "en")
        batch_size: Number of verses to process in each batch
        start_verse_id: Optional starting verse ID (for resuming)
        max_verses: Optional maximum number of verses to process
    """
    print("="*70)
    print("EMBEDDING GENERATION SCRIPT")
    print("="*70)
    
    # Check embedding backend
    backend = check_embedding_backend()
    if not backend:
        return False
    
    # Check current state
    emb_count, verse_count, trans_count = check_existing_embeddings()
    
    if trans_count == 0:
        print("\n✗ Cannot generate embeddings without translations")
        print("  Please run fix_translations.py first")
        return False
    
    print(f"\n{'='*70}")
    print(f"Generating embeddings for {language} translations")
    print(f"Batch size: {batch_size}")
    if start_verse_id:
        print(f"Starting from verse ID: {start_verse_id}")
    if max_verses:
        print(f"Maximum verses to process: {max_verses}")
    print(f"{'='*70}\n")
    
    # Initialize embedding service
    service = UnifiedEmbeddingService(backend=backend)
    
    if not service.client:
        print("✗ Failed to initialize embedding service")
        return False
    
    # Test embedding generation
    print("Testing embedding generation...")
    test_embedding = service.generate_embedding("test")
    if test_embedding is None:
        print("✗ Failed to generate test embedding")
        return False
    print(f"✓ Embedding generation successful (dimension: {len(test_embedding)}, model: {service.model})")
    
    # Get verses to process
    db = SessionLocal()
    try:
        # Get verses that need embeddings
        query = db.query(Verse.id)
        
        if start_verse_id:
            query = query.filter(Verse.id >= start_verse_id)
        
        query = query.order_by(Verse.id)
        
        if max_verses:
            query = query.limit(max_verses)
        
        verse_ids_query = query.all()
        verse_ids = [v.id for v in verse_ids_query]
        
        if not verse_ids:
            print("✓ No verses found to process")
            return True
        
        print(f"\nProcessing {len(verse_ids)} verses...")
        print(f"Verse IDs: {verse_ids[0]} to {verse_ids[-1]}")
        
        # Filter out verses that already have embeddings
        existing_embeddings = db.query(Embedding.verse_id).filter(
            Embedding.verse_id.in_(verse_ids),
            Embedding.language == language
        ).all()
        existing_verse_ids = {e.verse_id for e in existing_embeddings}
        
        verses_to_process = [vid for vid in verse_ids if vid not in existing_verse_ids]
        
        if existing_verse_ids:
            print(f"  {len(existing_verse_ids)} verses already have embeddings (skipping)")
        
        if not verses_to_process:
            print("✓ All verses already have embeddings!")
            return True
        
        print(f"  {len(verses_to_process)} verses need embeddings")
        print(f"\nStarting batch processing...")
        
        # Process in batches
        total_success = 0
        total_errors = 0
        
        for i in range(0, len(verses_to_process), batch_size):
            batch = verses_to_process[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(verses_to_process) + batch_size - 1) // batch_size
            
            print(f"\nBatch {batch_num}/{total_batches} (verses {batch[0]}-{batch[-1]})")
            
            result = service.create_embeddings_batch(
                verse_ids=batch,
                language=language,
                db=db
            )
            
            total_success += result['success']
            total_errors += result['errors']
            
            print(f"  Success: {result['success']}, Errors: {result['errors']}")
            
            # Show progress
            progress = ((i + len(batch)) / len(verses_to_process)) * 100
            print(f"  Overall progress: {progress:.1f}%")
        
        # Final results
        print(f"\n{'='*70}")
        print("EMBEDDING GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"Successfully generated: {total_success} embeddings")
        print(f"Errors: {total_errors}")
        print(f"Total verses with embeddings: {emb_count + total_success}")
        
        if total_errors == 0:
            print("\n✓ All embeddings generated successfully!")
        else:
            print(f"\n⚠ {total_errors} embeddings failed to generate")
            print("  You can re-run this script to retry failed verses")
        
        return total_errors == 0
        
    finally:
        db.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for Q&A functionality")
    parser.add_argument("--language", type=str, default="en", 
                       help="Language code for translations (default: en)")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Number of verses to process in each batch (default: 100)")
    parser.add_argument("--start-verse", type=int, default=None,
                       help="Starting verse ID (for resuming)")
    parser.add_argument("--max-verses", type=int, default=None,
                       help="Maximum number of verses to process")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check current state, don't generate embeddings")
    
    args = parser.parse_args()
    
    if args.check_only:
        check_embedding_backend()
        check_existing_embeddings()
        return 0
    
    # Generate embeddings
    success = generate_embeddings(
        language=args.language,
        batch_size=args.batch_size,
        start_verse_id=args.start_verse,
        max_verses=args.max_verses
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
