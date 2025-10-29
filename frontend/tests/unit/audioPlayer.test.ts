import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { GaplessAudioPlayer } from '../../lib/audioPlayer';

describe('GaplessAudioPlayer', () => {
  let player: GaplessAudioPlayer;
  let mockOnTrackChange: ReturnType<typeof vi.fn>;
  let mockOnPlayStateChange: ReturnType<typeof vi.fn>;
  let mockOnError: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnTrackChange = vi.fn();
    mockOnPlayStateChange = vi.fn();
    mockOnError = vi.fn();

    player = new GaplessAudioPlayer({
      onTrackChange: mockOnTrackChange,
      onPlayStateChange: mockOnPlayStateChange,
      onError: mockOnError,
    });
  });

  afterEach(() => {
    player.destroy();
  });

  describe('constructor', () => {
    it('should create player instance', () => {
      expect(player).toBeDefined();
      expect(player.getIsPlaying()).toBe(false);
      expect(player.getCurrentVerseIndex()).toBe(0);
    });

    it('should work with no config', () => {
      const simplePlayer = new GaplessAudioPlayer();
      expect(simplePlayer).toBeDefined();
      simplePlayer.destroy();
    });
  });

  describe('initialization', () => {
    it('should initialize with verse URLs', async () => {
      const urls = ['verse1.mp3', 'verse2.mp3', 'verse3.mp3'];
      
      // Mock fetch to avoid actual network calls
      global.fetch = vi.fn().mockResolvedValue({
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
      });

      await player.initialize(urls);
      
      expect(player.getCurrentVerseIndex()).toBe(0);
    });

    it('should handle empty URL array', async () => {
      await player.initialize([]);
      expect(player.getCurrentVerseIndex()).toBe(0);
    });
  });

  describe('state management', () => {
    it('should track playing state correctly', () => {
      expect(player.getIsPlaying()).toBe(false);
    });

    it('should track current verse index', () => {
      expect(player.getCurrentVerseIndex()).toBe(0);
    });
  });

  describe('playVerse', () => {
    it('should throw error for invalid verse index', async () => {
      const urls = ['verse1.mp3', 'verse2.mp3'];
      global.fetch = vi.fn().mockResolvedValue({
        arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
      });

      await player.initialize(urls);

      await expect(player.playVerse(-1)).rejects.toThrow('Invalid verse index');
      await expect(player.playVerse(5)).rejects.toThrow('Invalid verse index');
    });
  });

  describe('pause and stop', () => {
    it('should pause playback', () => {
      player.pause();
      expect(player.getIsPlaying()).toBe(false);
    });

    it('should stop playback and reset index', () => {
      player.stop();
      expect(player.getIsPlaying()).toBe(false);
      expect(player.getCurrentVerseIndex()).toBe(0);
    });

    it('should call onPlayStateChange callback on pause', () => {
      player.pause();
      expect(mockOnPlayStateChange).toHaveBeenCalledWith(false);
    });
  });

  describe('destroy', () => {
    it('should clean up resources', () => {
      player.destroy();
      expect(player.getIsPlaying()).toBe(false);
    });

    it('should not throw when called multiple times', () => {
      expect(() => {
        player.destroy();
        player.destroy();
      }).not.toThrow();
    });
  });

  describe('error handling', () => {
    it('should handle audio loading errors', async () => {
      const urls = ['invalid-url.mp3'];
      
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await player.initialize(urls).catch(() => {
        // Expected to fail
      });

      // Error callback should be called during initialization
      expect(mockOnError).toHaveBeenCalled();
    });

    it('should throw error when playing without initialization', async () => {
      await expect(player.play()).rejects.toThrow('Audio player not initialized');
    });
  });

  describe('callbacks', () => {
    it('should respect optional callbacks', async () => {
      const playerNoCallbacks = new GaplessAudioPlayer();
      
      // Should not throw without callbacks
      expect(() => {
        playerNoCallbacks.pause();
        playerNoCallbacks.stop();
      }).not.toThrow();

      playerNoCallbacks.destroy();
    });
  });

  describe('edge cases', () => {
    it('should handle rapid play/pause toggling', () => {
      expect(() => {
        player.pause();
        player.pause();
        player.stop();
        player.pause();
      }).not.toThrow();
    });

    it('should maintain state after multiple operations', async () => {
      player.pause();
      expect(player.getIsPlaying()).toBe(false);
      
      player.stop();
      expect(player.getCurrentVerseIndex()).toBe(0);
      
      player.pause();
      expect(player.getIsPlaying()).toBe(false);
    });
  });
});
