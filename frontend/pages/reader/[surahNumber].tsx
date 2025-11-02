import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { fetchSurahDetail, SurahDetail, Verse } from '../../lib/api';
import { GaplessAudioPlayer } from '../../lib/audioPlayer';
import { addBookmark, removeBookmark, isBookmarked, Bookmark } from '../../lib/bookmarks';
import { AccessibilityBar } from '../../components/AccessibilityBar';
import { useTheme, getFontSizeClasses } from '../../lib/theme';

export default function SurahReader() {
  const router = useRouter();
  const { surahNumber } = router.query;
  const { fontSize } = useTheme();
  const fontClasses = getFontSizeClasses(fontSize);
  
  const [surah, setSurah] = useState<SurahDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Display toggles
  const [showTransliteration, setShowTransliteration] = useState(false);
  const [translationLanguage, setTranslationLanguage] = useState<'en' | 'te'>('en');
  
  // Audio player state
  const [audioPlayer, setAudioPlayer] = useState<GaplessAudioPlayer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPlayingVerse, setCurrentPlayingVerse] = useState<number>(0);
  const [audioSupported, setAudioSupported] = useState(true);
  
  // Bookmarks
  const [bookmarks, setBookmarks] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (surahNumber) {
      loadSurah(Number(surahNumber));
    }
  }, [surahNumber]);

  useEffect(() => {
    // Load bookmarks for this surah
    if (surah) {
      const bookmarkedVerses = new Set<number>();
      surah.verses.forEach(verse => {
        if (isBookmarked(surah.number, verse.verse_number)) {
          bookmarkedVerses.add(verse.verse_number);
        }
      });
      setBookmarks(bookmarkedVerses);
    }
  }, [surah]);

  async function loadSurah(num: number) {
    try {
      setLoading(true);
      const data = await fetchSurahDetail(num);
      setSurah(data);
      setError(null);
      
      // Check if audio URLs are available
      const hasAudio = data.verses.some(verse => 
        verse.audio_tracks && verse.audio_tracks.length > 0
      );
      
      if (hasAudio) {
        // Extract audio URLs from verses
        const audioUrls = data.verses.map(verse => {
          const audioTrack = verse.audio_tracks?.[0]; // Use first audio track
          return audioTrack?.audio_url || '';
        }).filter(url => url !== '');
        
        if (audioUrls.length > 0) {
          // Initialize audio player with config
          const player = new GaplessAudioPlayer({
            onTrackChange: (verseNumber: number) => {
              setCurrentPlayingVerse(verseNumber);
            },
            onPlayStateChange: (playing: boolean) => {
              setIsPlaying(playing);
            },
            onError: (error: Error) => {
              console.error('Audio player error:', error);
            }
          });
          
          // Initialize with audio URLs
          await player.initialize(audioUrls);
          setAudioPlayer(player);
          setAudioSupported(true);
        } else {
          setAudioSupported(false);
        }
      } else {
        setAudioSupported(false);
      }
      
    } catch (err) {
      setError('Failed to load surah. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function toggleBookmark(verse: Verse) {
    if (!surah) return;
    
    const isCurrentlyBookmarked = bookmarks.has(verse.verse_number);
    
    if (isCurrentlyBookmarked) {
      removeBookmark(surah.number, verse.verse_number);
      setBookmarks(prev => {
        const next = new Set(prev);
        next.delete(verse.verse_number);
        return next;
      });
    } else {
      addBookmark({
        surahNumber: surah.number,
        verseNumber: verse.verse_number,
        surahName: surah.name_english,
        timestamp: new Date().toISOString()
      });
      setBookmarks(prev => {
        const next = new Set(prev);
        next.add(verse.verse_number);
        return next;
      });
    }
  }

  function getTranslation(verse: Verse): string {
    const lang = translationLanguage === 'en' ? 'en' : 'te';
    const translation = verse.translations.find(t => 
      t.language.toLowerCase() === lang
    );
    return translation?.text || 'Translation not available';
  }

  async function handlePlayVerse(verseIndex: number) {
    if (!audioSupported || !audioPlayer) {
      alert('Audio playback is not available for this surah. Audio data may not be loaded yet.');
      return;
    }
    
    try {
      if (currentPlayingVerse === verseIndex + 1 && isPlaying) {
        audioPlayer.pause();
      } else {
        await audioPlayer.playVerse(verseIndex);
      }
    } catch (error) {
      console.error('Error playing verse:', error);
      alert('Failed to play audio. Please try again.');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading surah...</p>
        </div>
      </div>
    );
  }

  if (error || !surah) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Surah not found'}</p>
          <Link href="/reader" className="text-green-600 hover:text-green-800 dark:text-green-400">
            ← Back to Surah List
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{surah.name_english} - Quran Reader</title>
        <meta name="description" content={`Read ${surah.name_english} (${surah.name_arabic})`} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AccessibilityBar className="sticky top-0 z-50" />
      <main id="main-content" className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Header */}
          <header className="mb-8">
            <Link 
              href="/reader"
              className="text-sm text-green-600 hover:text-green-800 dark:text-green-400 mb-4 inline-block"
            >
              ← Back to Surah List
            </Link>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center border-t-4 border-green-500">
              <h1 className={`font-arabic text-gray-900 dark:text-gray-100 mb-2 ${fontClasses.heading}`}>
                {surah.name_arabic}
              </h1>
              <h2 className={`font-bold text-gray-800 dark:text-gray-200 mb-1 ${fontClasses.body}`}>
                {surah.name_english}
              </h2>
              <p className={`text-gray-600 dark:text-gray-400 ${fontClasses.body}`}>
                {surah.name_transliteration} • {surah.total_verses} verses • {surah.revelation_place}
              </p>
            </div>
          </header>

          {/* Controls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6 sticky top-4 z-10">
            <div className="flex flex-wrap gap-4 items-center justify-between">
              <div className="flex gap-2">
                <button
                  onClick={() => setShowTransliteration(!showTransliteration)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    showTransliteration
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                  aria-pressed={showTransliteration}
                >
                  Transliteration
                </button>
              </div>
              
              <div className="flex items-center gap-2">
                <label htmlFor="translation-select" className="text-sm text-gray-700 dark:text-gray-300">
                  Translation:
                </label>
                <select
                  id="translation-select"
                  value={translationLanguage}
                  onChange={(e) => setTranslationLanguage(e.target.value as 'en' | 'te')}
                  className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="en">English</option>
                  <option value="te">Telugu</option>
                </select>
              </div>
            </div>
          </div>

          {/* Bismillah (except for Surah 9) */}
          {surah.number !== 9 && surah.number !== 1 && (
            <div className="text-center mb-8 py-6">
              <p className={`font-arabic text-gray-900 dark:text-gray-100 ${fontClasses.heading}`}>
                بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
              </p>
              <p className={`text-gray-600 dark:text-gray-400 mt-2 ${fontClasses.body}`}>
                In the name of Allah, the Most Gracious, the Most Merciful
              </p>
            </div>
          )}

          {/* Verses */}
          <div className="space-y-6">
            {surah.verses.map((verse, index) => (
              <article
                key={verse.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 hover:border-green-500 dark:hover:border-green-500 transition-colors"
                id={`verse-${verse.verse_number}`}
              >
                {/* Verse Number and Actions */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center justify-center w-10 h-10 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full font-semibold">
                      {verse.verse_number}
                    </span>
                    <button
                      onClick={() => handlePlayVerse(index)}
                      className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      aria-label={`Play verse ${verse.verse_number}`}
                      title="Audio playback coming soon"
                    >
                      {currentPlayingVerse === verse.verse_number && isPlaying ? (
                        <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  <button
                    onClick={() => toggleBookmark(verse)}
                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    aria-label={bookmarks.has(verse.verse_number) ? 'Remove bookmark' : 'Add bookmark'}
                  >
                    {bookmarks.has(verse.verse_number) ? (
                      <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                    )}
                  </button>
                </div>

                {/* Arabic Text */}
                <div className="mb-4 text-right" dir="rtl">
                  <p className={`font-arabic leading-loose text-gray-900 dark:text-gray-100 ${fontClasses.arabic}`}>
                    {verse.text_arabic}
                  </p>
                </div>

                {/* Transliteration */}
                {showTransliteration && verse.text_transliteration && (
                  <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <p className={`font-medium text-gray-700 dark:text-gray-300 italic ${fontClasses.body}`}>
                      {verse.text_transliteration}
                    </p>
                  </div>
                )}

                {/* Translation */}
                <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <p className={`text-gray-800 dark:text-gray-200 ${fontClasses.translation}`}>
                    {getTranslation(verse)}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
