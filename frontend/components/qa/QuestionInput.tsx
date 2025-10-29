import { useState, FormEvent, KeyboardEvent } from 'react'
import styles from './QuestionInput.module.css'

interface QuestionInputProps {
  onSubmit: (question: string) => void
  isLoading: boolean
  disabled: boolean
}

export default function QuestionInput({ onSubmit, isLoading, disabled }: QuestionInputProps) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (question.trim() && !disabled) {
      onSubmit(question)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.inputContainer}>
        <label htmlFor="question-input" className={styles.label}>
          Your Question
        </label>
        <textarea
          id="question-input"
          className={styles.textarea}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., Where is patience mentioned in the Quran?"
          disabled={disabled}
          rows={3}
          aria-describedby="question-help"
          aria-required="true"
        />
        <div id="question-help" className={styles.help}>
          Press Enter to submit, Shift+Enter for new line
        </div>
      </div>
      
      <button
        type="submit"
        className={styles.submitButton}
        disabled={disabled || !question.trim()}
        aria-label="Submit question"
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} aria-hidden="true" />
            <span>Searching...</span>
          </>
        ) : (
          'Ask Question'
        )}
      </button>
    </form>
  )
}
