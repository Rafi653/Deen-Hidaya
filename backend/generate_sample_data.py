"""
Helper script to generate sample Quran data for testing
This creates minimal valid JSON files for surahs 2-5 with proper structure and license info
"""

import json
from pathlib import Path
from datetime import datetime

# Surah metadata (number, Arabic name, English name, transliteration, revelation, verses)
SURAH_DATA = {
    2: ("البقرة", "Al-Baqarah", "The Cow", "Medinan", 286),
    3: ("آل عمران", "Ali 'Imran", "Family of Imran", "Medinan", 200),
    4: ("النساء", "An-Nisa", "The Women", "Medinan", 176),
    5: ("المائدة", "Al-Ma'idah", "The Table Spread", "Medinan", 120),
}

# Sample verses for each surah (first 3 verses as examples)
SAMPLE_VERSES = {
    2: [
        ("الٓمٓ", "الم", "Alif, Lam, Meem."),
        ("ذَٰلِكَ ٱلْكِتَـٰبُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًۭى لِّلْمُتَّقِينَ", "ذلك الكتاب لا ريب فيه هدى للمتقين", "This is the Book about which there is no doubt, a guidance for those conscious of Allah -"),
        ("ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ وَيُقِيمُونَ ٱلصَّلَوٰةَ وَمِمَّا رَزَقْنَـٰهُمْ يُنفِقُونَ", "الذين يؤمنون بالغيب ويقيمون الصلاة ومما رزقناهم ينفقون", "Who believe in the unseen, establish prayer, and spend out of what We have provided for them,"),
    ],
    3: [
        ("الٓمٓ", "الم", "Alif, Lam, Meem."),
        ("ٱللَّهُ لَآ إِلَـٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ", "الله لا إله إلا هو الحي القيوم", "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence."),
        ("نَزَّلَ عَلَيْكَ ٱلْكِتَـٰبَ بِٱلْحَقِّ مُصَدِّقًۭا لِّمَا بَيْنَ يَدَيْهِ وَأَنزَلَ ٱلتَّوْرَىٰةَ وَٱلْإِنجِيلَ", "نزل عليك الكتاب بالحق مصدقا لما بين يديه وأنزل التوراة والإنجيل", "He has sent down upon you, [O Muhammad], the Book in truth, confirming what was before it. And He revealed the Torah and the Gospel."),
    ],
    4: [
        ("يَـٰٓأَيُّهَا ٱلنَّاسُ ٱتَّقُوا۟ رَبَّكُمُ ٱلَّذِى خَلَقَكُم مِّن نَّفْسٍۢ وَٰحِدَةٍۢ", "يا أيها الناس اتقوا ربكم الذي خلقكم من نفس واحدة", "O mankind, fear your Lord, who created you from one soul and created from it its mate"),
        ("وَءَاتُوا۟ ٱلْيَتَـٰمَىٰٓ أَمْوَٰلَهُمْ", "وآتوا اليتامى أموالهم", "And give to the orphans their properties"),
        ("وَإِنْ خِفْتُمْ أَلَّا تُقْسِطُوا۟ فِى ٱلْيَتَـٰمَىٰ", "وإن خفتم ألا تقسطوا في اليتامى", "And if you fear that you will not deal justly with the orphan girls"),
    ],
    5: [
        ("يَـٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوٓا۟ أَوْفُوا۟ بِٱلْعُقُودِ", "يا أيها الذين آمنوا أوفوا بالعقود", "O you who have believed, fulfill [all] contracts."),
        ("يَسْـَٔلُونَكَ مَاذَآ أُحِلَّ لَهُمْ", "يسألونك ماذا أحل لهم", "They ask you, [O Muhammad], what has been made lawful for them."),
        ("حُرِّمَتْ عَلَيْكُمُ ٱلْمَيْتَةُ وَٱلدَّمُ وَلَحْمُ ٱلْخِنزِيرِ", "حرمت عليكم الميتة والدم ولحم الخنزير", "Prohibited to you are dead animals, blood, the flesh of swine"),
    ],
}


def generate_surah_json(surah_number: int, output_dir: Path):
    """Generate sample JSON for a surah"""
    
    if surah_number not in SURAH_DATA:
        return False
    
    arabic_name, english_name, transliteration, revelation, total_verses = SURAH_DATA[surah_number]
    sample_verses = SAMPLE_VERSES[surah_number]
    
    timestamp = datetime.utcnow().isoformat()
    
    # Generate verses (just first 3 as samples, mark that this is sample data)
    verses = []
    for i, (text_uthmani, text_imlaei, translation) in enumerate(sample_verses, 1):
        verse = {
            "id": i,
            "verse_number": i,
            "verse_key": f"{surah_number}:{i}",
            "juz_number": 1,  # Simplified for sample
            "hizb_number": 1,
            "rub_el_hizb_number": 1,
            "text_uthmani": text_uthmani,
            "text_imlaei": text_imlaei,
            "translations": [
                {
                    "id": i,
                    "resource_id": 131,
                    "text": translation,
                    "resource_name": "Sahih International",
                    "language_name": "english"
                }
            ]
        }
        verses.append(verse)
    
    # Build JSON structure
    data = {
        "metadata": {
            "surah_number": surah_number,
            "scraped_at": timestamp,
            "source": "api.quran.com (fallback: local sample data for testing)",
            "version": "1.0",
            "note": f"Sample data containing first 3 verses of {total_verses} total verses"
        },
        "license": {
            "text": {
                "source": "api.quran.com",
                "license": "Public Domain",
                "attribution": "The Quran text is in the public domain",
                "terms_url": "https://quran.com/terms",
                "fetched_at": timestamp
            },
            "translations": {
                "source": "api.quran.com",
                "license": "Various - See individual translation licenses",
                "attribution": "Translation copyrights belong to respective translators",
                "terms_url": "https://quran.com/terms",
                "fetched_at": timestamp
            },
            "audio": {
                "source": "everyayah.com via api.quran.com",
                "license": "Free for non-commercial use",
                "attribution": "Audio recitations courtesy of everyayah.com",
                "terms_url": "https://everyayah.com/",
                "note": "Audio URLs provided - not downloaded locally due to size",
                "fetched_at": timestamp
            }
        },
        "surah_info": {
            "id": surah_number,
            "revelation_place": revelation,
            "name_complex": transliteration,
            "name_arabic": arabic_name,
            "name_simple": english_name,
            "verses_count": total_verses,
            "pages": [1, 1]  # Simplified
        },
        "verses": verses,
        "audio_metadata": {
            "audio_file": {
                "chapter_id": surah_number,
                "audio_url": f"https://verses.quran.com/Alafasy/mp3/{surah_number:03d}.mp3"
            },
            "recitation": {
                "id": 7,
                "reciter_name": "Mishari Rashid al-`Afasy",
                "style": "Murattal"
            }
        }
    }
    
    # Save to file
    output_file = output_dir / f"surah_{surah_number:03d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated: {output_file}")
    return True


def main():
    """Generate sample data for surahs 2-5"""
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "data" / "quran_text"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating sample Quran data for testing...")
    print(f"Output directory: {output_dir}\n")
    
    for surah_num in [2, 3, 4, 5]:
        generate_surah_json(surah_num, output_dir)
    
    print("\n✓ Sample data generation complete!")
    print("Note: These files contain only the first 3 verses of each surah for testing purposes.")


if __name__ == "__main__":
    main()
