# Translation API Investigation - ID 213 Issue

## Problem Statement
Translation ID 213 (Telugu translation by Abdul Hafeez & Mohammed Abdul Haq) is not working properly when fetching from api.quran.com. Need to investigate the source API and find reliable translation sources.

## API Investigation

### Current API: api.quran.com

**Endpoint**: `https://api.quran.com/api/v4/verses/by_chapter/{chapter}`

**Parameters**:
- `translations`: Comma-separated translation IDs
- `language`: UI language for metadata
- `fields`: Specific fields to return

### Known Translation IDs

#### English Translations
- **131**: Dr. Mustafa Khattab, The Clear Quran (Recommended) ✅
- **20**: Saheeh International ✅
- **85**: Marmaduke Pickthall ✅
- **19**: Abdullah Yusuf Ali ✅
- **22**: Muhammad Asad ✅

#### Telugu Translations
- **213**: Abdul Hafeez & Mohammed Abdul Haq ⚠️ (Reported not working)
- **214**: Muhammad Abdul Haleem ❓ (Need to verify)

#### Other Languages
- **140**: Muhammad Isa Garcia (Spanish) ✅
- **97**: Abul A'ala Maududi (Urdu) ✅
- **38**: Muhammad Hamidullah (French) ✅

## Issue Analysis

### Possible Causes for ID 213 Not Working

1. **Translation Removed/Deprecated**
   - The translation may have been removed from the API
   - License or copyright issues
   - Quality concerns

2. **API Changes**
   - Translation ID changed
   - Different endpoint required
   - API version updated

3. **Language Code Issues**
   - Our code maps ID 213 to language "te" (Telugu)
   - API might use different language codes
   - Metadata mismatch

4. **Incomplete Data**
   - Not all verses have Telugu translation
   - Missing verses show as empty
   - Partial translation coverage

## Verification Steps

### 1. Check Available Translations
```bash
# Get list of all available translations
curl "https://api.quran.com/api/v4/resources/translations" | jq '.translations[] | select(.language_name | contains("Telugu"))'
```

### 2. Test Specific Translation
```bash
# Try fetching with translation ID 213
curl "https://api.quran.com/api/v4/verses/by_chapter/1?translations=213" | jq '.verses[0].translations'
```

### 3. Verify Translation Metadata
```bash
# Get details about translation 213
curl "https://api.quran.com/api/v4/resources/translations/213" | jq '.'
```

## Alternative Translation Sources

### 1. Tanzil.net
**API**: http://api.tanzil.net/
- **Pros**: Well-established, multiple translations, good documentation
- **Cons**: Limited Telugu translations, older API
- **Status**: Backup option

**Example**:
```bash
curl "http://api.tanzil.net/quran?type=text&quran=quran-simple&chapter=1"
```

### 2. GlobalQuran.com API
**API**: Various endpoints for translations
- **Pros**: Multiple language support
- **Cons**: Less documentation, unclear licensing
- **Status**: Need more research

### 3. Al-Quran Cloud
**API**: https://alquran.cloud/api
- **Pros**: Good documentation, multiple editions
- **Cons**: Might have same limitations as api.quran.com
- **Status**: Worth investigating

**Example**:
```bash
curl "https://api.alquran.cloud/v1/surah/1/editions/quran-unicode,en.sahih"
```

### 4. IslamicNetwork/AlAdhan API
**API**: https://aladhan.com/quran-api
- **Pros**: RESTful, well-maintained
- **Cons**: Focus on prayer times, limited Quran API
- **Status**: Backup option

## Recommended Solution

### Approach 1: Fix Current API Usage (Recommended)
1. **Verify translation availability** via API
2. **Update translation ID** if it changed
3. **Add error handling** for missing translations
4. **Implement fallback** to default translation

```python
def fetch_translation_with_fallback(surah_number, translation_ids):
    """Fetch translations with fallback mechanism"""
    primary_ids = translation_ids
    fallback_ids = [131, 20]  # English fallbacks
    
    # Try primary translations
    result = fetch_surah_verses(surah_number, primary_ids)
    
    # Check if translations are present
    if not result or not has_translations(result):
        logger.warning(f"Primary translations {primary_ids} not available")
        result = fetch_surah_verses(surah_number, fallback_ids)
    
    return result
```

### Approach 2: Multi-Source Strategy
1. **Primary**: api.quran.com (English translations)
2. **Secondary**: Alternative APIs for Telugu
3. **Fallback**: English-only if Telugu unavailable

```python
TRANSLATION_SOURCES = {
    'en': {
        'api': 'api.quran.com',
        'ids': [131, 20],
        'primary': True
    },
    'te': {
        'api': 'api.quran.com',
        'ids': [213],
        'primary': False,
        'fallback_api': 'alternative-api.com',
        'fallback_ids': [...]
    }
}
```

### Approach 3: Pre-downloaded Translations
1. **Download** verified translation datasets
2. **Store** in `data/translations/` directory
3. **Ingest** directly without API calls
4. **Update** periodically from trusted sources

**Benefits**:
- No API dependency
- Always available
- Faster ingestion
- Consistent data

**Sources for Pre-downloaded Translations**:
- Tanzil.net datasets
- Quran.com exports
- Community-maintained repositories

## Implementation Plan

### Phase 1: Immediate Fix (Priority: High)
1. Verify translation ID 213 status via API
2. If unavailable, remove from defaults
3. Update TRANSLATION_METADATA in scrape_quran.py
4. Add logging for missing translations
5. Test with available Telugu translations

### Phase 2: Robust Error Handling (Priority: High)
1. Add translation availability check
2. Implement fallback mechanism
3. Log missing translations for monitoring
4. Update documentation with known limitations

### Phase 3: Alternative Sources (Priority: Medium)
1. Research alternative Telugu translation sources
2. Implement multi-source support if needed
3. Consider pre-downloaded translation option
4. Document translation sources and licenses

### Phase 4: Monitoring (Priority: Low)
1. Add API health checks
2. Monitor translation availability
3. Alert on translation fetch failures
4. Regular data quality audits

## Code Changes Needed

### 1. Update scrape_quran.py

```python
# Add translation verification
def verify_translation_availability(translation_id):
    """Check if translation is available in API"""
    endpoint = f"resources/translations/{translation_id}"
    result = self._make_request(endpoint)
    return result is not None

# Update DEFAULT_TRANSLATIONS after verification
DEFAULT_TRANSLATIONS = [131]  # Only English (Dr. Khattab) as default

# Add Telugu if available
if verify_translation_availability(213):
    DEFAULT_TRANSLATIONS.append(213)
else:
    logger.warning("Telugu translation (ID 213) not available")
```

### 2. Update fix_translations.py

```python
def fix_translations(start_surah=1, end_surah=114, force_rescrape=False):
    """Fix translations with proper error handling"""
    
    # Verify translation availability first
    available_translations = verify_available_translations([131, 213])
    
    if 213 not in available_translations:
        logger.warning("Telugu translation not available, using English only")
        translation_ids = [131]
    else:
        translation_ids = [131, 213]
    
    # Continue with scraping...
```

### 3. Add Translation Health Check

```python
# backend/translation_health_check.py
def check_translation_health():
    """Check health of all configured translations"""
    results = {}
    for trans_id in [131, 20, 213]:
        try:
            # Fetch sample verse with translation
            result = fetch_verse(1, 1, translation_ids=[trans_id])
            results[trans_id] = {
                'available': True,
                'verses_fetched': len(result['verses'])
            }
        except Exception as e:
            results[trans_id] = {
                'available': False,
                'error': str(e)
            }
    return results
```

## Testing Strategy

### Manual Testing
```bash
# Test English translation (should work)
curl "https://api.quran.com/api/v4/verses/by_chapter/1?translations=131" 

# Test Telugu translation (verify status)
curl "https://api.quran.com/api/v4/verses/by_chapter/1?translations=213"

# Test multiple translations
curl "https://api.quran.com/api/v4/verses/by_chapter/1?translations=131,213"
```

### Automated Testing
```python
def test_translation_availability():
    """Test that configured translations are available"""
    scraper = QuranScraper()
    
    for trans_id in [131, 213]:
        result = scraper.fetch_surah_verses(1, translation_ids=[trans_id])
        assert result is not None
        assert 'verses' in result
        assert len(result['verses']) > 0
        assert len(result['verses'][0].get('translations', [])) > 0
```

## Documentation Updates

1. **README.md**: Note about Telugu translation availability
2. **QUICKFIX_GUIDE.md**: Update translation fix steps
3. **API_DOCUMENTATION.md**: Document available translations
4. **scrape_quran.py**: Add docstring notes about translation IDs

## Conclusion

**Immediate Action**: Verify translation ID 213 status and update code accordingly.

**Short-term**: Implement robust error handling and fallback mechanisms.

**Long-term**: Consider multi-source approach or pre-downloaded translations for reliability.

**Key Principle**: Always have a working fallback (English translations) even if specific language translations are unavailable.

## Next Steps

1. [ ] Verify translation 213 availability via API
2. [ ] Update TRANSLATION_METADATA with accurate information
3. [ ] Implement fallback to English-only if Telugu unavailable
4. [ ] Add translation health check script
5. [ ] Update documentation with findings
6. [ ] Test translation scraping end-to-end
7. [ ] Consider pre-downloaded translation option for reliability
