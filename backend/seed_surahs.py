"""
Seed script to populate surah metadata
This script populates the database with information about all 114 surahs of the Quran
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Surah

# Surah data: number, Arabic name, English name, transliteration, revelation place, total verses
SURAH_DATA = [
    (1, "الفاتحة", "Al-Fatihah", "The Opening", "Meccan", 7),
    (2, "البقرة", "Al-Baqarah", "The Cow", "Medinan", 286),
    (3, "آل عمران", "Ali 'Imran", "Family of Imran", "Medinan", 200),
    (4, "النساء", "An-Nisa", "The Women", "Medinan", 176),
    (5, "المائدة", "Al-Ma'idah", "The Table Spread", "Medinan", 120),
    (6, "الأنعام", "Al-An'am", "The Cattle", "Meccan", 165),
    (7, "الأعراف", "Al-A'raf", "The Heights", "Meccan", 206),
    (8, "الأنفال", "Al-Anfal", "The Spoils of War", "Medinan", 75),
    (9, "التوبة", "At-Tawbah", "The Repentance", "Medinan", 129),
    (10, "يونس", "Yunus", "Jonah", "Meccan", 109),
    (11, "هود", "Hud", "Hud", "Meccan", 123),
    (12, "يوسف", "Yusuf", "Joseph", "Meccan", 111),
    (13, "الرعد", "Ar-Ra'd", "The Thunder", "Medinan", 43),
    (14, "إبراهيم", "Ibrahim", "Abraham", "Meccan", 52),
    (15, "الحجر", "Al-Hijr", "The Rocky Tract", "Meccan", 99),
    (16, "النحل", "An-Nahl", "The Bee", "Meccan", 128),
    (17, "الإسراء", "Al-Isra", "The Night Journey", "Meccan", 111),
    (18, "الكهف", "Al-Kahf", "The Cave", "Meccan", 110),
    (19, "مريم", "Maryam", "Mary", "Meccan", 98),
    (20, "طه", "Taha", "Ta-Ha", "Meccan", 135),
    (21, "الأنبياء", "Al-Anbya", "The Prophets", "Meccan", 112),
    (22, "الحج", "Al-Hajj", "The Pilgrimage", "Medinan", 78),
    (23, "المؤمنون", "Al-Mu'minun", "The Believers", "Meccan", 118),
    (24, "النور", "An-Nur", "The Light", "Medinan", 64),
    (25, "الفرقان", "Al-Furqan", "The Criterion", "Meccan", 77),
    (26, "الشعراء", "Ash-Shu'ara", "The Poets", "Meccan", 227),
    (27, "النمل", "An-Naml", "The Ant", "Meccan", 93),
    (28, "القصص", "Al-Qasas", "The Stories", "Meccan", 88),
    (29, "العنكبوت", "Al-'Ankabut", "The Spider", "Meccan", 69),
    (30, "الروم", "Ar-Rum", "The Romans", "Meccan", 60),
    (31, "لقمان", "Luqman", "Luqman", "Meccan", 34),
    (32, "السجدة", "As-Sajdah", "The Prostration", "Meccan", 30),
    (33, "الأحزاب", "Al-Ahzab", "The Combined Forces", "Medinan", 73),
    (34, "سبأ", "Saba", "Sheba", "Meccan", 54),
    (35, "فاطر", "Fatir", "Originator", "Meccan", 45),
    (36, "يس", "Ya-Sin", "Ya Sin", "Meccan", 83),
    (37, "الصافات", "As-Saffat", "Those who set the Ranks", "Meccan", 182),
    (38, "ص", "Sad", "The Letter \"Saad\"", "Meccan", 88),
    (39, "الزمر", "Az-Zumar", "The Troops", "Meccan", 75),
    (40, "غافر", "Ghafir", "The Forgiver", "Meccan", 85),
    (41, "فصلت", "Fussilat", "Explained in Detail", "Meccan", 54),
    (42, "الشورى", "Ash-Shuraa", "The Consultation", "Meccan", 53),
    (43, "الزخرف", "Az-Zukhruf", "The Ornaments of Gold", "Meccan", 89),
    (44, "الدخان", "Ad-Dukhan", "The Smoke", "Meccan", 59),
    (45, "الجاثية", "Al-Jathiyah", "The Crouching", "Meccan", 37),
    (46, "الأحقاف", "Al-Ahqaf", "The Wind-Curved Sandhills", "Meccan", 35),
    (47, "محمد", "Muhammad", "Muhammad", "Medinan", 38),
    (48, "الفتح", "Al-Fath", "The Victory", "Medinan", 29),
    (49, "الحجرات", "Al-Hujurat", "The Rooms", "Medinan", 18),
    (50, "ق", "Qaf", "The Letter \"Qaf\"", "Meccan", 45),
    (51, "الذاريات", "Adh-Dhariyat", "The Winnowing Winds", "Meccan", 60),
    (52, "الطور", "At-Tur", "The Mount", "Meccan", 49),
    (53, "النجم", "An-Najm", "The Star", "Meccan", 62),
    (54, "القمر", "Al-Qamar", "The Moon", "Meccan", 55),
    (55, "الرحمن", "Ar-Rahman", "The Beneficent", "Medinan", 78),
    (56, "الواقعة", "Al-Waqi'ah", "The Inevitable", "Meccan", 96),
    (57, "الحديد", "Al-Hadid", "The Iron", "Medinan", 29),
    (58, "المجادلة", "Al-Mujadila", "The Pleading Woman", "Medinan", 22),
    (59, "الحشر", "Al-Hashr", "The Exile", "Medinan", 24),
    (60, "الممتحنة", "Al-Mumtahanah", "She that is to be examined", "Medinan", 13),
    (61, "الصف", "As-Saf", "The Ranks", "Medinan", 14),
    (62, "الجمعة", "Al-Jumu'ah", "The Congregation", "Medinan", 11),
    (63, "المنافقون", "Al-Munafiqun", "The Hypocrites", "Medinan", 11),
    (64, "التغابن", "At-Taghabun", "The Mutual Disillusion", "Medinan", 18),
    (65, "الطلاق", "At-Talaq", "The Divorce", "Medinan", 12),
    (66, "التحريم", "At-Tahrim", "The Prohibition", "Medinan", 12),
    (67, "الملك", "Al-Mulk", "The Sovereignty", "Meccan", 30),
    (68, "القلم", "Al-Qalam", "The Pen", "Meccan", 52),
    (69, "الحاقة", "Al-Haqqah", "The Reality", "Meccan", 52),
    (70, "المعارج", "Al-Ma'arij", "The Ascending Stairways", "Meccan", 44),
    (71, "نوح", "Nuh", "Noah", "Meccan", 28),
    (72, "الجن", "Al-Jinn", "The Jinn", "Meccan", 28),
    (73, "المزمل", "Al-Muzzammil", "The Enshrouded One", "Meccan", 20),
    (74, "المدثر", "Al-Muddaththir", "The Cloaked One", "Meccan", 56),
    (75, "القيامة", "Al-Qiyamah", "The Resurrection", "Meccan", 40),
    (76, "الإنسان", "Al-Insan", "The Man", "Medinan", 31),
    (77, "المرسلات", "Al-Mursalat", "The Emissaries", "Meccan", 50),
    (78, "النبأ", "An-Naba", "The Tidings", "Meccan", 40),
    (79, "النازعات", "An-Nazi'at", "Those who drag forth", "Meccan", 46),
    (80, "عبس", "'Abasa", "He Frowned", "Meccan", 42),
    (81, "التكوير", "At-Takwir", "The Overthrowing", "Meccan", 29),
    (82, "الإنفطار", "Al-Infitar", "The Cleaving", "Meccan", 19),
    (83, "المطففين", "Al-Mutaffifin", "The Defrauding", "Meccan", 36),
    (84, "الإنشقاق", "Al-Inshiqaq", "The Splitting Open", "Meccan", 25),
    (85, "البروج", "Al-Buruj", "The Mansions of the Stars", "Meccan", 22),
    (86, "الطارق", "At-Tariq", "The Morning Star", "Meccan", 17),
    (87, "الأعلى", "Al-A'la", "The Most High", "Meccan", 19),
    (88, "الغاشية", "Al-Ghashiyah", "The Overwhelming", "Meccan", 26),
    (89, "الفجر", "Al-Fajr", "The Dawn", "Meccan", 30),
    (90, "البلد", "Al-Balad", "The City", "Meccan", 20),
    (91, "الشمس", "Ash-Shams", "The Sun", "Meccan", 15),
    (92, "الليل", "Al-Layl", "The Night", "Meccan", 21),
    (93, "الضحى", "Ad-Duhaa", "The Morning Hours", "Meccan", 11),
    (94, "الشرح", "Ash-Sharh", "The Relief", "Meccan", 8),
    (95, "التين", "At-Tin", "The Fig", "Meccan", 8),
    (96, "العلق", "Al-'Alaq", "The Clot", "Meccan", 19),
    (97, "القدر", "Al-Qadr", "The Power", "Meccan", 5),
    (98, "البينة", "Al-Bayyinah", "The Clear Proof", "Medinan", 8),
    (99, "الزلزلة", "Az-Zalzalah", "The Earthquake", "Medinan", 8),
    (100, "العاديات", "Al-'Adiyat", "The Courser", "Meccan", 11),
    (101, "القارعة", "Al-Qari'ah", "The Calamity", "Meccan", 11),
    (102, "التكاثر", "At-Takathur", "The Rivalry in world increase", "Meccan", 8),
    (103, "العصر", "Al-'Asr", "The Declining Day", "Meccan", 3),
    (104, "الهمزة", "Al-Humazah", "The Traducer", "Meccan", 9),
    (105, "الفيل", "Al-Fil", "The Elephant", "Meccan", 5),
    (106, "قريش", "Quraysh", "Quraysh", "Meccan", 4),
    (107, "الماعون", "Al-Ma'un", "The Small kindnesses", "Meccan", 7),
    (108, "الكوثر", "Al-Kawthar", "The Abundance", "Meccan", 3),
    (109, "الكافرون", "Al-Kafirun", "The Disbelievers", "Meccan", 6),
    (110, "النصر", "An-Nasr", "The Divine Support", "Medinan", 3),
    (111, "المسد", "Al-Masad", "The Palm Fiber", "Meccan", 5),
    (112, "الإخلاص", "Al-Ikhlas", "The Sincerity", "Meccan", 4),
    (113, "الفلق", "Al-Falaq", "The Daybreak", "Meccan", 5),
    (114, "الناس", "An-Nas", "Mankind", "Meccan", 6),
]


def seed_surahs(db: Session):
    """Seed the database with surah metadata"""
    print("Starting surah seeding...")
    
    # Check if surahs already exist
    existing_count = db.query(Surah).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} surahs. Skipping seeding.")
        return
    
    # Insert all surahs
    for number, name_arabic, name_english, transliteration, revelation, verses in SURAH_DATA:
        surah = Surah(
            number=number,
            name_arabic=name_arabic,
            name_english=name_english,
            name_transliteration=transliteration,
            revelation_place=revelation,
            total_verses=verses
        )
        db.add(surah)
    
    db.commit()
    print(f"Successfully seeded {len(SURAH_DATA)} surahs into the database.")


def main():
    """Main function to run the seeding"""
    print("Connecting to database...")
    db = SessionLocal()
    
    try:
        seed_surahs(db)
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
