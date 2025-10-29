"""
Quran Data Scraping Module

This module fetches Quran text, translations, and audio metadata from verified APIs
and stores them in structured JSON format with proper license metadata.

Data Sources:
- api.quran.com - Quran text, translations, and audio recitations
  License: The Quran API is free to use for non-commercial purposes.
  The Quran text is in the public domain.

Author: Deen Hidaya Backend Team
"""

import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class QuranScraper:
    """
    Scraper for Quran text and metadata from api.quran.com
    """
    
    BASE_URL = "https://api.quran.com/api/v4"
    
    # Default editions
    DEFAULT_TEXT_EDITION = "quran-uthmani"  # Uthmani script with diacritics
    # Translation IDs - can be configured for different languages
    # Common translation IDs from api.quran.com:
    # English: 131 (Dr. Mustafa Khattab), 20 (Sahih International), 85 (Pickthall)
    # Telugu: 213 (Abdul Hafeez & Mohammed Abdul Haq)
    # Spanish: 140 (Muhammad Isa Garcia)
    # Urdu: 97 (Abul A'ala Maududi), 151 (Ahmed Ali)
    DEFAULT_TRANSLATIONS = [131, 213]  # English and Telugu as defaults
    
    # Translation metadata - maps translation ID to metadata
    TRANSLATION_METADATA = {
        131: {
            "name": "Dr. Mustafa Khattab, The Clear Quran",
            "author": "Dr. Mustafa Khattab",
            "language": "en",
            "language_name": "English",
            "license": "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0",
            "source": "api.quran.com"
        },
        20: {
            "name": "Saheeh International",
            "author": "Saheeh International",
            "language": "en",
            "language_name": "English",
            "license": "Public Domain",
            "source": "api.quran.com"
        },
        140: {
            "name": "Muhammad Isa Garcia",
            "author": "Muhammad Isa Garcia", 
            "language": "es",
            "language_name": "Spanish",
            "license": "Public Domain",
            "source": "api.quran.com"
        },
        213: {
            "name": "Abdul Hafeez & Mohammed Abdul Haq",
            "author": "Abdul Hafeez, Mohammed Abdul Haq", 
            "language": "te",
            "language_name": "Telugu",
            "license": "Various",
            "source": "api.quran.com"
        }
    }
    
    # License information
    LICENSE_INFO = {
        "quran_text": {
            "source": "api.quran.com",
            "license": "Public Domain",
            "attribution": "The Quran text is in the public domain",
            "terms_url": "https://quran.com/terms",
            "fetched_at": None
        },
        "translations": {
            "source": "api.quran.com",
            "license": "Various - See individual translation licenses",
            "attribution": "Translation copyrights belong to respective translators",
            "terms_url": "https://quran.com/terms",
            "fetched_at": None
        },
        "audio": {
            "source": "everyayah.com via api.quran.com",
            "license": "Free for non-commercial use",
            "attribution": "Audio recitations courtesy of everyayah.com",
            "terms_url": "https://everyayah.com/",
            "note": "Audio URLs provided - not downloaded locally due to size",
            "fetched_at": None
        }
    }
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the scraper
        
        Args:
            output_dir: Base directory for storing scraped data
        """
        if output_dir is None:
            # Default to /data directory in project root
            project_root = Path(__file__).resolve().parent.parent
            output_dir = project_root / "data"
        
        self.output_dir = Path(output_dir)
        self.quran_text_dir = self.output_dir / "quran_text"
        self.audio_metadata_dir = self.output_dir / "audio_metadata"
        
        # Create directories
        self.quran_text_dir.mkdir(parents=True, exist_ok=True)
        self.audio_metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Deen-Hidaya/1.0 (Educational Islamic Platform)"
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response JSON or None on error
        """
        url = f"{self.BASE_URL}/{endpoint}"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
    
    def fetch_surah_info(self, surah_number: int) -> Optional[Dict]:
        """
        Fetch basic information about a surah
        
        Args:
            surah_number: Surah number (1-114)
            
        Returns:
            Surah metadata or None
        """
        endpoint = f"chapters/{surah_number}"
        result = self._make_request(endpoint)
        
        if result and "chapter" in result:
            return result["chapter"]
        return None
    
    def fetch_surah_verses(self, surah_number: int, translation_ids: List[int] = None, language: str = "ar") -> Optional[Dict]:
        """
        Fetch verses for a surah with text and translations
        
        Args:
            surah_number: Surah number (1-114)
            translation_ids: List of translation IDs to fetch (default: DEFAULT_TRANSLATIONS)
            language: Language code for UI language
            
        Returns:
            Verses data or None
        """
        if translation_ids is None:
            translation_ids = self.DEFAULT_TRANSLATIONS
        
        # Fetch Arabic text with translations
        endpoint = f"verses/by_chapter/{surah_number}"
        
        # Build translations parameter - comma-separated list of translation IDs
        translations_param = ",".join(str(tid) for tid in translation_ids)
        
        params = {
            "language": language,
            "words": "false",  # Don't fetch word-by-word data for now
            "translations": translations_param,
            "fields": "text_uthmani,text_imlaei,verse_key,verse_number,juz_number,hizb_number,rub_el_hizb_number",
            "per_page": 300  # Max verses in a surah (Al-Baqarah has 286)
        }
        
        result = self._make_request(endpoint, params=params)
        
        if result and "verses" in result:
            return result
        return None
    
    def fetch_audio_metadata(self, surah_number: int, reciter_id: int = 7) -> Optional[Dict]:
        """
        Fetch audio metadata for a surah
        
        Args:
            surah_number: Surah number (1-114)
            reciter_id: Reciter ID (default: 7 = Mishari Rashid al-`Afasy)
            
        Returns:
            Audio metadata or None
        """
        endpoint = f"chapter_recitations/{reciter_id}/{surah_number}"
        result = self._make_request(endpoint)
        
        if result and "audio_file" in result:
            return result
        return None
    
    def get_available_reciters(self) -> Optional[List[Dict]]:
        """
        Fetch list of available reciters
        
        Returns:
            List of reciter metadata
        """
        endpoint = "resources/recitations"
        result = self._make_request(endpoint)
        
        if result and "recitations" in result:
            return result["recitations"]
        return None
    
    def scrape_surah(self, surah_number: int, translation_ids: List[int] = None, include_audio: bool = True) -> bool:
        """
        Scrape complete data for a single surah and save to JSON
        
        Args:
            surah_number: Surah number (1-114)
            translation_ids: List of translation IDs to fetch (default: DEFAULT_TRANSLATIONS)
            include_audio: Whether to include audio metadata
            
        Returns:
            True if successful, False otherwise
        """
        if translation_ids is None:
            translation_ids = self.DEFAULT_TRANSLATIONS
            
        print(f"Scraping Surah {surah_number}...")
        
        # Fetch surah info
        surah_info = self.fetch_surah_info(surah_number)
        if not surah_info:
            print(f"Failed to fetch info for Surah {surah_number}")
            return False
        
        # Fetch verses with translations
        verses_data = self.fetch_surah_verses(surah_number, translation_ids=translation_ids)
        if not verses_data:
            print(f"Failed to fetch verses for Surah {surah_number}")
            return False
        
        # Fetch audio metadata if requested
        audio_data = None
        if include_audio:
            audio_data = self.fetch_audio_metadata(surah_number)
        
        # Prepare output data
        timestamp = datetime.utcnow().isoformat()
        
        # Build translation metadata
        translation_metadata = {}
        for trans_id in translation_ids:
            if trans_id in self.TRANSLATION_METADATA:
                translation_metadata[str(trans_id)] = self.TRANSLATION_METADATA[trans_id]
        
        output_data = {
            "metadata": {
                "surah_number": surah_number,
                "scraped_at": timestamp,
                "source": "api.quran.com",
                "version": "1.0",
                "translation_ids": translation_ids
            },
            "license": {
                "text": self.LICENSE_INFO["quran_text"].copy(),
                "translations": self.LICENSE_INFO["translations"].copy(),
                "audio": self.LICENSE_INFO["audio"].copy() if include_audio else None
            },
            "translation_metadata": translation_metadata,
            "surah_info": surah_info,
            "verses": verses_data.get("verses", []),
            "audio_metadata": audio_data if include_audio else None
        }
        
        # Update license timestamps
        output_data["license"]["text"]["fetched_at"] = timestamp
        output_data["license"]["translations"]["fetched_at"] = timestamp
        if include_audio and output_data["license"]["audio"]:
            output_data["license"]["audio"]["fetched_at"] = timestamp
        
        # Save to file
        output_file = self.quran_text_dir / f"surah_{surah_number:03d}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✓ Successfully saved Surah {surah_number} to {output_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to save Surah {surah_number}: {e}")
            return False
    
    def scrape_multiple_surahs(self, start: int = 1, end: int = 5, translation_ids: List[int] = None, include_audio: bool = True) -> Dict[str, Any]:
        """
        Scrape multiple surahs
        
        Args:
            start: Starting surah number
            end: Ending surah number (inclusive)
            translation_ids: List of translation IDs to fetch (default: DEFAULT_TRANSLATIONS)
            include_audio: Whether to include audio metadata
            
        Returns:
            Dictionary with scraping statistics
        """
        if translation_ids is None:
            translation_ids = self.DEFAULT_TRANSLATIONS
            
        print(f"\n{'='*60}")
        print(f"Starting Quran Data Scraping")
        print(f"Surahs: {start} to {end}")
        print(f"Translation IDs: {translation_ids}")
        print(f"Output directory: {self.quran_text_dir}")
        print(f"{'='*60}\n")
        
        successful = []
        failed = []
        
        for surah_num in range(start, end + 1):
            if self.scrape_surah(surah_num, translation_ids=translation_ids, include_audio=include_audio):
                successful.append(surah_num)
            else:
                failed.append(surah_num)
            
            # Be respectful to the API - add a small delay
            if surah_num < end:
                time.sleep(1)
        
        stats = {
            "total_attempted": end - start + 1,
            "successful": len(successful),
            "failed": len(failed),
            "successful_surahs": successful,
            "failed_surahs": failed,
            "output_directory": str(self.quran_text_dir)
        }
        
        print(f"\n{'='*60}")
        print(f"Scraping Complete!")
        print(f"Successful: {stats['successful']}/{stats['total_attempted']}")
        if failed:
            print(f"Failed: {failed}")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Main function to run the scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Quran data from api.quran.com")
    parser.add_argument("--start", type=int, default=1, help="Starting surah number (default: 1)")
    parser.add_argument("--end", type=int, default=5, help="Ending surah number (default: 5)")
    parser.add_argument("--no-audio", action="store_true", help="Skip audio metadata")
    parser.add_argument("--output-dir", type=str, help="Output directory for scraped data")
    parser.add_argument("--translations", type=str, help="Comma-separated list of translation IDs (default: 131)")
    
    args = parser.parse_args()
    
    # Validate surah numbers
    if not (1 <= args.start <= 114) or not (1 <= args.end <= 114):
        print("Error: Surah numbers must be between 1 and 114")
        return 1
    
    if args.start > args.end:
        print("Error: Start surah must be less than or equal to end surah")
        return 1
    
    # Parse translation IDs
    translation_ids = None
    if args.translations:
        try:
            translation_ids = [int(tid.strip()) for tid in args.translations.split(',')]
        except ValueError:
            print("Error: Translation IDs must be comma-separated integers")
            return 1
    
    # Create scraper and run
    scraper = QuranScraper(output_dir=args.output_dir)
    stats = scraper.scrape_multiple_surahs(
        start=args.start,
        end=args.end,
        translation_ids=translation_ids,
        include_audio=not args.no_audio
    )
    
    # Save stats
    stats_file = scraper.quran_text_dir / "scraping_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"Statistics saved to: {stats_file}")
    
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
