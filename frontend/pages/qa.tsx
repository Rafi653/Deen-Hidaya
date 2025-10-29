import Head from 'next/head'
import { useState } from 'react'
import QuestionInput from '@/components/qa/QuestionInput'
import ResultsList from '@/components/qa/ResultsList'
import ExplanationModal from '@/components/qa/ExplanationModal'
import styles from '@/styles/QA.module.css'

export interface Verse {
  verse_id: string
  surah_number: number
  verse_number: number
  text_arabic: string
  text_translation: string
  relevance_score: number
}

export interface QAResult {
  question: string
  answer: string
  verses: Verse[]
  timestamp: string
}

export default function QAPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<QAResult | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleQuestionSubmit = async (question: string) => {
    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      // Call backend API (when implemented)
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      if (!response.ok) {
        throw new Error('Failed to get answer')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error('Error fetching answer:', err)
      setError('Failed to get answer. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleShowExplanation = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  return (
    <>
      <Head>
        <title>Q&A - Deen Hidaya</title>
        <meta name="description" content="Ask questions about the Quran" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className={styles.container}>
        <div className={styles.content}>
          <header className={styles.header}>
            <h1>Ask About the Quran</h1>
            <p className={styles.subtitle}>
              Ask natural-language questions and get answers with verse citations
            </p>
          </header>

          <QuestionInput
            onSubmit={handleQuestionSubmit}
            isLoading={isLoading}
            disabled={isLoading}
          />

          {error && (
            <div className={styles.error} role="alert" aria-live="polite">
              {error}
            </div>
          )}

          {result && (
            <ResultsList
              result={result}
              onShowExplanation={handleShowExplanation}
            />
          )}

          {result && isModalOpen && (
            <ExplanationModal
              result={result}
              onClose={handleCloseModal}
            />
          )}
        </div>
      </main>
    </>
  )
}
