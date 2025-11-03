# Name Generator Feature Documentation

## Overview

The Suggestive Name Generator is a versatile tool that helps users find the perfect name for various entities including babies, pets, vehicles, companies, toys, and more. The system uses a sophisticated recommendation algorithm to suggest names based on user preferences.

## Features

### Entity Types Supported
- **Baby Names**: Human baby names with cultural and religious significance
- **Pet Names**: Names for dogs, cats, and other pets
- **Vehicle Names**: Names for cars, motorcycles, and other vehicles
- **Company Names**: Business and organization names
- **Toy Names**: Names for toys and playthings

### User Preferences

Users can specify the following preferences:

1. **Entity Type** (required): The type of entity being named
2. **Subtype/Category**: More specific categorization (e.g., dog/cat for pets, car/motorcycle for vehicles)
3. **Gender**: Male, female, or unisex (where applicable)
4. **Origin**: Cultural or linguistic origin (e.g., Arabic, English, Latin, etc.)
5. **Meaning**: Desired meaning or association (e.g., "strength", "joy", "beauty")
6. **Themes**: Multiple themes can be selected (e.g., classic, modern, playful, professional)
7. **Phonetic Preference**: Phonetic patterns or sounds

### Recommendation Algorithm

The system uses a weighted relevance scoring algorithm with the following factors:

- **Base Popularity** (20%): General popularity of the name
- **Meaning Match** (25%): How well the name's meaning matches user preferences
- **Theme Match** (25%): Overlap between user-selected themes and name themes
- **Phonetic Match** (15%): Similarity to phonetic preferences
- **Origin Match** (15%): Match with preferred cultural origin

Names are ranked by relevance score, with higher scores indicating better matches to user preferences.

### Results Features

- **Relevance Scoring**: Each suggestion includes a relevance score (0-100%)
- **Filtering**: Filter results by gender and origin after generation
- **Sorting**: Sort by relevance, name (alphabetically), or popularity
- **Favorites**: Save favorite names for later review
- **Detailed Information**: View meaning, origin, phonetic pronunciation, themes, and associated traits

## Architecture

### Backend (FastAPI + PostgreSQL)

**Models:**
- `NameEntity`: Stores name data with metadata
- `NameFavorite`: Tracks user favorites

**Services:**
- `NameSuggestionService`: Core recommendation engine

**API Endpoints:**
- `POST /api/v1/names/suggest` - Get name suggestions
- `GET /api/v1/names/entity-types` - Get available entity types
- `GET /api/v1/names/subtypes/{entity_type}` - Get subtypes for entity type
- `GET /api/v1/names/origins` - Get available origins
- `GET /api/v1/names/themes` - Get available themes
- `GET /api/v1/names/names/{id}` - Get specific name details
- `GET /api/v1/names/search` - Search names by query
- `POST /api/v1/names/favorites` - Add to favorites
- `GET /api/v1/names/favorites/{user_id}` - Get user favorites
- `DELETE /api/v1/names/favorites/{id}` - Remove from favorites

### Frontend (Next.js + React)

**Pages:**
- `/name-generator` - Main name generator interface

**Components:**
- Preference form with all input fields
- Results grid with name cards
- Filter and sort controls
- Favorites management

## Setup Instructions

### 1. Database Migration

Run the Alembic migration to create the required tables:

```bash
cd backend
alembic upgrade head
```

### 2. Seed Sample Data

Populate the database with sample names:

```bash
cd backend
python seed_names.py
```

This will add 30+ sample names across different categories including:
- 11 baby names (Arabic origin)
- 7 pet names (dogs and cats)
- 5 vehicle names (cars and motorcycles)
- 5 company names (tech and retail)
- 4 toy names

### 3. Start Services

Start the backend and frontend services:

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (in another terminal)
cd frontend
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Name Generator: http://localhost:3000/name-generator
- API Documentation: http://localhost:8000/docs

## Usage Examples

### Example 1: Finding a Baby Name

**Preferences:**
- Entity Type: Baby
- Gender: Male
- Origin: Arabic
- Themes: Classic, Religious
- Meaning: Strength

**Expected Results:**
Names like Muhammad, Ali, Omar with high relevance scores based on matching criteria.

### Example 2: Finding a Pet Name

**Preferences:**
- Entity Type: Pet
- Subtype: Dog
- Gender: Female
- Themes: Elegant, Modern

**Expected Results:**
Names like Luna, Bella with associated traits of beauty and grace.

### Example 3: Finding a Company Name

**Preferences:**
- Entity Type: Company
- Subtype: Technology
- Themes: Professional, Modern
- Meaning: Innovation

**Expected Results:**
Names like Innovatech, NexGen, ByteForge with professional themes.

## Extensibility

### Adding New Entity Types

1. Add names to the database with the new entity type:

```python
new_name = NameEntity(
    name="Example",
    entity_type="new_type",
    subtype="category",
    # ... other fields
)
db.add(new_name)
db.commit()
```

2. The new entity type will automatically appear in the UI dropdown.

### Adding New Name Data

New names can be added through:
- Direct database insertion
- Bulk import scripts
- Admin API endpoints (future enhancement)

### Customizing the Algorithm

The relevance scoring weights can be adjusted in `name_suggestion_service.py`:

```python
def _calculate_relevance_score(self, name: NameEntity, request: NameSuggestionRequest) -> float:
    # Adjust weights here:
    # - Base popularity: currently 0.2 (20%)
    # - Meaning match: currently 0.25 (25%)
    # - Theme match: currently 0.25 (25%)
    # - Phonetic match: currently 0.15 (15%)
    # - Origin match: currently 0.15 (15%)
```

## Testing

### Backend Tests

Run the comprehensive test suite:

```bash
cd backend
pytest test_name_generator.py -v
```

Test coverage includes:
- API endpoint functionality
- Suggestion algorithm
- Filtering and sorting
- Favorites management
- Error handling

### Manual Testing

1. Navigate to http://localhost:3000/name-generator
2. Select different entity types and observe subtype changes
3. Apply various filters and verify results
4. Add/remove favorites
5. Test sorting and filtering options
6. Verify responsive design on mobile devices

## API Examples

### Generate Name Suggestions

```bash
curl -X POST "http://localhost:8000/api/v1/names/suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "baby",
    "gender": "male",
    "origin": "Arabic",
    "themes": ["classic", "religious"],
    "max_results": 20
  }'
```

### Search Names

```bash
curl "http://localhost:8000/api/v1/names/search?query=Max&entity_type=pet"
```

### Add to Favorites

```bash
curl -X POST "http://localhost:8000/api/v1/names/favorites" \
  -H "Content-Type: application/json" \
  -d '{
    "name_entity_id": 1,
    "user_id": "user_123",
    "note": "Love this name!"
  }'
```

## Future Enhancements

### Potential Features
1. **User Accounts**: Full user authentication and profile management
2. **Comparison Tool**: Compare multiple names side-by-side
3. **Name History**: Track previously viewed names
4. **Social Sharing**: Share favorite names with friends and family
5. **Custom Lists**: Create and manage multiple name lists
6. **Name Ratings**: Community ratings and reviews
7. **Name Trends**: Analytics on popular names over time
8. **AI-Generated Names**: Use GPT to generate unique names based on preferences
9. **Pronunciation Audio**: Audio clips for name pronunciation
10. **Name Compatibility**: Check name compatibility with surnames or themes
11. **Multilingual Support**: Names and meanings in multiple languages
12. **Export Functionality**: Export favorites to PDF or CSV

### Data Expansion
- Expand name database to thousands of entries
- Add more cultural origins (Indian, Chinese, Japanese, African, etc.)
- Include historical context and famous namesakes
- Add naming traditions and customs

### Algorithm Improvements
- Machine learning-based recommendations
- Collaborative filtering based on user preferences
- Semantic similarity for meaning matching
- Advanced phonetic analysis

## Security Considerations

- User IDs are stored locally in browser localStorage
- No sensitive personal information is collected
- API rate limiting should be implemented in production
- Input validation on all user inputs
- SQL injection protection via SQLAlchemy ORM

## Performance Considerations

- Database indexes on frequently queried fields
- Pagination for large result sets
- Caching of entity types, origins, and themes
- Lazy loading of favorites
- Optimized relevance score calculations

## Troubleshooting

### Names Not Appearing
- Ensure database migration has been run
- Verify seed script has been executed
- Check backend logs for errors

### Favorites Not Saving
- Verify localStorage is enabled in browser
- Check network requests for API errors
- Ensure user_id is generated properly

### Low Relevance Scores
- Adjust algorithm weights in `name_suggestion_service.py`
- Add more name data with better metadata
- Improve meaning and theme matching logic

## Contributing

To contribute new names or features:

1. Add names with comprehensive metadata
2. Include meanings, origins, and themes
3. Test with various preference combinations
4. Update documentation
5. Submit pull request with test coverage

## License

*(Same as parent project)*
