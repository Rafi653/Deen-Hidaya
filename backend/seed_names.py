"""
Script to seed sample name data for testing the name generator
"""
import sys
import sqlalchemy as sa
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import NameEntity, Base


def seed_sample_names(db: Session):
    """Seed database with sample names for different entity types"""
    
    sample_names = [
        # Baby names - Boys (Islamic/Arabic origin)
        NameEntity(
            name="Muhammad",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="Praised one, praiseworthy",
            origin="Arabic",
            phonetic="moo-HAM-mad",
            themes=["classic", "religious", "traditional"],
            associated_traits=["leadership", "strength", "honor"],
            popularity_score=0.95
        ),
        NameEntity(
            name="Ali",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="Elevated, noble, sublime",
            origin="Arabic",
            phonetic="ah-LEE",
            themes=["classic", "traditional", "short"],
            associated_traits=["nobility", "bravery", "wisdom"],
            popularity_score=0.90
        ),
        NameEntity(
            name="Omar",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="Long-lived, flourishing",
            origin="Arabic",
            phonetic="OH-mar",
            themes=["classic", "traditional"],
            associated_traits=["longevity", "prosperity", "leadership"],
            popularity_score=0.85
        ),
        NameEntity(
            name="Yusuf",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="God increases",
            origin="Arabic",
            phonetic="YOO-soof",
            themes=["classic", "religious", "biblical"],
            associated_traits=["beauty", "wisdom", "patience"],
            popularity_score=0.88
        ),
        NameEntity(
            name="Zayn",
            entity_type="baby",
            subtype="human",
            gender="male",
            meaning="Beauty, grace",
            origin="Arabic",
            phonetic="ZAYN",
            themes=["modern", "short", "trendy"],
            associated_traits=["beauty", "grace", "charm"],
            popularity_score=0.75
        ),
        
        # Baby names - Girls (Islamic/Arabic origin)
        NameEntity(
            name="Fatima",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Captivating, one who weans",
            origin="Arabic",
            phonetic="fah-TEE-mah",
            themes=["classic", "religious", "traditional"],
            associated_traits=["purity", "devotion", "compassion"],
            popularity_score=0.92
        ),
        NameEntity(
            name="Aisha",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Living, prosperous",
            origin="Arabic",
            phonetic="ah-EE-shah",
            themes=["classic", "traditional"],
            associated_traits=["life", "prosperity", "wisdom"],
            popularity_score=0.89
        ),
        NameEntity(
            name="Maryam",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Beloved, drop of the sea",
            origin="Arabic",
            phonetic="MAR-yam",
            themes=["classic", "religious", "biblical"],
            associated_traits=["purity", "devotion", "grace"],
            popularity_score=0.91
        ),
        NameEntity(
            name="Zainab",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Fragrant flower",
            origin="Arabic",
            phonetic="ZAY-nab",
            themes=["classic", "traditional"],
            associated_traits=["beauty", "kindness", "strength"],
            popularity_score=0.86
        ),
        NameEntity(
            name="Layla",
            entity_type="baby",
            subtype="human",
            gender="female",
            meaning="Night, dark beauty",
            origin="Arabic",
            phonetic="LAY-lah",
            themes=["romantic", "poetic", "modern"],
            associated_traits=["beauty", "mystery", "romance"],
            popularity_score=0.83
        ),
        
        # Universal/Unisex baby names
        NameEntity(
            name="Noor",
            entity_type="baby",
            subtype="human",
            gender="unisex",
            meaning="Light, illumination",
            origin="Arabic",
            phonetic="NOOR",
            themes=["modern", "short", "spiritual"],
            associated_traits=["light", "guidance", "clarity"],
            popularity_score=0.80
        ),
        
        # Pet names - Dogs
        NameEntity(
            name="Max",
            entity_type="pet",
            subtype="dog",
            gender="male",
            meaning="Greatest",
            origin="Latin",
            phonetic="MAKS",
            themes=["classic", "short", "strong"],
            associated_traits=["strength", "loyalty", "leadership"],
            popularity_score=0.95
        ),
        NameEntity(
            name="Buddy",
            entity_type="pet",
            subtype="dog",
            gender="male",
            meaning="Friend, companion",
            origin="English",
            phonetic="BUH-dee",
            themes=["friendly", "playful", "classic"],
            associated_traits=["friendship", "loyalty", "joy"],
            popularity_score=0.88
        ),
        NameEntity(
            name="Luna",
            entity_type="pet",
            subtype="dog",
            gender="female",
            meaning="Moon",
            origin="Latin",
            phonetic="LOO-nah",
            themes=["mystical", "modern", "elegant"],
            associated_traits=["beauty", "mystery", "grace"],
            popularity_score=0.92
        ),
        NameEntity(
            name="Bella",
            entity_type="pet",
            subtype="dog",
            gender="female",
            meaning="Beautiful",
            origin="Italian",
            phonetic="BEL-lah",
            themes=["elegant", "classic", "feminine"],
            associated_traits=["beauty", "grace", "charm"],
            popularity_score=0.90
        ),
        
        # Pet names - Cats
        NameEntity(
            name="Whiskers",
            entity_type="pet",
            subtype="cat",
            gender="unisex",
            meaning="Facial hair",
            origin="English",
            phonetic="WISS-kerz",
            themes=["playful", "classic", "descriptive"],
            associated_traits=["curiosity", "playfulness", "cuteness"],
            popularity_score=0.75
        ),
        NameEntity(
            name="Shadow",
            entity_type="pet",
            subtype="cat",
            gender="unisex",
            meaning="Dark silhouette",
            origin="English",
            phonetic="SHAD-oh",
            themes=["mysterious", "sleek", "dark"],
            associated_traits=["stealth", "mystery", "independence"],
            popularity_score=0.78
        ),
        NameEntity(
            name="Simba",
            entity_type="pet",
            subtype="cat",
            gender="male",
            meaning="Lion",
            origin="Swahili",
            phonetic="SIM-bah",
            themes=["strong", "regal", "adventurous"],
            associated_traits=["bravery", "strength", "leadership"],
            popularity_score=0.82
        ),
        
        # Vehicle names - Cars
        NameEntity(
            name="Thunder",
            entity_type="vehicle",
            subtype="car",
            gender="unisex",
            meaning="Loud rumbling sound",
            origin="English",
            phonetic="THUN-der",
            themes=["powerful", "fast", "bold"],
            associated_traits=["power", "speed", "intensity"],
            popularity_score=0.70
        ),
        NameEntity(
            name="Phoenix",
            entity_type="vehicle",
            subtype="car",
            gender="unisex",
            meaning="Mythical bird that rises from ashes",
            origin="Greek",
            phonetic="FEE-niks",
            themes=["mythical", "powerful", "resilient"],
            associated_traits=["rebirth", "strength", "endurance"],
            popularity_score=0.72
        ),
        NameEntity(
            name="Blaze",
            entity_type="vehicle",
            subtype="car",
            gender="unisex",
            meaning="Bright flame",
            origin="English",
            phonetic="BLAYZ",
            themes=["fiery", "fast", "intense"],
            associated_traits=["speed", "passion", "energy"],
            popularity_score=0.68
        ),
        
        # Vehicle names - Motorcycles
        NameEntity(
            name="Raptor",
            entity_type="vehicle",
            subtype="motorcycle",
            gender="unisex",
            meaning="Bird of prey",
            origin="Latin",
            phonetic="RAP-tor",
            themes=["fierce", "fast", "predatory"],
            associated_traits=["speed", "agility", "power"],
            popularity_score=0.75
        ),
        NameEntity(
            name="Ghost",
            entity_type="vehicle",
            subtype="motorcycle",
            gender="unisex",
            meaning="Spirit",
            origin="English",
            phonetic="GOHST",
            themes=["mysterious", "sleek", "stealthy"],
            associated_traits=["stealth", "speed", "mystery"],
            popularity_score=0.73
        ),
        
        # Company names - Tech
        NameEntity(
            name="Innovatech",
            entity_type="company",
            subtype="technology",
            gender="unisex",
            meaning="Innovation in technology",
            origin="English",
            phonetic="in-NO-vah-tek",
            themes=["professional", "modern", "technical"],
            associated_traits=["innovation", "progress", "technology"],
            popularity_score=0.65
        ),
        NameEntity(
            name="NexGen",
            entity_type="company",
            subtype="technology",
            gender="unisex",
            meaning="Next generation",
            origin="English",
            phonetic="NEKS-jen",
            themes=["futuristic", "professional", "cutting-edge"],
            associated_traits=["innovation", "future", "advancement"],
            popularity_score=0.70
        ),
        NameEntity(
            name="ByteForge",
            entity_type="company",
            subtype="software",
            gender="unisex",
            meaning="Creating/forging digital solutions",
            origin="English",
            phonetic="BYTE-forj",
            themes=["technical", "creative", "professional"],
            associated_traits=["craftsmanship", "technology", "innovation"],
            popularity_score=0.62
        ),
        
        # Company names - Retail
        NameEntity(
            name="Urban Nest",
            entity_type="company",
            subtype="retail",
            gender="unisex",
            meaning="City living space",
            origin="English",
            phonetic="UR-ban NEST",
            themes=["modern", "cozy", "lifestyle"],
            associated_traits=["comfort", "style", "home"],
            popularity_score=0.68
        ),
        NameEntity(
            name="Evergreen Market",
            entity_type="company",
            subtype="retail",
            gender="unisex",
            meaning="Always fresh marketplace",
            origin="English",
            phonetic="EV-er-green MAR-ket",
            themes=["natural", "sustainable", "fresh"],
            associated_traits=["freshness", "sustainability", "quality"],
            popularity_score=0.71
        ),
        
        # Toy names
        NameEntity(
            name="Buddy Bear",
            entity_type="toy",
            subtype="stuffed_animal",
            gender="unisex",
            meaning="Friendly teddy bear",
            origin="English",
            phonetic="BUH-dee BAIR",
            themes=["cute", "friendly", "classic"],
            associated_traits=["friendship", "comfort", "joy"],
            popularity_score=0.85
        ),
        NameEntity(
            name="Captain Zoom",
            entity_type="toy",
            subtype="action_figure",
            gender="male",
            meaning="Fast-moving hero",
            origin="English",
            phonetic="KAP-tin ZOOM",
            themes=["heroic", "adventurous", "energetic"],
            associated_traits=["speed", "bravery", "adventure"],
            popularity_score=0.77
        ),
        NameEntity(
            name="Sparkle",
            entity_type="toy",
            subtype="stuffed_animal",
            gender="female",
            meaning="Glitter, shine",
            origin="English",
            phonetic="SPAR-kul",
            themes=["magical", "cute", "shiny"],
            associated_traits=["beauty", "magic", "joy"],
            popularity_score=0.80
        ),
        NameEntity(
            name="Robo Rex",
            entity_type="toy",
            subtype="robot",
            gender="unisex",
            meaning="Robot dinosaur king",
            origin="English",
            phonetic="ROH-boh REKS",
            themes=["futuristic", "strong", "adventurous"],
            associated_traits=["strength", "technology", "power"],
            popularity_score=0.74
        ),
    ]
    
    # Check if data already exists
    existing_count = db.query(NameEntity).count()
    if existing_count > 0:
        print(f"Database already has {existing_count} names. Skipping seed.")
        print("To re-seed, delete existing names first.")
        return
    
    # Add all sample names
    for name in sample_names:
        db.add(name)
    
    db.commit()
    print(f"Successfully seeded {len(sample_names)} sample names!")
    
    # Print summary
    summary = db.query(NameEntity.entity_type, sa.func.count(NameEntity.id))\
        .group_by(NameEntity.entity_type)\
        .all()
    
    print("\nNames by entity type:")
    for entity_type, count in summary:
        print(f"  {entity_type}: {count}")


if __name__ == "__main__":
    print("Seeding name database with sample data...")
    db = SessionLocal()
    try:
        seed_sample_names(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()
    
    print("\nDone!")
