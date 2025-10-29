import { useEffect, useRef, KeyboardEvent } from 'react'
import { QAResult } from '@/pages/qa'
import styles from './ExplanationModal.module.css'

interface ExplanationModalProps {
  result: QAResult
  onClose: () => void
}

export default function ExplanationModal({ result, onClose }: ExplanationModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    // Focus close button when modal opens
    closeButtonRef.current?.focus()

    // Lock body scroll
    document.body.style.overflow = 'hidden'

    // Handle Escape key
    const handleEscape = (e: globalThis.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)

    return () => {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleEscape)
    }
  }, [onClose])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    // Trap focus within modal
    if (e.key === 'Tab') {
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      if (focusableElements && focusableElements.length > 0) {
        const firstElement = focusableElements[0] as HTMLElement
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }
  }

  return (
    <div
      className={styles.backdrop}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className={styles.modal}
        onKeyDown={handleKeyDown}
      >
        <header className={styles.header}>
          <h2 id="modal-title" className={styles.title}>
            Detailed Explanation
          </h2>
          <button
            ref={closeButtonRef}
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close explanation modal"
          >
            ✕
          </button>
        </header>

        <div className={styles.content}>
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Your Question</h3>
            <p className={styles.question}>{result.question}</p>
          </section>

          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>AI-Generated Answer</h3>
            <p className={styles.answer}>{result.answer}</p>
            <div className={styles.disclaimer} role="note">
              <strong>⚠️ Important:</strong> This answer is AI-generated and should be used for guidance only. 
              Always refer to the original Quranic text and consult with qualified scholars for religious guidance.
            </div>
          </section>

          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Source Verses</h3>
            <div className={styles.sources}>
              {result.verses.map((verse, index) => (
                <div key={verse.verse_id} className={styles.source}>
                  <div className={styles.sourceHeader}>
                    <span className={styles.sourceRank}>#{index + 1}</span>
                    <span className={styles.sourceRef}>
                      Surah {verse.surah_number}:{verse.verse_number}
                    </span>
                    <span className={styles.sourceScore}>
                      {Math.round(verse.relevance_score * 100)}% match
                    </span>
                  </div>
                  <div className={styles.sourceText}>
                    <div className={styles.sourceArabic} dir="rtl" lang="ar">
                      {verse.text_arabic}
                    </div>
                    <div className={styles.sourceTranslation}>
                      {verse.text_translation}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Methodology</h3>
            <p className={styles.methodology}>
              This answer was generated using semantic search with embeddings to find the most relevant 
              verses from the Quran based on your question. An AI language model then synthesized the 
              information from these verses to provide a concise answer. The top 3 most relevant verses 
              are cited as sources.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
