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
      
      // Mock data for development/testing
      setResult({
        question,
        answer: 'Patience (Sabr) is mentioned throughout the Quran as a key virtue for believers. It involves perseverance through hardship, gratitude during ease, and steadfastness in faith.',
        verses: [
          {
            verse_id: '2:153',
            surah_number: 2,
            verse_number: 153,
            text_arabic: 'يَا أَيُّهَا الَّذِينَ آمَنُوا اسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ ۚ إِنَّ اللَّهَ مَعَ الصَّابِرِينَ',
            text_translation: 'O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.',
            relevance_score: 0.95
          },
          {
            verse_id: '3:200',
            surah_number: 3,
            verse_number: 200,
            text_arabic: 'يَا أَيُّهَا الَّذِينَ آمَنُوا اصْبِرُوا وَصَابِرُوا وَرَابِطُوا وَاتَّقُوا اللَّهَ لَعَلَّكُمْ تُفْلِحُونَ',
            text_translation: 'O you who have believed, persevere and endure and remain stationed and fear Allah that you may be successful.',
            relevance_score: 0.92
          },
          {
            verse_id: '16:127',
            surah_number: 16,
            verse_number: 127,
            text_arabic: 'وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ ۚ وَلَا تَحْزَنْ عَلَيْهِمْ وَلَا تَكُ فِي ضَيْقٍ مِّمَّا يَمْكُرُونَ',
            text_translation: 'And be patient, and your patience is not but through Allah. And do not grieve over them and do not be in distress over what they conspire.',
            relevance_score: 0.89
          }
        ],
        timestamp: new Date().toISOString()
      })
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
