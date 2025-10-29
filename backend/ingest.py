#!/usr/bin/env python3
"""
Quran Data Ingestion Script

This script ingests scraped Quran data from JSON files into the PostgreSQL database.
It performs upsert operations to handle updates and avoid duplicates.

Usage:
    python ingest.py --surahs 1-5
    python ingest.py --all
    python ingest.py --init  # Initialize database tables first
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
import argparse
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import SessionLocal, init_db, test_connection, engine
from models import Surah, Verse, Translation, AudioTrack, DataSource


class QuranIngestor:
    """Ingest Quran data from JSON files into PostgreSQL."""
    
    DATA_DIR = Path(__file__).parent.parent / "data" / "quran_text"
    
    def __init__(self):
        """Initialize the ingestor."""
        self.session: Session = SessionLocal()
        self.stats = {
            "surahs": 0,
            "verses": 0,
            "translations": 0,
            "audio_tracks": 0,
            "errors": 0
        }
    
    def close(self):
        """Close the database session."""
        self.session.close()
    
    def load_surah_json(self, surah_number: int) -> Dict:
        """
        Load surah data from JSON file.
        
        Args:
            surah_number: Surah number (1-114)
        
        Returns:
            Dictionary containing surah data
        """
        filename = self.DATA_DIR / f"surah_{surah_number:03d}.json"
        
        if not filename.exists():
            print(f"  ✗ File not found: {filename}")
            return {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"  ✗ Error loading {filename}: {e}")
            return {}
    
    def ingest_surah(self, surah_number: int) -> bool:
        """
        Ingest a single surah into the database.
        
        Args:
            surah_number: Surah number to ingest
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n--- Ingesting Surah {surah_number} ---")
        
        # Load JSON data
        data = self.load_surah_json(surah_number)
        if not data:
            self.stats["errors"] += 1
            return False
        
        try:
            surah_data = data.get("surah", {})
            verses_data = data.get("verses", [])
            audio_data = data.get("audio", {})
            metadata = data.get("metadata", {})
            
            # Upsert surah
            surah = self.session.query(Surah).filter_by(number=surah_data["number"]).first()
            
            if surah:
                print(f"  ↻ Updating existing Surah {surah_number}")
                # Update existing surah
                surah.name_arabic = surah_data.get("name_arabic")
                surah.name_simple = surah_data.get("name_simple")
                surah.name_complex = surah_data.get("name_complex")
                surah.revelation_place = surah_data.get("revelation_place")
                surah.revelation_order = surah_data.get("revelation_order")
                surah.verses_count = surah_data.get("verses_count")
                surah.pages = surah_data.get("pages")
            else:
                print(f"  ✓ Creating new Surah {surah_number}")
                # Create new surah
                surah = Surah(
                    number=surah_data["number"],
                    name_arabic=surah_data.get("name_arabic"),
                    name_simple=surah_data.get("name_simple"),
                    name_complex=surah_data.get("name_complex"),
                    revelation_place=surah_data.get("revelation_place"),
                    revelation_order=surah_data.get("revelation_order"),
                    verses_count=surah_data.get("verses_count"),
                    pages=surah_data.get("pages")
                )
                self.session.add(surah)
                self.stats["surahs"] += 1
            
            # Commit surah to get ID
            self.session.commit()
            
            # Delete existing verses for this surah (cascade will handle translations)
            self.session.query(Verse).filter_by(surah_id=surah.id).delete()
            self.session.commit()
            
            # Insert verses
            for verse_data in verses_data:
                verse = Verse(
                    surah_id=surah.id,
                    verse_number=verse_data["verse_number"],
                    verse_key=verse_data["verse_key"],
                    juz_number=verse_data.get("juz_number"),
                    hizb_number=verse_data.get("hizb_number"),
                    rub_number=verse_data.get("rub_number"),
                    text_uthmani=verse_data["text_uthmani"],
                    text_imlaei=verse_data.get("text_imlaei"),
                    text_simple=verse_data.get("text_simple")
                )
                self.session.add(verse)
                self.session.flush()  # Get verse ID
                
                self.stats["verses"] += 1
                
                # Insert translations
                for trans_data in verse_data.get("translations", []):
                    translation = Translation(
                        verse_id=verse.id,
                        resource_id=trans_data.get("id"),
                        text=trans_data["text"],
                        language=trans_data.get("language", "english")
                    )
                    self.session.add(translation)
                    self.stats["translations"] += 1
            
            # Delete existing audio tracks for this surah
            self.session.query(AudioTrack).filter_by(surah_id=surah.id).delete()
            
            # Insert audio track if available
            if audio_data and audio_data.get("audio_url"):
                audio_track = AudioTrack(
                    surah_id=surah.id,
                    reciter=audio_data.get("reciter", "Unknown"),
                    reciter_id=audio_data.get("reciter_id"),
                    audio_url=audio_data["audio_url"],
                    format=audio_data.get("format", "mp3"),
                    license_info=audio_data.get("license")
                )
                self.session.add(audio_track)
                self.stats["audio_tracks"] += 1
            
            # Store data source information
            if metadata:
                # Check if data source already exists
                existing_source = self.session.query(DataSource).filter_by(
                    source_name=metadata.get("source", "Unknown")
                ).first()
                
                if not existing_source:
                    data_source = DataSource(
                        source_name=metadata.get("source", "Unknown"),
                        license_text=str(metadata.get("license", {})),
                        data_type="quran_text",
                        scraped_at=metadata.get("scraped_at"),
                        source_metadata=metadata
                    )
                    self.session.add(data_source)
            
            # Commit all changes
            self.session.commit()
            
            print(f"  ✓ Successfully ingested Surah {surah_number} " +
                  f"({len(verses_data)} verses)")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error ingesting Surah {surah_number}: {e}")
            self.session.rollback()
            self.stats["errors"] += 1
            return False
    
    def ingest_range(self, start: int, end: int) -> int:
        """
        Ingest a range of surahs.
        
        Args:
            start: Starting surah number
            end: Ending surah number
        
        Returns:
            Number of successfully ingested surahs
        """
        print(f"\n{'='*60}")
        print(f"Ingesting Surahs {start} to {end}")
        print(f"{'='*60}")
        
        success_count = 0
        
        for surah_num in range(start, end + 1):
            if self.ingest_surah(surah_num):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Ingestion Summary:")
        print(f"  Surahs: {self.stats['surahs']}")
        print(f"  Verses: {self.stats['verses']}")
        print(f"  Translations: {self.stats['translations']}")
        print(f"  Audio Tracks: {self.stats['audio_tracks']}")
        print(f"  Errors: {self.stats['errors']}")
        print(f"Successfully ingested {success_count}/{end - start + 1} surahs")
        print(f"{'='*60}\n")
        
        return success_count
    
    def verify_ingestion(self, start: int, end: int):
        """
        Verify that data was ingested correctly.
        
        Args:
            start: Starting surah number
            end: Ending surah number
        """
        print("\n--- Verification ---")
        
        for surah_num in range(start, end + 1):
            surah = self.session.query(Surah).filter_by(number=surah_num).first()
            if surah:
                verses_count = self.session.query(Verse).filter_by(surah_id=surah.id).count()
                print(f"  ✓ Surah {surah_num} ({surah.name_simple}): {verses_count} verses")
            else:
                print(f"  ✗ Surah {surah_num}: Not found in database")
        
        print()


def main():
    """Main entry point for the ingestor."""
    parser = argparse.ArgumentParser(
        description="Ingest Quran data from JSON files into PostgreSQL"
    )
    parser.add_argument(
        "--surahs",
        type=str,
        default="1-5",
        help="Surah range to ingest (e.g., '1-5' or '1-114')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ingest all 114 surahs"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize database tables before ingestion"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify ingestion after completion"
    )
    
    args = parser.parse_args()
    
    # Test database connection
    print("Testing database connection...")
    if not test_connection():
        print("\n✗ Cannot connect to database. Please check:")
        print("  1. PostgreSQL is running (docker-compose up postgres)")
        print("  2. Environment variables are set correctly")
        print("  3. Database credentials are correct")
        return 1
    
    # Initialize database if requested
    if args.init:
        print("\nInitializing database tables...")
        init_db()
    
    # Parse surah range
    if args.all:
        start, end = 1, 114
    else:
        try:
            start, end = map(int, args.surahs.split("-"))
        except ValueError:
            print("Invalid surah range format. Use '1-5' or '1-114'")
            return 1
    
    # Validate range
    if not (1 <= start <= 114 and 1 <= end <= 114 and start <= end):
        print("Invalid surah range. Must be between 1 and 114")
        return 1
    
    # Run ingestor
    ingestor = QuranIngestor()
    try:
        success_count = ingestor.ingest_range(start, end)
        
        # Verify if requested
        if args.verify:
            ingestor.verify_ingestion(start, end)
        
        return 0 if success_count > 0 else 1
    finally:
        ingestor.close()


if __name__ == "__main__":
    sys.exit(main())
