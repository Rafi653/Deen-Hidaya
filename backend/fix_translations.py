#!/usr/bin/env python3
"""
Script to fix missing translations (English and Telugu)
Re-scrapes data with correct translation IDs and re-ingests into database
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scrape_quran import QuranScraper
from ingest_data import QuranDataIngester
from database import SessionLocal
from models import Translation, Verse

def check_existing_translations():
    """Check current state of translations in database"""
    db = SessionLocal()
    try:
        total_translations = db.query(Translation).count()
        if total_translations > 0:
            # Get counts by language
            langs = db.query(Translation.language, Translation.translator).distinct().all()
            print(f"\nCurrent translations in database:")
            print(f"  Total: {total_translations}")
            print(f"  Languages/Translators:")
            for lang, translator in langs:
                count = db.query(Translation).filter(
                    Translation.language == lang,
                    Translation.translator == translator
                ).count()
                print(f"    - {lang} ({translator}): {count} verses")
        else:
            print("\nNo translations found in database")
        
        total_verses = db.query(Verse).count()
        print(f"  Total verses: {total_verses}")
        
        return total_translations, total_verses
    finally:
        db.close()


def fix_translations(start_surah=1, end_surah=114, force_rescrape=False):
    """
    Fix translations by re-scraping with both English and Telugu
    
    Args:
        start_surah: Starting surah number (default: 1)
        end_surah: Ending surah number (default: 114)
        force_rescrape: If True, re-scrape even if files exist
    """
    print("="*70)
    print("TRANSLATION FIX SCRIPT")
    print("="*70)
    
    # Check current state
    trans_count, verse_count = check_existing_translations()
    
    # Translation IDs
    # 131 = Dr. Mustafa Khattab (English)
    # 140 = Telugu translation
    translation_ids = [131, 140]
    
    print(f"\n{'='*70}")
    print(f"Re-scraping surahs {start_surah} to {end_surah}")
    print(f"Translation IDs: {translation_ids} (English + Telugu)")
    print(f"{'='*70}\n")
    
    # Initialize scraper
    scraper = QuranScraper()
    
    # Check if files exist
    data_dir = Path(__file__).resolve().parent.parent / "data" / "quran_text"
    
    if not force_rescrape:
        # Check first file
        first_file = data_dir / f"surah_{start_surah:03d}.json"
        if first_file.exists():
            import json
            with open(first_file, 'r') as f:
                data = json.load(f)
                existing_trans_count = len(data['verses'][0].get('translations', []))
                if existing_trans_count >= 2:
                    print(f"✓ Data files already have {existing_trans_count} translations")
                    print("  Use --force to re-scrape anyway")
                    scrape_needed = False
                else:
                    print(f"⚠ Data files only have {existing_trans_count} translation(s)")
                    print("  Re-scraping is needed")
                    scrape_needed = True
        else:
            scrape_needed = True
    else:
        scrape_needed = True
    
    # Scrape if needed
    if scrape_needed:
        print("\n--- Step 1: Scraping data with translations ---")
        stats = scraper.scrape_multiple_surahs(
            start=start_surah,
            end=end_surah,
            translation_ids=translation_ids,
            include_audio=True
        )
        
        if stats['failed'] > 0:
            print(f"\n⚠ Warning: {stats['failed']} surah(s) failed to scrape")
            if stats['successful'] == 0:
                print("✗ No surahs scraped successfully. Aborting.")
                return False
    else:
        print("\n--- Step 1: Skipping scrape (data exists) ---")
    
    # Ingest data
    print("\n--- Step 2: Ingesting data into database ---")
    ingester = QuranDataIngester()
    ingest_stats = ingester.ingest_multiple_surahs(
        start=start_surah,
        end=end_surah
    )
    
    if ingest_stats['failed'] > 0:
        print(f"\n⚠ Warning: {ingest_stats['failed']} surah(s) failed to ingest")
    
    # Check results
    print("\n--- Step 3: Verifying results ---")
    new_trans_count, new_verse_count = check_existing_translations()
    
    if new_trans_count > trans_count:
        print(f"\n✓ Success! Added {new_trans_count - trans_count} translations")
        print(f"  Total translations: {new_trans_count}")
        print(f"  Total verses: {new_verse_count}")
        
        # Calculate expected translations (2 per verse)
        expected = new_verse_count * 2
        if new_trans_count >= expected * 0.95:  # Allow 5% margin
            print(f"  ✓ Translation coverage is good ({new_trans_count}/{expected})")
        else:
            print(f"  ⚠ Expected ~{expected} translations but got {new_trans_count}")
    else:
        print(f"\n⚠ No new translations added. Current count: {new_trans_count}")
    
    print(f"\n{'='*70}")
    print("TRANSLATION FIX COMPLETE")
    print(f"{'='*70}\n")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix missing translations in database")
    parser.add_argument("--start", type=int, default=1, help="Starting surah number (default: 1)")
    parser.add_argument("--end", type=int, default=114, help="Ending surah number (default: 114)")
    parser.add_argument("--force", action="store_true", help="Force re-scrape even if files exist")
    
    args = parser.parse_args()
    
    # Validate surah numbers
    if not (1 <= args.start <= 114) or not (1 <= args.end <= 114):
        print("Error: Surah numbers must be between 1 and 114")
        return 1
    
    if args.start > args.end:
        print("Error: Start surah must be less than or equal to end surah")
        return 1
    
    # Run the fix
    success = fix_translations(
        start_surah=args.start,
        end_surah=args.end,
        force_rescrape=args.force
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
