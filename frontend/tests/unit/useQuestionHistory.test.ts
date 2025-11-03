import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useQuestionHistory } from '../../lib/useQuestionHistory';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true
});

describe('useQuestionHistory', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('should initialize with empty history', () => {
    const { result } = renderHook(() => useQuestionHistory());
    expect(result.current.history).toEqual([]);
  });

  it('should add a question to history', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('What is patience?');
    });

    expect(result.current.history).toHaveLength(1);
    expect(result.current.history[0].question).toBe('What is patience?');
    expect(result.current.history[0].id).toBeTruthy();
    expect(result.current.history[0].timestamp).toBeTruthy();
  });

  it('should trim whitespace from questions', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('  What is charity?  ');
    });

    expect(result.current.history[0].question).toBe('What is charity?');
  });

  it('should not add empty questions', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('');
    });

    expect(result.current.history).toHaveLength(0);

    act(() => {
      result.current.addQuestion('   ');
    });

    expect(result.current.history).toHaveLength(0);
  });

  it('should remove duplicate questions (case-insensitive)', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('What is patience?');
    });

    act(() => {
      result.current.addQuestion('What Is Patience?');
    });

    expect(result.current.history).toHaveLength(1);
    expect(result.current.history[0].question).toBe('What Is Patience?');
  });

  it('should maintain maximum history size of 10 items', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      for (let i = 1; i <= 15; i++) {
        result.current.addQuestion(`Question ${i}`);
      }
    });

    expect(result.current.history).toHaveLength(10);
    expect(result.current.history[0].question).toBe('Question 15');
    expect(result.current.history[9].question).toBe('Question 6');
  });

  it('should add new questions at the beginning', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('First question');
    });

    act(() => {
      result.current.addQuestion('Second question');
    });

    expect(result.current.history[0].question).toBe('Second question');
    expect(result.current.history[1].question).toBe('First question');
  });

  it('should clear all history', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('Question 1');
      result.current.addQuestion('Question 2');
    });

    expect(result.current.history).toHaveLength(2);

    act(() => {
      result.current.clearHistory();
    });

    expect(result.current.history).toHaveLength(0);
  });

  it('should remove a specific question by id', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('Question 1');
      result.current.addQuestion('Question 2');
      result.current.addQuestion('Question 3');
    });

    const idToRemove = result.current.history[1].id;

    act(() => {
      result.current.removeQuestion(idToRemove);
    });

    expect(result.current.history).toHaveLength(2);
    expect(result.current.history.find((item) => item.id === idToRemove)).toBeUndefined();
  });

  it('should persist history to localStorage', () => {
    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('Persisted question');
    });

    const stored = localStorageMock.getItem('qa_question_history');
    expect(stored).toBeTruthy();

    const parsed = JSON.parse(stored!);
    expect(parsed).toHaveLength(1);
    expect(parsed[0].question).toBe('Persisted question');
  });

  it('should load history from localStorage on mount', () => {
    const mockHistory = [
      { id: '1', question: 'Loaded question 1', timestamp: Date.now() },
      { id: '2', question: 'Loaded question 2', timestamp: Date.now() }
    ];

    localStorageMock.setItem('qa_question_history', JSON.stringify(mockHistory));

    const { result } = renderHook(() => useQuestionHistory());

    // Wait for useEffect to run
    expect(result.current.history).toHaveLength(2);
    expect(result.current.history[0].question).toBe('Loaded question 1');
    expect(result.current.history[1].question).toBe('Loaded question 2');
  });

  it('should handle localStorage errors gracefully', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock localStorage to throw error
    const originalSetItem = localStorageMock.setItem;
    localStorageMock.setItem = () => {
      throw new Error('Storage quota exceeded');
    };

    const { result } = renderHook(() => useQuestionHistory());

    act(() => {
      result.current.addQuestion('Test question');
    });

    expect(consoleErrorSpy).toHaveBeenCalled();

    // Restore
    localStorageMock.setItem = originalSetItem;
    consoleErrorSpy.mockRestore();
  });

  it('should handle corrupted localStorage data', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    localStorageMock.setItem('qa_question_history', 'invalid json');

    const { result } = renderHook(() => useQuestionHistory());

    expect(result.current.history).toEqual([]);
    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });
});
