# Embedding and Semantic Search Examples

This document provides examples of using the embedding generation and semantic search functionality.

## Prerequisites

1. Set up OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Update `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
```

## Generating Embeddings

### Create Embeddings for All Verses

```bash
curl -X POST http://localhost:8000/api/v1/admin/embed/verse \
  -H "Authorization: Bearer dev_admin_token_change_in_production" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "model": "text-embedding-ada-002"
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Successfully embedded 6236 verses in en",
  "verses_embedded": 6236
}
```

### Create Embeddings for Specific Verses

```bash
curl -X POST http://localhost:8000/api/v1/admin/embed/verse \
  -H "Authorization: Bearer dev_admin_token_change_in_production" \
  -H "Content-Type: application/json" \
  -d '{
    "verse_ids": [1, 2, 3, 4, 5],
    "language": "en",
    "model": "text-embedding-ada-002"
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Successfully embedded 5 verses in en",
  "verses_embedded": 5
}
```

### Create Embeddings for Arabic Text

```bash
curl -X POST http://localhost:8000/api/v1/admin/embed/verse \
  -H "Authorization: Bearer dev_admin_token_change_in_production" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "ar",
    "model": "text-embedding-ada-002"
  }'
```

## Semantic Search Examples

### Simple Semantic Search

Find verses semantically similar to a query:

```bash
curl "http://localhost:8000/api/v1/search?q=patience+in+hardship&search_type=semantic&lang=en&limit=10"
```

Response:
```json
{
  "query": "patience in hardship",
  "search_type": "semantic",
  "language": "en",
  "total_results": 10,
  "results": [
    {
      "verse_id": 155,
      "verse_number": 155,
      "surah_number": 2,
      "surah_name": "Al-Baqarah",
      "text_arabic": "وَلَنَبْلُوَنَّكُم بِشَىْءٍۢ مِّنَ ٱلْخَوْفِ وَٱلْجُوعِ وَنَقْصٍۢ مِّنَ ٱلْأَمْوَٰلِ وَٱلْأَنفُسِ وَٱلثَّمَرَٰتِ ۗ وَبَشِّرِ ٱلصَّـٰبِرِينَ",
      "text_transliteration": "Walanabluwannakum bishayin mina alkhawfi waaljuAAi wanaqsin mina al-amwali waal-anfusi waalththamarati wabashshiri alssabireena",
      "translations": [
        {
          "id": 155,
          "language": "en",
          "translator": "Sahih International",
          "text": "And We will surely test you with something of fear and hunger and a loss of wealth and lives and fruits, but give good tidings to the patient,",
          "license": "Public Domain",
          "source": "quran.com"
        }
      ],
      "score": 0.92,
      "match_type": "semantic"
    }
  ]
}
```

### Conceptual Queries

Search for abstract concepts:

```bash
# Find verses about gratitude
curl "http://localhost:8000/api/v1/search?q=being+thankful+to+God&search_type=semantic&lang=en&limit=5"

# Find verses about forgiveness
curl "http://localhost:8000/api/v1/search?q=divine+mercy+and+forgiveness&search_type=semantic&lang=en&limit=5"

# Find verses about justice
curl "http://localhost:8000/api/v1/search?q=fairness+and+justice&search_type=semantic&lang=en&limit=5"
```

### Hybrid Search (Lexical + Semantic)

Combines exact matching, fuzzy search, and semantic search:

```bash
curl "http://localhost:8000/api/v1/search?q=charity&search_type=hybrid&lang=en&limit=20"
```

This will return results from:
1. Exact matches (score weight: 1.0)
2. Fuzzy matches (score weight: 0.8)
3. Semantic matches (score weight: 0.7)

### Arabic Semantic Search

Search in Arabic text:

```bash
curl "http://localhost:8000/api/v1/search?q=الصبر&search_type=semantic&lang=ar&limit=10"
```

## Example Use Cases

### 1. Topic-Based Discovery

Find all verses related to a specific topic without knowing exact keywords:

```bash
# Prayer and worship
curl "http://localhost:8000/api/v1/search?q=worship+prayer+devotion&search_type=semantic&lang=en"

# Family values
curl "http://localhost:8000/api/v1/search?q=parents+children+family&search_type=semantic&lang=en"

# Social justice
curl "http://localhost:8000/api/v1/search?q=helping+poor+social+justice&search_type=semantic&lang=en"
```

### 2. Question-Based Search

Find verses that answer specific questions:

```bash
# What does the Quran say about...
curl "http://localhost:8000/api/v1/search?q=what+happens+after+death&search_type=semantic&lang=en"

curl "http://localhost:8000/api/v1/search?q=how+to+be+a+good+person&search_type=semantic&lang=en"

curl "http://localhost:8000/api/v1/search?q=purpose+of+life&search_type=semantic&lang=en"
```

### 3. Thematic Study

Compare different aspects of a theme:

```bash
# Find verses about different types of charity
curl "http://localhost:8000/api/v1/search?q=giving+money+to+poor&search_type=semantic&lang=en"
curl "http://localhost:8000/api/v1/search?q=helping+orphans&search_type=semantic&lang=en"
curl "http://localhost:8000/api/v1/search?q=feeding+hungry&search_type=semantic&lang=en"
```

## Python Client Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
ADMIN_TOKEN = "dev_admin_token_change_in_production"

def create_embeddings(verse_ids=None, language="en"):
    """Create embeddings for verses"""
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "language": language,
        "model": "text-embedding-ada-002"
    }
    
    if verse_ids:
        data["verse_ids"] = verse_ids
    
    response = requests.post(
        f"{API_BASE}/admin/embed/verse",
        headers=headers,
        json=data
    )
    
    return response.json()

def semantic_search(query, language="en", limit=10):
    """Perform semantic search"""
    params = {
        "q": query,
        "search_type": "semantic",
        "lang": language,
        "limit": limit
    }
    
    response = requests.get(f"{API_BASE}/search", params=params)
    return response.json()

def hybrid_search(query, language="en", limit=20):
    """Perform hybrid search"""
    params = {
        "q": query,
        "search_type": "hybrid",
        "lang": language,
        "limit": limit
    }
    
    response = requests.get(f"{API_BASE}/search", params=params)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Generate embeddings for first 10 verses
    print("Creating embeddings...")
    result = create_embeddings(verse_ids=list(range(1, 11)))
    print(f"Embedded {result['verses_embedded']} verses")
    
    # Semantic search
    print("\nSearching for verses about patience...")
    results = semantic_search("patience and perseverance")
    
    for r in results["results"][:3]:
        print(f"\nSurah {r['surah_number']}:{r['verse_number']} - {r['surah_name']}")
        print(f"Score: {r['score']:.2f}")
        if r['translations']:
            print(f"Translation: {r['translations'][0]['text']}")
```

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8000/api/v1';
const ADMIN_TOKEN = 'dev_admin_token_change_in_production';

async function createEmbeddings(verseIds = null, language = 'en') {
  const data = {
    language,
    model: 'text-embedding-ada-002'
  };
  
  if (verseIds) {
    data.verse_ids = verseIds;
  }
  
  const response = await axios.post(
    `${API_BASE}/admin/embed/verse`,
    data,
    {
      headers: {
        'Authorization': `Bearer ${ADMIN_TOKEN}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return response.data;
}

async function semanticSearch(query, language = 'en', limit = 10) {
  const response = await axios.get(`${API_BASE}/search`, {
    params: {
      q: query,
      search_type: 'semantic',
      lang: language,
      limit
    }
  });
  
  return response.data;
}

async function hybridSearch(query, language = 'en', limit = 20) {
  const response = await axios.get(`${API_BASE}/search`, {
    params: {
      q: query,
      search_type: 'hybrid',
      lang: language,
      limit
    }
  });
  
  return response.data;
}

// Example usage
async function main() {
  try {
    // Generate embeddings
    console.log('Creating embeddings...');
    const embedResult = await createEmbeddings([1, 2, 3, 4, 5]);
    console.log(`Embedded ${embedResult.verses_embedded} verses`);
    
    // Semantic search
    console.log('\nSearching for verses about mercy...');
    const searchResults = await semanticSearch('divine mercy and compassion');
    
    searchResults.results.slice(0, 3).forEach(result => {
      console.log(`\nSurah ${result.surah_number}:${result.verse_number} - ${result.surah_name}`);
      console.log(`Score: ${result.score.toFixed(2)}`);
      if (result.translations.length > 0) {
        console.log(`Translation: ${result.translations[0].text}`);
      }
    });
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

## Performance Tips

1. **Batch Embedding Generation**: Generate embeddings in batches of 100 verses for optimal performance
2. **Language-Specific Embeddings**: Create separate embeddings for Arabic and English for better accuracy
3. **Cache Results**: Consider caching frequently searched queries
4. **Limit Results**: Use reasonable limit values (10-20) for better performance
5. **Monitor API Costs**: OpenAI embeddings API has usage costs, monitor your usage

## Troubleshooting

### OpenAI API Key Not Configured

```json
{
  "detail": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
}
```

**Solution**: Set the `OPENAI_API_KEY` environment variable

### No Embeddings Found

If semantic search returns no results, embeddings may not have been generated yet.

**Solution**: Generate embeddings first using the admin endpoint

### Rate Limiting

OpenAI API has rate limits. If you encounter rate limit errors, reduce batch sizes or add delays between requests.

## API Cost Estimation

- **Embedding Model**: text-embedding-ada-002
- **Cost**: $0.0001 per 1K tokens
- **Average verse**: ~50 tokens
- **Total Quran**: ~6,236 verses = ~$0.03 for all verses

Costs are minimal for this application, but may vary based on usage patterns.
