"""
Transliteration Generator Module

This module provides functions to generate transliteration for Arabic Quran text
using various strategies:
1. Fetch from api.quran.com (when available)
2. Use a simple Arabic-to-Latin mapping (fallback)

Author: Deen Hidaya Backend Team
"""

import re
from typing import Dict, Optional


# Simple Arabic to Latin character mapping
# This is a basic transliteration map - can be enhanced with more sophisticated rules
ARABIC_TO_LATIN = {
    # Letters
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa',
    'ب': 'b',
    'ت': 't',
    'ث': 'th',
    'ج': 'j',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'dh',
    'ر': 'r',
    'ز': 'z',
    'س': 's',
    'ش': 'sh',
    'ص': 's',
    'ض': 'd',
    'ط': 't',
    'ظ': 'z',
    'ع': "'",
    'غ': 'gh',
    'ف': 'f',
    'ق': 'q',
    'ك': 'k',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'و': 'w',
    'ي': 'y',
    'ى': 'a',
    'ة': 'h',
    'ئ': "'",
    'ؤ': "'",
    
    # Tashkeel (diacritics) - representing vowels
    'َ': 'a',  # Fatha
    'ُ': 'u',  # Damma
    'ِ': 'i',  # Kasra
    'ّ': '',   # Shadda (doubled letter)
    'ْ': '',   # Sukun (no vowel)
    'ً': 'an', # Tanween Fath
    'ٌ': 'un', # Tanween Dam
    'ٍ': 'in', # Tanween Kasr
    'ٓ': 'aa', # Madda
    'ٰ': 'a',  # Alif Khanjariyah
    
    # Special characters
    'ﷲ': 'Allah',
    'ﷺ': '(peace be upon him)',
    '۞': '',   # Star
    '۩': '',   # Sajdah marker
}


def simple_transliterate(arabic_text: str) -> str:
    """
    Generate simple transliteration of Arabic text to Latin characters.
    
    This is a basic implementation that maps Arabic characters to their
    Latin equivalents. For production use, consider using more sophisticated
    libraries or API-based transliteration.
    
    Args:
        arabic_text: Arabic text to transliterate
        
    Returns:
        Transliterated text in Latin characters
    """
    if not arabic_text:
        return ""
    
    result = []
    text = arabic_text.strip()
    
    for char in text:
        # Check if character is in our mapping
        if char in ARABIC_TO_LATIN:
            latin = ARABIC_TO_LATIN[char]
            result.append(latin)
        elif char in ' \n\t':
            # Preserve whitespace
            result.append(char)
        elif char.isdigit():
            # Preserve numbers
            result.append(char)
        else:
            # For unknown characters, skip them
            # (includes tatweel, other marks)
            pass
    
    # Join and clean up multiple spaces
    transliterated = ''.join(result)
    transliterated = re.sub(r'\s+', ' ', transliterated)
    transliterated = transliterated.strip()
    
    # Capitalize first letter of each sentence
    if transliterated:
        transliterated = transliterated[0].upper() + transliterated[1:]
    
    return transliterated


def fetch_transliteration_from_api(surah_number: int, verse_number: int) -> Optional[str]:
    """
    Fetch transliteration from api.quran.com (when available).
    
    This function attempts to fetch transliteration from the API.
    If the API is unavailable or doesn't provide transliteration,
    it returns None and we should fall back to simple_transliterate.
    
    Args:
        surah_number: Surah number (1-114)
        verse_number: Verse number within the surah
        
    Returns:
        Transliteration text or None if unavailable
    """
    # Note: api.quran.com doesn't directly provide verse transliteration
    # In the current implementation, but they do have transliteration resources
    # We could potentially fetch from:
    # https://api.quran.com/api/v4/quran/transliterations/{transliteration_id}
    # For now, return None to indicate API method not implemented
    return None


def generate_transliteration(arabic_text: str, 
                            surah_number: Optional[int] = None,
                            verse_number: Optional[int] = None) -> str:
    """
    Generate transliteration for Arabic text.
    
    Tries multiple strategies:
    1. Fetch from API if surah/verse numbers provided
    2. Fall back to simple character-by-character transliteration
    
    Args:
        arabic_text: Arabic text to transliterate
        surah_number: Optional surah number for API lookup
        verse_number: Optional verse number for API lookup
        
    Returns:
        Transliterated text in Latin characters
    """
    # Try API first if we have verse coordinates
    if surah_number and verse_number:
        api_result = fetch_transliteration_from_api(surah_number, verse_number)
        if api_result:
            return api_result
    
    # Fall back to simple transliteration
    return simple_transliterate(arabic_text)


# Example usage and testing
if __name__ == "__main__":
    # Test with first verse of Al-Fatihah
    test_verse = "بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ"
    transliteration = generate_transliteration(test_verse, 1, 1)
    print(f"Arabic: {test_verse}")
    print(f"Transliteration: {transliteration}")
    
    # Expected output similar to: "Bismi Allahi alrrahmani alrrahimi"
