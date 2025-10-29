import { QAResult } from '@/pages/qa'
import VerseCard from './VerseCard'
import styles from './ResultsList.module.css'

interface ResultsListProps {
  result: QAResult
  onShowExplanation: () => void
}

export default function ResultsList({ result, onShowExplanation }: ResultsListProps) {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Results</h2>
        <button
          className={styles.explanationButton}
          onClick={onShowExplanation}
          aria-label="Show detailed explanation"
        >
          <span aria-hidden="true">ℹ️</span> View Explanation
        </button>
      </div>

      <div className={styles.answer}>
        <h3 className={styles.answerLabel}>Answer</h3>
        <p className={styles.answerText}>{result.answer}</p>
        <p className={styles.disclaimer} role="note">
          <strong>Note:</strong> This is an AI-generated summary. Please refer to the verses below for the actual Quranic text.
        </p>
      </div>

      <div className={styles.verses}>
        <h3 className={styles.versesLabel}>
          Top {result.verses.length} Related Verses
        </h3>
        <div className={styles.versesList} role="list">
          {result.verses.map((verse, index) => (
            <VerseCard
              key={verse.verse_id}
              verse={verse}
              rank={index + 1}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
