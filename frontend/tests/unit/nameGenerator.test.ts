import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  suggestNames,
  getEntityTypes,
  getSubtypes,
  getOrigins,
  getThemes,
  getNameById,
  searchNames,
  createFavorite,
  getUserFavorites,
  deleteFavorite,
} from '../../lib/api';

// Mock fetch globally
global.fetch = vi.fn();

describe('Name Generator API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('suggestNames', () => {
    it('should fetch name suggestions from backend', async () => {
      const mockRequest = {
        entity_type: 'baby',
        gender: 'male',
        origin: 'Arabic',
        max_results: 20,
      };

      const mockResponse = {
        request: mockRequest,
        suggestions: [
          {
            id: 1,
            name: 'Muhammad',
            entity_type: 'baby',
            gender: 'male',
            meaning: 'Praised one',
            origin: 'Arabic',
            relevance_score: 0.95,
          },
        ],
        total: 1,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await suggestNames(mockRequest);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/suggest',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockRequest),
        })
      );
    });

    it('should throw error when backend request fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(
        suggestNames({ entity_type: 'baby' })
      ).rejects.toThrow('Failed to get name suggestions');
    });
  });

  describe('getEntityTypes', () => {
    it('should fetch available entity types', async () => {
      const mockTypes = ['baby', 'pet', 'vehicle', 'company', 'toy'];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTypes,
      });

      const result = await getEntityTypes();
      expect(result).toEqual(mockTypes);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/entity-types'
      );
    });
  });

  describe('getSubtypes', () => {
    it('should fetch subtypes for entity type', async () => {
      const mockSubtypes = ['dog', 'cat'];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSubtypes,
      });

      const result = await getSubtypes('pet');
      expect(result).toEqual(mockSubtypes);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/subtypes/pet'
      );
    });
  });

  describe('getOrigins', () => {
    it('should fetch available origins', async () => {
      const mockOrigins = ['Arabic', 'English', 'Latin'];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOrigins,
      });

      const result = await getOrigins();
      expect(result).toEqual(mockOrigins);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/origins'
      );
    });
  });

  describe('getThemes', () => {
    it('should fetch available themes', async () => {
      const mockThemes = ['classic', 'modern', 'playful'];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockThemes,
      });

      const result = await getThemes();
      expect(result).toEqual(mockThemes);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/themes'
      );
    });
  });

  describe('getNameById', () => {
    it('should fetch name details by ID', async () => {
      const mockName = {
        id: 1,
        name: 'Muhammad',
        entity_type: 'baby',
        gender: 'male',
        meaning: 'Praised one',
        origin: 'Arabic',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockName,
      });

      const result = await getNameById(1);
      expect(result).toEqual(mockName);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/names/1'
      );
    });

    it('should throw error when name not found', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(getNameById(9999)).rejects.toThrow('Failed to fetch name');
    });
  });

  describe('searchNames', () => {
    it('should search names by query', async () => {
      const mockResults = [
        {
          id: 1,
          name: 'Max',
          entity_type: 'pet',
          gender: 'male',
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults,
      });

      const result = await searchNames('Max');
      expect(result).toEqual(mockResults);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('query=Max')
      );
    });

    it('should include entity type filter when provided', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await searchNames('test', 'pet');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('entity_type=pet')
      );
    });
  });

  describe('createFavorite', () => {
    it('should create a new favorite', async () => {
      const favoriteData = {
        name_entity_id: 1,
        user_id: 'test_user',
        note: 'Love this name!',
      };

      const mockResponse = {
        id: 1,
        ...favoriteData,
        created_at: '2024-01-01T00:00:00Z',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await createFavorite(favoriteData);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/favorites',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(favoriteData),
        })
      );
    });
  });

  describe('getUserFavorites', () => {
    it('should fetch user favorites', async () => {
      const mockFavorites = [
        {
          id: 1,
          name_entity_id: 1,
          user_id: 'test_user',
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockFavorites,
      });

      const result = await getUserFavorites('test_user');
      expect(result).toEqual(mockFavorites);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/favorites/test_user'
      );
    });
  });

  describe('deleteFavorite', () => {
    it('should delete a favorite', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Favorite removed successfully' }),
      });

      await deleteFavorite(1, 'test_user');
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/names/favorites/1?user_id=test_user',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should throw error when delete fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(
        deleteFavorite(9999, 'test_user')
      ).rejects.toThrow('Failed to delete favorite');
    });
  });
});
