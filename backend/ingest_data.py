"""
Quran Data Ingestion Module

This module reads scraped Quran JSON data and ingests it into the PostgreSQL database.
It handles upserts to avoid duplicate data and maintains data integrity.

Author: Deen Hidaya Backend Team
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
from models import Base, Surah, Verse, Translation, AudioTrack


class QuranDataIngester:
    """
    Ingests scraped Quran data into the database
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the ingester
        
        Args:
            data_dir: Directory containing scraped JSON files
        """
        if data_dir is None:
            # Default to /data/quran_text directory
            project_root = Path(__file__).resolve().parent.parent
            data_dir = project_root / "data" / "quran_text"
        
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {self.data_dir}")
    
    def load_surah_json(self, surah_number: int) -> Optional[Dict]:
        """
        Load scraped JSON data for a surah
        
        Args:
            surah_number: Surah number (1-114)
            
        Returns:
            Parsed JSON data or None if file doesn't exist
        """
        json_file = self.data_dir / f"surah_{surah_number:03d}.json"
        
        if not json_file.exists():
            print(f"Warning: JSON file not found for Surah {surah_number}: {json_file}")
            return None
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON for Surah {surah_number}: {e}")
            return None
    
    def upsert_surah_info(self, db: Session, surah_data: Dict) -> Optional[Surah]:
        """
        Insert or update surah metadata
        
        Args:
            db: Database session
            surah_data: Surah information from JSON
            
        Returns:
            Surah object or None on error
        """
        surah_info = surah_data.get("surah_info", {})
        surah_number = surah_data.get("metadata", {}).get("surah_number")
        
        if not surah_number or not surah_info:
            print(f"Error: Invalid surah data structure")
            return None
        
        try:
            # Check if surah already exists
            existing_surah = db.query(Surah).filter(Surah.number == surah_number).first()
            
            if existing_surah:
                # Update existing surah
                existing_surah.name_arabic = surah_info.get("name_arabic", existing_surah.name_arabic)
                existing_surah.name_english = surah_info.get("name_simple", existing_surah.name_english)
                existing_surah.name_transliteration = surah_info.get("name_complex", existing_surah.name_transliteration)
                existing_surah.revelation_place = surah_info.get("revelation_place", existing_surah.revelation_place)
                existing_surah.total_verses = surah_info.get("verses_count", existing_surah.total_verses)
                existing_surah.updated_at = datetime.utcnow()
                
                print(f"  Updated existing Surah {surah_number}: {existing_surah.name_english}")
                return existing_surah
            else:
                # Create new surah
                new_surah = Surah(
                    number=surah_number,
                    name_arabic=surah_info.get("name_arabic", ""),
                    name_english=surah_info.get("name_simple", ""),
                    name_transliteration=surah_info.get("name_complex", ""),
                    revelation_place=surah_info.get("revelation_place", ""),
                    total_verses=surah_info.get("verses_count", 0)
                )
                db.add(new_surah)
                db.flush()  # Get the ID without committing
                
                print(f"  Created new Surah {surah_number}: {new_surah.name_english}")
                return new_surah
                
        except Exception as e:
            print(f"Error upserting Surah {surah_number}: {e}")
            db.rollback()
            return None
    
    def upsert_verses(self, db: Session, surah: Surah, verses_data: List[Dict]) -> int:
        """
        Insert or update verses for a surah
        
        Args:
            db: Database session
            surah: Surah object
            verses_data: List of verse data from JSON
            
        Returns:
            Number of verses processed
        """
        verses_processed = 0
        
        for verse_data in verses_data:
            try:
                verse_number = verse_data.get("verse_number")
                if not verse_number:
                    continue
                
                # Check if verse already exists
                existing_verse = db.query(Verse).filter(
                    Verse.surah_id == surah.id,
                    Verse.verse_number == verse_number
                ).first()
                
                # Extract verse text (prioritize text_uthmani)
                text_arabic = verse_data.get("text_uthmani") or verse_data.get("text_imlaei", "")
                text_simple = verse_data.get("text_imlaei", "")
                
                if existing_verse:
                    # Update existing verse
                    existing_verse.text_arabic = text_arabic
                    existing_verse.text_simple = text_simple
                    existing_verse.juz_number = verse_data.get("juz_number")
                    existing_verse.hizb_number = verse_data.get("hizb_number")
                    existing_verse.rub_number = verse_data.get("rub_el_hizb_number")
                    existing_verse.updated_at = datetime.utcnow()
                    
                    verse_obj = existing_verse
                else:
                    # Create new verse
                    new_verse = Verse(
                        surah_id=surah.id,
                        verse_number=verse_number,
                        text_arabic=text_arabic,
                        text_simple=text_simple,
                        juz_number=verse_data.get("juz_number"),
                        hizb_number=verse_data.get("hizb_number"),
                        rub_number=verse_data.get("rub_el_hizb_number"),
                        sajda=False  # Default, would need additional data for sajda verses
                    )
                    db.add(new_verse)
                    db.flush()  # Get the ID
                    verse_obj = new_verse
                
                # Handle translations
                translations = verse_data.get("translations", [])
                if translations:
                    self.upsert_translations(db, verse_obj, translations)
                
                verses_processed += 1
                
            except Exception as e:
                print(f"  Error processing verse {verse_data.get('verse_number', '?')}: {e}")
                continue
        
        return verses_processed
    
    def upsert_translations(self, db: Session, verse: Verse, translations_data: List[Dict]):
        """
        Insert or update translations for a verse
        
        Args:
            db: Database session
            verse: Verse object
            translations_data: List of translation data from JSON
        """
        for trans_data in translations_data:
            try:
                resource_name = trans_data.get("resource_name", "")
                language_code = trans_data.get("language_name", "en")[:10]
                text = trans_data.get("text", "")
                
                if not text:
                    continue
                
                # Extract translator name from resource_name
                translator = resource_name if resource_name else "Unknown"
                
                # Check if translation already exists
                existing_translation = db.query(Translation).filter(
                    Translation.verse_id == verse.id,
                    Translation.language == language_code,
                    Translation.translator == translator
                ).first()
                
                if existing_translation:
                    # Update existing translation
                    existing_translation.text = text
                    existing_translation.updated_at = datetime.utcnow()
                else:
                    # Create new translation
                    new_translation = Translation(
                        verse_id=verse.id,
                        language=language_code,
                        translator=translator,
                        text=text
                    )
                    db.add(new_translation)
                
            except Exception as e:
                print(f"    Error processing translation: {e}")
                continue
    
    def upsert_audio_metadata(self, db: Session, surah: Surah, audio_data: Dict):
        """
        Insert or update audio metadata for a surah
        
        Args:
            db: Database session
            surah: Surah object
            audio_data: Audio metadata from JSON
        """
        if not audio_data:
            return
        
        try:
            audio_file = audio_data.get("audio_file")
            if not audio_file:
                return
            
            # Get audio file info
            audio_url = audio_file.get("audio_url", "")
            chapter_id = audio_file.get("chapter_id")
            
            # Get reciter info
            recitation = audio_data.get("recitation", {})
            reciter_name = recitation.get("reciter_name", "Unknown")
            
            if not audio_url or not chapter_id:
                return
            
            # For chapter-level audio, we create a single audio track entry
            # In a more complete implementation, we'd have verse-level audio
            
            # Get first verse of the surah to attach audio metadata
            first_verse = db.query(Verse).filter(
                Verse.surah_id == surah.id,
                Verse.verse_number == 1
            ).first()
            
            if not first_verse:
                return
            
            # Check if audio track already exists
            existing_audio = db.query(AudioTrack).filter(
                AudioTrack.verse_id == first_verse.id,
                AudioTrack.reciter == reciter_name
            ).first()
            
            if existing_audio:
                # Update existing audio track
                existing_audio.audio_url = audio_url
                existing_audio.updated_at = datetime.utcnow()
            else:
                # Create new audio track
                new_audio = AudioTrack(
                    verse_id=first_verse.id,
                    reciter=reciter_name,
                    audio_url=audio_url,
                    format="mp3",
                    quality="128kbps"
                )
                db.add(new_audio)
            
        except Exception as e:
            print(f"  Error processing audio metadata: {e}")
    
    def ingest_surah(self, surah_number: int, db: Session = None) -> bool:
        """
        Ingest a single surah from JSON into the database
        
        Args:
            surah_number: Surah number (1-114)
            db: Database session (optional, will create one if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            print(f"Ingesting Surah {surah_number}...")
            
            # Load JSON data
            surah_data = self.load_surah_json(surah_number)
            if not surah_data:
                return False
            
            # Upsert surah info
            surah = self.upsert_surah_info(db, surah_data)
            if not surah:
                return False
            
            # Upsert verses
            verses_data = surah_data.get("verses", [])
            verses_count = self.upsert_verses(db, surah, verses_data)
            print(f"  Processed {verses_count} verses")
            
            # Upsert audio metadata
            audio_data = surah_data.get("audio_metadata")
            if audio_data:
                self.upsert_audio_metadata(db, surah, audio_data)
                print(f"  Added audio metadata")
            
            # Commit transaction
            db.commit()
            print(f"✓ Successfully ingested Surah {surah_number}")
            return True
            
        except Exception as e:
            print(f"✗ Error ingesting Surah {surah_number}: {e}")
            db.rollback()
            return False
        finally:
            if close_db:
                db.close()
    
    def ingest_multiple_surahs(self, start: int = 1, end: int = 5) -> Dict[str, Any]:
        """
        Ingest multiple surahs from JSON files
        
        Args:
            start: Starting surah number
            end: Ending surah number (inclusive)
            
        Returns:
            Dictionary with ingestion statistics
        """
        print(f"\n{'='*60}")
        print(f"Starting Quran Data Ingestion")
        print(f"Surahs: {start} to {end}")
        print(f"Data directory: {self.data_dir}")
        print(f"{'='*60}\n")
        
        db = SessionLocal()
        successful = []
        failed = []
        
        try:
            for surah_num in range(start, end + 1):
                if self.ingest_surah(surah_num, db=db):
                    successful.append(surah_num)
                else:
                    failed.append(surah_num)
                print()  # Blank line between surahs
            
            stats = {
                "total_attempted": end - start + 1,
                "successful": len(successful),
                "failed": len(failed),
                "successful_surahs": successful,
                "failed_surahs": failed,
                "ingested_at": datetime.utcnow().isoformat()
            }
            
            print(f"{'='*60}")
            print(f"Ingestion Complete!")
            print(f"Successful: {stats['successful']}/{stats['total_attempted']}")
            if failed:
                print(f"Failed: {failed}")
            print(f"{'='*60}\n")
            
            return stats
            
        finally:
            db.close()


def main():
    """Main function to run the ingester"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest scraped Quran data into database")
    parser.add_argument("--start", type=int, default=1, help="Starting surah number (default: 1)")
    parser.add_argument("--end", type=int, default=5, help="Ending surah number (default: 5)")
    parser.add_argument("--data-dir", type=str, help="Directory containing scraped JSON files")
    
    args = parser.parse_args()
    
    # Validate surah numbers
    if not (1 <= args.start <= 114) or not (1 <= args.end <= 114):
        print("Error: Surah numbers must be between 1 and 114")
        return 1
    
    if args.start > args.end:
        print("Error: Start surah must be less than or equal to end surah")
        return 1
    
    # Create ingester and run
    try:
        ingester = QuranDataIngester(data_dir=args.data_dir)
        stats = ingester.ingest_multiple_surahs(start=args.start, end=args.end)
        
        # Save stats
        stats_file = ingester.data_dir / "ingestion_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"Statistics saved to: {stats_file}")
        
        return 0 if stats["failed"] == 0 else 1
        
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
