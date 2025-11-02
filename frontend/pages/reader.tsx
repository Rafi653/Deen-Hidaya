import Head from 'next/head';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { fetchSurahs, Surah } from '../lib/api';
import { AccessibilityBar } from '../components/AccessibilityBar';

export default function Reader() {
  const [surahs, setSurahs] = useState<Surah[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadSurahs();
  }, []);

  async function loadSurahs() {
    try {
      setLoading(true);
      const data = await fetchSurahs();
      setSurahs(data);
      setError(null);
    } catch (err) {
      setError('Failed to load surahs. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const filteredSurahs = surahs.filter(surah =>
    surah.name_english.toLowerCase().includes(searchQuery.toLowerCase()) ||
    surah.name_arabic.includes(searchQuery) ||
    surah.number.toString().includes(searchQuery)
  );

  return (
    <>
      <Head>
        <title>Quran Reader - Deen Hidaya</title>
        <meta name="description" content="Browse and read the Holy Quran" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AccessibilityBar className="sticky top-0 z-50" />
      <main id="main-content" className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 dark:text-green-400 mb-2">
              القرآن الكريم
            </h1>
            <h2 className="text-2xl text-gray-700 dark:text-gray-300 mb-4">
              The Holy Quran
            </h2>
            <Link 
              href="/"
              className="text-sm text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
            >
              ← Back to Home
            </Link>
          </header>

          {/* Search */}
          <div className="mb-8">
            <input
              type="text"
              placeholder="Search by name or number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
              aria-label="Search surahs"
            />
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading surahs...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6" role="alert">
              <p>{error}</p>
              <button 
                onClick={loadSurahs}
                className="mt-2 text-sm underline hover:no-underline"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Surah List */}
          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredSurahs.map((surah) => (
                <Link
                  key={surah.id}
                  href={`/reader/${surah.number}`}
                  className="block p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 rtl:space-x-reverse">
                      {/* Number Badge */}
                      <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                        <span className="text-lg font-semibold text-green-800 dark:text-green-200">
                          {surah.number}
                        </span>
                      </div>
                      
                      {/* Names */}
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                          {surah.name_english}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {surah.name_transliteration}
                        </p>
                      </div>
                    </div>
                    
                    {/* Arabic Name */}
                    <div className="text-right">
                      <p className="text-2xl font-arabic text-gray-900 dark:text-gray-100 mb-1">
                        {surah.name_arabic}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {surah.total_verses} verses • {surah.revelation_place}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {!loading && !error && filteredSurahs.length === 0 && (
            <div className="text-center py-12 text-gray-600 dark:text-gray-400">
              <p>No surahs found matching &quot;{searchQuery}&quot;</p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
