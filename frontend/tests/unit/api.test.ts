import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  fetchSurahs,
  fetchSurahDetail,
  askQuestion,
  fetchAvailableTranslations,
} from '../../lib/api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Library', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchSurahs', () => {
    it('should fetch surahs from backend', async () => {
      const mockSurahs = [
        {
          id: 1,
          number: 1,
          name_arabic: 'الفاتحة',
          name_english: 'Al-Fatihah',
          name_transliteration: 'The Opening',
          revelation_place: 'Makkah',
          total_verses: 7,
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSurahs,
      });

      const result = await fetchSurahs();
      expect(result).toEqual(mockSurahs);
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/surahs');
    });

    it('should return mock data when backend is unavailable', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const result = await fetchSurahs();
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
    });

    it('should return mock data on network error', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const result = await fetchSurahs();
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('fetchSurahDetail', () => {
    it('should fetch surah detail from backend', async () => {
      const mockSurah = {
        id: 1,
        number: 1,
        name_arabic: 'الفاتحة',
        name_english: 'Al-Fatihah',
        name_transliteration: 'The Opening',
        revelation_place: 'Makkah',
        total_verses: 7,
        verses: [
          {
            id: 1,
            verse_number: 1,
            text_arabic: 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
            text_transliteration: 'Bismillahir-Rahmanir-Rahim',
            sajda: false,
            translations: [],
          },
        ],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSurah,
      });

      const result = await fetchSurahDetail(1);
      expect(result).toEqual(mockSurah);
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/surahs/1');
    });

    it('should return mock data when backend is unavailable', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      const result = await fetchSurahDetail(1);
      expect(result).toBeDefined();
      expect(result.number).toBe(1);
      expect(result.verses).toBeDefined();
    });

    it('should return mock data on network error', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const result = await fetchSurahDetail(1);
      expect(result).toBeDefined();
    });
  });

  describe('askQuestion', () => {
    it('should send question to backend', async () => {
      const mockResponse = {
        question: 'What is patience?',
        answer: 'Patience is a virtue...',
        cited_verses: [],
        confidence_score: 0.95,
        processing_time_ms: 250,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await askQuestion({
        question: 'What is patience?',
        max_verses: 3,
      });

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/qa/ask',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: 'What is patience?', max_verses: 3 }),
        })
      );
    });

    it('should return mock data when backend is unavailable', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const result = await askQuestion({ question: 'Test question' });
      expect(result).toBeDefined();
      expect(result.question).toBe('Test question');
      expect(result.answer).toBeDefined();
      expect(result.cited_verses).toBeDefined();
    });

    it('should handle network errors gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const result = await askQuestion({ question: 'Test question' });
      expect(result).toBeDefined();
      expect(result.question).toBe('Test question');
    });

    it('should include optional parameters', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ question: 'test', answer: 'answer', cited_verses: [] }),
      });

      await askQuestion({
        question: 'Test',
        language: 'en',
        max_verses: 5,
      });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/qa/ask',
        expect.objectContaining({
          body: JSON.stringify({ question: 'Test', language: 'en', max_verses: 5 }),
        })
      );
    });
  });

  describe('fetchAvailableTranslations', () => {
    it('should fetch available translations', async () => {
      const mockTranslations = [
        { language: 'en', translator: 'Sahih International', source: 'api.quran.com' },
        { language: 'te', translator: 'Telugu Translation' },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTranslations,
      });

      const result = await fetchAvailableTranslations();
      expect(result).toEqual(mockTranslations);
      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/translations');
    });

    it('should throw error when backend fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(fetchAvailableTranslations()).rejects.toThrow(
        'Failed to fetch translations'
      );
    });
  });

  describe('API configuration', () => {
    it('should use correct base URL', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await fetchSurahs();
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8000')
      );
    });
  });

  describe('error handling', () => {
    it('should handle malformed JSON responses', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(fetchAvailableTranslations()).rejects.toThrow();
    });

    it('should handle timeout errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Timeout'));

      const result = await fetchSurahs();
      // Should return mock data
      expect(result).toBeDefined();
    });
  });
});
