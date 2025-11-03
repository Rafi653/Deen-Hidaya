import { useState, useEffect } from 'react';

const QUESTION_HISTORY_KEY = 'qa_question_history';
const MAX_HISTORY_SIZE = 10;

export interface QuestionHistoryItem {
  id: string;
  question: string;
  timestamp: number;
}

export function useQuestionHistory() {
  const [history, setHistory] = useState<QuestionHistoryItem[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(QUESTION_HISTORY_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(Array.isArray(parsed) ? parsed : []);
      }
    } catch (error) {
      console.error('Failed to load question history:', error);
      setHistory([]);
    }
  }, []);

  // Add a question to history
  const addQuestion = (question: string) => {
    if (!question.trim()) return;

    const newItem: QuestionHistoryItem = {
      id: `${Date.now()}-${Math.random()}`,
      question: question.trim(),
      timestamp: Date.now()
    };

    setHistory((prevHistory) => {
      // Remove duplicates (same question text)
      const filtered = prevHistory.filter(
        (item) => item.question.toLowerCase() !== question.trim().toLowerCase()
      );

      // Add new question at the beginning
      const updated = [newItem, ...filtered].slice(0, MAX_HISTORY_SIZE);

      // Save to localStorage
      try {
        localStorage.setItem(QUESTION_HISTORY_KEY, JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to save question history:', error);
      }

      return updated;
    });
  };

  // Clear all history
  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem(QUESTION_HISTORY_KEY);
    } catch (error) {
      console.error('Failed to clear question history:', error);
    }
  };

  // Remove a specific question from history
  const removeQuestion = (id: string) => {
    setHistory((prevHistory) => {
      const updated = prevHistory.filter((item) => item.id !== id);

      // Save to localStorage
      try {
        localStorage.setItem(QUESTION_HISTORY_KEY, JSON.stringify(updated));
      } catch (error) {
        console.error('Failed to save question history:', error);
      }

      return updated;
    });
  };

  return {
    history,
    addQuestion,
    clearHistory,
    removeQuestion
  };
}
