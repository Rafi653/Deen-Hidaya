import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  addBookmark,
  removeBookmark,
  isBookmarked,
  getBookmarks,
  Bookmark,
} from '../../lib/bookmarks';

describe('Bookmarks Library', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('getBookmarks', () => {
    it('should return empty array when no bookmarks exist', () => {
      const bookmarks = getBookmarks();
      expect(bookmarks).toEqual([]);
    });

    it('should return stored bookmarks', () => {
      const mockBookmarks: Bookmark[] = [
        {
          surahNumber: 1,
          verseNumber: 1,
          surahName: 'Al-Fatihah',
          timestamp: '2025-10-29T00:00:00.000Z',
        },
      ];
      localStorage.setItem('deen-hidaya-bookmarks', JSON.stringify(mockBookmarks));

      const bookmarks = getBookmarks();
      expect(bookmarks).toEqual(mockBookmarks);
    });

    it('should return empty array for invalid JSON', () => {
      localStorage.setItem('deen-hidaya-bookmarks', 'invalid-json');
      const bookmarks = getBookmarks();
      expect(bookmarks).toEqual([]);
    });
  });

  describe('addBookmark', () => {
    it('should add a new bookmark', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      const bookmarks = getBookmarks();

      expect(bookmarks).toHaveLength(1);
      expect(bookmarks[0]).toEqual(bookmark);
    });

    it('should not add duplicate bookmarks', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      addBookmark(bookmark);

      const bookmarks = getBookmarks();
      expect(bookmarks).toHaveLength(1);
    });

    it('should add multiple different bookmarks', () => {
      const bookmark1: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      const bookmark2: Bookmark = {
        surahNumber: 2,
        verseNumber: 5,
        surahName: 'Al-Baqarah',
        timestamp: '2025-10-29T01:00:00.000Z',
      };

      addBookmark(bookmark1);
      addBookmark(bookmark2);

      const bookmarks = getBookmarks();
      expect(bookmarks).toHaveLength(2);
    });
  });

  describe('removeBookmark', () => {
    it('should remove an existing bookmark', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      expect(getBookmarks()).toHaveLength(1);

      removeBookmark(1, 1);
      expect(getBookmarks()).toHaveLength(0);
    });

    it('should not affect other bookmarks', () => {
      const bookmark1: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      const bookmark2: Bookmark = {
        surahNumber: 2,
        verseNumber: 5,
        surahName: 'Al-Baqarah',
        timestamp: '2025-10-29T01:00:00.000Z',
      };

      addBookmark(bookmark1);
      addBookmark(bookmark2);

      removeBookmark(1, 1);

      const bookmarks = getBookmarks();
      expect(bookmarks).toHaveLength(1);
      expect(bookmarks[0]).toEqual(bookmark2);
    });

    it('should handle removing non-existent bookmark', () => {
      removeBookmark(999, 999);
      expect(getBookmarks()).toHaveLength(0);
    });
  });

  describe('isBookmarked', () => {
    it('should return true for bookmarked verse', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      expect(isBookmarked(1, 1)).toBe(true);
    });

    it('should return false for non-bookmarked verse', () => {
      expect(isBookmarked(1, 1)).toBe(false);
    });

    it('should return false after removing bookmark', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      expect(isBookmarked(1, 1)).toBe(true);

      removeBookmark(1, 1);
      expect(isBookmarked(1, 1)).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle large numbers of bookmarks', () => {
      for (let i = 1; i <= 100; i++) {
        addBookmark({
          surahNumber: i,
          verseNumber: 1,
          surahName: `Surah ${i}`,
          timestamp: new Date().toISOString(),
        });
      }

      const bookmarks = getBookmarks();
      expect(bookmarks).toHaveLength(100);
    });

    it('should preserve bookmark data types', () => {
      const bookmark: Bookmark = {
        surahNumber: 1,
        verseNumber: 1,
        surahName: 'Al-Fatihah',
        timestamp: '2025-10-29T00:00:00.000Z',
      };

      addBookmark(bookmark);
      const retrieved = getBookmarks()[0];

      expect(typeof retrieved.surahNumber).toBe('number');
      expect(typeof retrieved.verseNumber).toBe('number');
      expect(typeof retrieved.surahName).toBe('string');
      expect(typeof retrieved.timestamp).toBe('string');
    });
  });
});
