import Head from 'next/head';
import Link from 'next/link';
import { useState } from 'react';
import { askQuestion, QAResponse, CitedVerse } from '../lib/api';

export default function QA() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<QAResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVerse, setSelectedVerse] = useState<CitedVerse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await askQuestion({ 
        question: question.trim(),
        max_verses: 3 
      });
      setResponse(result);
    } catch (err) {
      setError('Failed to process your question. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleQuestion = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
    setError(null);
  };

  const exampleQuestions = [
    "What does the Quran say about patience?",
    "What is mentioned about charity in the Quran?",
    "What are the qualities of believers?",
    "What does the Quran teach about forgiveness?"
  ];

  return (
    <>
      <Head>
        <title>Q&A - Deen Hidaya</title>
        <meta name="description" content="Ask questions about the Quran and get answers with verse citations" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8 max-w-5xl">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 dark:text-green-400 mb-2">
              Quran Q&A
            </h1>
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
              Ask questions about the Quran and get answers with verse citations
            </p>
            <Link 
              href="/"
              className="text-sm text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
            >
              ← Back to Home
            </Link>
          </header>

          {/* Question Input Form */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8 border border-gray-200 dark:border-gray-700">
            <form onSubmit={handleSubmit}>
              <label htmlFor="question-input" className="block text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                Ask Your Question
              </label>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  id="question-input"
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g., What does the Quran say about patience?"
                  className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
                  aria-label="Enter your question"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold rounded-lg shadow transition-colors"
                  aria-label="Submit question"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Searching...
                    </span>
                  ) : (
                    'Ask'
                  )}
                </button>
              </div>
            </form>

            {/* Example Questions */}
            <div className="mt-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQuestions.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleQuestion(example)}
                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full transition-colors"
                    disabled={loading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6" role="alert">
              <p>{error}</p>
            </div>
          )}

          {/* Results */}
          {response && (
            <div className="space-y-6">
              {/* Answer Summary */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  Question: {response.question}
                </h2>
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 mb-4">
                  <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                    {response.answer}
                  </p>
                </div>
                
                {/* Metadata */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                  {response.confidence_score && (
                    <div className="flex items-center gap-1">
                      <span className="font-medium">Confidence:</span>
                      <span>{(response.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                  )}
                  {response.processing_time_ms && (
                    <div className="flex items-center gap-1">
                      <span className="font-medium">Processing time:</span>
                      <span>{response.processing_time_ms}ms</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <span className="font-medium">Sources:</span>
                    <span>{response.cited_verses.length} verses</span>
                  </div>
                </div>
              </div>

              {/* Cited Verses */}
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Cited Verses ({response.cited_verses.length})
                </h3>
                <div className="space-y-4">
                  {response.cited_verses.map((verse, index) => (
                    <div 
                      key={verse.verse_id}
                      className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-5 border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 transition-colors"
                    >
                      {/* Verse Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            {verse.surah_name} ({verse.surah_number}:{verse.verse_number})
                          </h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              Relevance: {(verse.relevance_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setSelectedVerse(verse)}
                            className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                            aria-label={`View details for verse ${verse.surah_number}:${verse.verse_number}`}
                          >
                            View Details
                          </button>
                          <Link
                            href={`/reader/${verse.surah_number}#verse-${verse.verse_number}`}
                            className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                            aria-label={`Read in context verse ${verse.surah_number}:${verse.verse_number}`}
                          >
                            Read in Context
                          </Link>
                        </div>
                      </div>

                      {/* Arabic Text */}
                      <div className="mb-3 text-right">
                        <p className="text-2xl leading-loose text-gray-900 dark:text-gray-100 font-arabic">
                          {verse.text_arabic}
                        </p>
                      </div>

                      {/* Transliteration */}
                      {verse.text_transliteration && (
                        <div className="mb-3">
                          <p className="text-sm italic text-gray-600 dark:text-gray-400">
                            {verse.text_transliteration}
                          </p>
                        </div>
                      )}

                      {/* Translation */}
                      {verse.translations.length > 0 && (
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                          <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                            {verse.translations[0].text}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                            — {verse.translations[0].translator}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Explanation Modal */}
          {selectedVerse && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
              onClick={() => setSelectedVerse(null)}
              role="dialog"
              aria-modal="true"
              aria-labelledby="modal-title"
            >
              <div 
                className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Modal Header */}
                <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
                  <h2 id="modal-title" className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                    {selectedVerse.surah_name} {selectedVerse.surah_number}:{selectedVerse.verse_number}
                  </h2>
                  <button
                    onClick={() => setSelectedVerse(null)}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2"
                    aria-label="Close modal"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* Modal Content */}
                <div className="p-6 space-y-6">
                  {/* Answer Context */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Why this verse is relevant:
                    </h3>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                      <p className="text-gray-800 dark:text-gray-200">
                        {response?.answer}
                      </p>
                    </div>
                  </div>

                  {/* Verse Details */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                      Verse Text:
                    </h3>
                    
                    {/* Arabic */}
                    <div className="mb-4 text-right">
                      <p className="text-3xl leading-loose text-gray-900 dark:text-gray-100 font-arabic">
                        {selectedVerse.text_arabic}
                      </p>
                    </div>

                    {/* Transliteration */}
                    {selectedVerse.text_transliteration && (
                      <div className="mb-4">
                        <p className="text-base italic text-gray-600 dark:text-gray-400">
                          {selectedVerse.text_transliteration}
                        </p>
                      </div>
                    )}

                    {/* Translations */}
                    {selectedVerse.translations.map((translation, index) => (
                      <div key={index} className="mb-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                        <p className="text-gray-800 dark:text-gray-200 leading-relaxed mb-2">
                          {translation.text}
                        </p>
                        <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-500">
                          <span>— {translation.translator}</span>
                          {translation.language && <span>• {translation.language}</span>}
                          {translation.source && <span>• Source: {translation.source}</span>}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Metadata */}
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                      Details:
                    </h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Surah:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-100">{selectedVerse.surah_name}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Reference:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-100">{selectedVerse.surah_number}:{selectedVerse.verse_number}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Relevance Score:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-100">{(selectedVerse.relevance_score * 100).toFixed(0)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Verse ID:</span>
                        <span className="ml-2 text-gray-900 dark:text-gray-100">{selectedVerse.verse_id}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <Link
                      href={`/reader/${selectedVerse.surah_number}#verse-${selectedVerse.verse_number}`}
                      className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-center rounded-lg transition-colors"
                    >
                      Read in Full Context
                    </Link>
                    <button
                      onClick={() => setSelectedVerse(null)}
                      className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!response && !loading && !error && (
            <div className="text-center py-12 text-gray-600 dark:text-gray-400">
              <svg className="mx-auto h-16 w-16 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-lg">Ask a question to get started</p>
              <p className="text-sm mt-2">Try one of the example questions above</p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
