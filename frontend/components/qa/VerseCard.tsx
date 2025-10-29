import { Verse } from '@/pages/qa'
import styles from './VerseCard.module.css'

interface VerseCardProps {
  verse: Verse
  rank: number
}

export default function VerseCard({ verse, rank }: VerseCardProps) {
  const handleVerseClick = () => {
    // Navigate to verse detail page (to be implemented)
    // For now, we'll just log
    console.log('Navigate to verse:', verse.verse_id)
  }

  return (
    <article 
      className={styles.card}
      role="listitem"
      aria-label={`Verse ${verse.verse_id}, rank ${rank}`}
    >
      <div className={styles.header}>
        <div className={styles.rank} aria-label={`Rank ${rank}`}>
          #{rank}
        </div>
        <div className={styles.reference}>
          <span className={styles.surahVerse}>
            Surah {verse.surah_number}, Verse {verse.verse_number}
          </span>
          <span className={styles.relevance} aria-label={`Relevance score ${Math.round(verse.relevance_score * 100)}%`}>
            {Math.round(verse.relevance_score * 100)}% match
          </span>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.arabic} dir="rtl" lang="ar">
          {verse.text_arabic}
        </div>
        <div className={styles.translation}>
          {verse.text_translation}
        </div>
      </div>

      <button
        className={styles.viewButton}
        onClick={handleVerseClick}
        aria-label={`View full context for verse ${verse.verse_id}`}
      >
        View in Context →
      </button>
    </article>
  )
}
