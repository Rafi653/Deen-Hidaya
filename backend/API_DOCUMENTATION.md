# Deen Hidaya API Documentation

## Overview

The Deen Hidaya API provides RESTful endpoints for accessing Quran text, translations, transliterations, audio recitations, bookmarks, and search functionality.

**Base URL:** `http://localhost:8000`  
**API Version:** `v1`  
**API Documentation:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Documentation:** `http://localhost:8000/redoc` (ReDoc)

## Authentication

Admin endpoints require Bearer token authentication:

```bash
Authorization: Bearer <admin_token>
```

Set `ADMIN_TOKEN` in your `.env` file for admin access.

## Endpoints

### Health Check

#### GET /health
Health check endpoint for service monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.0.0"
}
```

---

### Surah Endpoints

#### GET /api/v1/surahs
List all surahs with basic information.

**Query Parameters:**
- `skip` (integer, default: 0): Number of surahs to skip
- `limit` (integer, default: 114, max: 114): Number of surahs to return

**Response:**
```json
[
  {
    "id": 1,
    "number": 1,
    "name_arabic": "الفاتحة",
    "name_english": "Al-Fatiha",
    "name_transliteration": "Al-Fatihah",
    "revelation_place": "Meccan",
    "total_verses": 7
  }
]
```

#### GET /api/v1/surahs/{surah_number}
Get detailed information about a specific surah including all verses.

**Path Parameters:**
- `surah_number` (integer): Surah number (1-114)

**Query Parameters:**
- `include_translations` (boolean, default: true): Include translations in verses

**Response:**
```json
{
  "id": 1,
  "number": 1,
  "name_arabic": "الفاتحة",
  "name_english": "Al-Fatiha",
  "name_transliteration": "Al-Fatihah",
  "revelation_place": "Meccan",
  "total_verses": 7,
  "verses": [
    {
      "id": 1,
      "verse_number": 1,
      "text_arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
      "text_simple": "بسم الله الرحمن الرحيم",
      "text_transliteration": "Bismillahir Rahmanir Raheem",
      "juz_number": 1,
      "translations": [
        {
          "id": 1,
          "language": "en",
          "translator": "Sahih International",
          "text": "In the name of Allah, the Entirely Merciful, the Especially Merciful.",
          "license": "CC BY-NC-ND 4.0",
          "source": "api.quran.com"
        }
      ]
    }
  ]
}
```

---

### Verse Endpoints

#### GET /api/v1/verses/{verse_id}
Get detailed information about a specific verse.

**Path Parameters:**
- `verse_id` (integer): Verse ID

**Query Parameters:**
- `include_translations` (boolean, default: true): Include translations

**Response:**
```json
{
  "id": 1,
  "verse_number": 1,
  "text_arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
  "text_simple": "بسم الله الرحمن الرحيم",
  "text_transliteration": "Bismillahir Rahmanir Raheem",
  "juz_number": 1,
  "sajda": false,
  "translations": []
}
```

#### GET /api/v1/surahs/{surah_number}/verses/{verse_number}
Get a verse by surah number and verse number (e.g., 2:255 for Ayat al-Kursi).

**Path Parameters:**
- `surah_number` (integer): Surah number (1-114)
- `verse_number` (integer): Verse number within the surah

**Query Parameters:**
- `include_translations` (boolean, default: true): Include translations

---

### Audio Endpoints

#### GET /api/v1/verses/{verse_id}/audio
Get audio metadata for a specific verse.

**Path Parameters:**
- `verse_id` (integer): Verse ID

**Query Parameters:**
- `language` (string, optional): Filter by language (ar, en, te)
- `reciter` (string, optional): Filter by reciter name

**Response:**
```json
[
  {
    "id": 1,
    "reciter": "Abdul Basit",
    "reciter_arabic": "عبد الباسط عبد الصمد",
    "audio_url": "/audio/abdul_basit/001001.mp3",
    "duration": 5.2,
    "format": "mp3",
    "quality": "128kbps"
  }
]
```

#### GET /api/v1/verses/{verse_id}/audio/stream
Stream audio file for a verse with HTTP range request support.

**Path Parameters:**
- `verse_id` (integer): Verse ID

**Query Parameters:**
- `language` (string, default: "ar"): Language code (ar, en, te)
- `reciter` (string, default: "default"): Reciter identifier

**Headers:**
- `Range` (optional): Byte range for partial content (e.g., "bytes=0-1023")

**Response:**
- Content-Type: `audio/mpeg`
- Status: 200 (full content) or 206 (partial content)
- Headers: `Content-Range`, `Accept-Ranges`, `Content-Length`

**Example:**
```bash
curl -H "Range: bytes=0-1023" http://localhost:8000/api/v1/verses/1/audio/stream
```

---

### Bookmark Endpoints

#### POST /api/v1/bookmarks
Create a new bookmark for a verse.

**Request Body:**
```json
{
  "verse_id": 1,
  "user_id": "user_session_123",
  "note": "Important verse about patience"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "verse_id": 1,
  "user_id": "user_session_123",
  "note": "Important verse about patience",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/bookmarks
List all bookmarks for a user.

**Query Parameters:**
- `user_id` (string, required): User ID or session ID
- `include_verses` (boolean, default: true): Include verse details
- `skip` (integer, default: 0): Number to skip
- `limit` (integer, default: 100, max: 100): Number to return

**Response:**
```json
[
  {
    "id": 1,
    "verse_id": 1,
    "user_id": "user_session_123",
    "note": "Important verse",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "verse": {
      "id": 1,
      "verse_number": 1,
      "text_arabic": "...",
      "translations": []
    }
  }
]
```

#### DELETE /api/v1/bookmarks/{bookmark_id}
Delete a bookmark.

**Path Parameters:**
- `bookmark_id` (integer): Bookmark ID

**Query Parameters:**
- `user_id` (string, required): User ID for authorization

**Response:**
- Status: 204 (No Content)

---

### Search Endpoint

#### GET /api/v1/search
Unified search endpoint for Quran verses.

**Query Parameters:**
- `q` (string, required): Search query
- `lang` (string, default: "en"): Language to search (en, ar, te)
- `search_type` (string, default: "hybrid"): Search type
  - `exact`: Exact text matching
  - `fuzzy`: Fuzzy matching with PostgreSQL trigram similarity
  - `semantic`: Semantic search using embeddings (requires issue #7)
  - `hybrid`: Combines all search types
- `limit` (integer, default: 20, max: 100): Number of results

**Response:**
```json
{
  "query": "patience",
  "results": [
    {
      "verse_id": 156,
      "verse_number": 45,
      "surah_number": 2,
      "surah_name": "Al-Baqarah",
      "text_arabic": "وَاسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ",
      "text_transliteration": "Wastaʿīnū biṣ-ṣabri waṣ-ṣalāh",
      "translations": [
        {
          "id": 156,
          "language": "en",
          "translator": "Sahih International",
          "text": "And seek help through patience and prayer...",
          "license": "CC BY-NC-ND 4.0",
          "source": "api.quran.com"
        }
      ],
      "score": 0.95,
      "match_type": "exact"
    }
  ],
  "total": 15,
  "search_type": "hybrid"
}
```

**Search Type Behavior:**
- **exact**: Direct substring match using ILIKE
- **fuzzy**: PostgreSQL pg_trgm similarity (threshold: 0.3)
- **semantic**: Vector similarity search (placeholder for issue #7)
- **hybrid**: Combines all types with weighted scoring:
  - Exact: 1.0
  - Fuzzy: 0.8
  - Semantic: 0.7

---

### Translation Endpoint

#### GET /api/v1/translations
List all available translator/language combinations.

**Response:**
```json
[
  {
    "language": "en",
    "translator": "Sahih International",
    "source": "api.quran.com",
    "license": "CC BY-NC-ND 4.0"
  },
  {
    "language": "te",
    "translator": "Muhammad Junagarhi",
    "source": "tanzil.net",
    "license": "Public Domain"
  }
]
```

---

### Admin Endpoints

**Authentication Required:** All admin endpoints require Bearer token authentication.

#### POST /api/v1/admin/ingest/scrape
Run data scraping and ingestion pipeline.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "surah_numbers": [1, 2, 3]
}
```

**Optional Parameters:**
- `surah_numbers`: Array of specific surah numbers to scrape (if omitted, scrapes all)

**Response:**
```json
{
  "status": "success",
  "message": "Scraped 3 surahs and ingested successfully",
  "surahs_processed": [1, 2, 3],
  "verses_processed": 350
}
```

**Error Response (403):**
```json
{
  "detail": "Invalid admin token"
}
```

#### POST /api/v1/admin/embed/verse
Create embeddings for verses (placeholder for issue #7).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "verse_ids": [1, 2, 3],
  "model": "text-embedding-ada-002",
  "language": "en"
}
```

**Optional Parameters:**
- `verse_ids`: Array of specific verse IDs to embed (if omitted, embeds all)
- `model`: Embedding model to use (default: "text-embedding-ada-002")
- `language`: Language of text to embed (default: "en")

**Response:**
```json
{
  "status": "pending",
  "message": "Would embed 3 verses (embedding generation not yet implemented)",
  "verses_embedded": 0
}
```

---

## Error Responses

All endpoints follow consistent error response format:

**404 Not Found:**
```json
{
  "detail": "Verse 99999 not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Invalid search_type. Must be one of: exact, fuzzy, semantic, hybrid"
}
```

**403 Forbidden:**
```json
{
  "detail": "Invalid admin token"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Scraping/ingestion failed: <error details>"
}
```

---

## Rate Limiting

Rate limiting is not currently implemented but is recommended for production use. 

**Recommended Implementation:**
- Use FastAPI-limiter or SlowAPI for application-level rate limiting
- Configure Nginx or API Gateway for infrastructure-level rate limiting
- Implement stricter limits for admin endpoints (e.g., 10 requests/hour)
- Standard endpoints: 100 requests/minute per user
- Search endpoints: 30 requests/minute per user

**Note:** This is a minimal viable implementation focusing on core functionality. Rate limiting should be added before production deployment, especially for public-facing and admin endpoints.

---

## CORS Configuration

CORS is configured to allow all origins in development. Update for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

---

## Examples

### Python

```python
import requests

# Get all surahs
response = requests.get("http://localhost:8000/api/v1/surahs")
surahs = response.json()

# Search for verses
response = requests.get(
    "http://localhost:8000/api/v1/search",
    params={"q": "mercy", "lang": "en", "search_type": "hybrid"}
)
results = response.json()

# Create bookmark
response = requests.post(
    "http://localhost:8000/api/v1/bookmarks",
    json={
        "verse_id": 1,
        "user_id": "user123",
        "note": "Beautiful verse"
    }
)
bookmark = response.json()
```

### JavaScript

```javascript
// Get surah details
const response = await fetch('http://localhost:8000/api/v1/surahs/1');
const surah = await response.json();

// Search verses
const searchResponse = await fetch(
  'http://localhost:8000/api/v1/search?q=patience&lang=en&search_type=hybrid'
);
const searchResults = await searchResponse.json();

// Stream audio with range support
const audioResponse = await fetch(
  'http://localhost:8000/api/v1/verses/1/audio/stream?language=ar',
  {
    headers: {
      'Range': 'bytes=0-'
    }
  }
);
const audioBlob = await audioResponse.blob();
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# List surahs
curl http://localhost:8000/api/v1/surahs

# Get specific surah
curl http://localhost:8000/api/v1/surahs/1

# Search
curl "http://localhost:8000/api/v1/search?q=patience&lang=en&search_type=hybrid"

# Create bookmark
curl -X POST http://localhost:8000/api/v1/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"verse_id": 1, "user_id": "user123", "note": "Important"}'

# Stream audio with range
curl -H "Range: bytes=0-1023" \
  http://localhost:8000/api/v1/verses/1/audio/stream

# Admin endpoint (replace YOUR_ADMIN_TOKEN with actual token from .env file)
curl -X POST http://localhost:8000/api/v1/admin/ingest/scrape \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"surah_numbers": [1, 2, 3]}'
```

---

## Database Schema

Refer to `/backend/models.py` for complete schema definitions:

- **surah**: Surah metadata
- **verse**: Verse text and metadata
- **translation**: Verse translations
- **audio_track**: Audio file metadata
- **bookmark**: User bookmarks
- **tag**: Verse tags
- **verse_tag**: Many-to-many verse-tag relationship
- **embedding**: Verse embeddings for semantic search
- **entity**: Named entities mentioned in Quran

---

## Development

### Running Tests

```bash
cd backend
pytest test_api.py -v
```

### Starting Development Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Interactive API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Future Enhancements

- [ ] Implement semantic search (Issue #7)
- [ ] Add rate limiting
- [ ] Add caching layer (Redis)
- [ ] Implement pagination cursors
- [ ] Add WebSocket support for real-time updates
- [ ] Add batch endpoint for multiple verses
- [ ] Implement verse comparison across translations
- [ ] Add tafsir (commentary) endpoints

---

## License

Refer to main project LICENSE file.
