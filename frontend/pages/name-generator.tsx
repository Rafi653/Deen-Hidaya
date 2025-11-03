import Head from 'next/head';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  suggestNames,
  getEntityTypes,
  getSubtypes,
  getOrigins,
  getThemes,
  createFavorite,
  getUserFavorites,
  deleteFavorite,
  NameEntity,
  NameSuggestionRequest,
  NameFavorite,
} from '../lib/api';
import { AccessibilityBar } from '../components/AccessibilityBar';

export default function NameGenerator() {
  // State for form inputs
  const [entityType, setEntityType] = useState('baby');
  const [subtype, setSubtype] = useState('');
  const [gender, setGender] = useState('');
  const [origin, setOrigin] = useState('');
  const [meaning, setMeaning] = useState('');
  const [selectedThemes, setSelectedThemes] = useState<string[]>([]);
  const [phoneticPreference, setPhoneticPreference] = useState('');
  
  // State for available options
  const [entityTypes, setEntityTypes] = useState<string[]>([]);
  const [subtypes, setSubtypes] = useState<string[]>([]);
  const [origins, setOrigins] = useState<string[]>([]);
  const [themes, setThemes] = useState<string[]>([]);
  
  // State for results
  const [suggestions, setSuggestions] = useState<NameEntity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for favorites
  const [favorites, setFavorites] = useState<NameFavorite[]>([]);
  const [userId] = useState(() => {
    // Generate or retrieve user ID from localStorage
    if (typeof window !== 'undefined') {
      let id = localStorage.getItem('name_generator_user_id');
      if (!id) {
        id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('name_generator_user_id', id);
      }
      return id;
    }
    return 'temp_user';
  });
  
  // State for filters
  const [filterGender, setFilterGender] = useState('');
  const [filterOrigin, setFilterOrigin] = useState('');
  const [sortBy, setSortBy] = useState<'relevance' | 'name' | 'popularity'>('relevance');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  // Load initial data
  useEffect(() => {
    loadInitialData();
    loadFavorites();
  }, []);

  // Load subtypes when entity type changes
  useEffect(() => {
    if (entityType) {
      loadSubtypes(entityType);
    }
  }, [entityType]);

  async function loadInitialData() {
    try {
      const [typesData, originsData, themesData] = await Promise.all([
        getEntityTypes(),
        getOrigins(),
        getThemes(),
      ]);
      setEntityTypes(typesData);
      setOrigins(originsData);
      setThemes(themesData);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  }

  async function loadSubtypes(type: string) {
    try {
      const data = await getSubtypes(type);
      setSubtypes(data);
      setSubtype(''); // Reset subtype when entity type changes
    } catch (err) {
      console.error('Failed to load subtypes:', err);
      setSubtypes([]);
    }
  }

  async function loadFavorites() {
    try {
      const data = await getUserFavorites(userId);
      setFavorites(data);
    } catch (err) {
      console.error('Failed to load favorites:', err);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const request: NameSuggestionRequest = {
        entity_type: entityType,
        subtype: subtype || undefined,
        gender: gender || undefined,
        origin: origin || undefined,
        meaning: meaning || undefined,
        themes: selectedThemes.length > 0 ? selectedThemes : undefined,
        phonetic_preference: phoneticPreference || undefined,
        max_results: 50,
      };

      const response = await suggestNames(request);
      setSuggestions(response.suggestions);
    } catch (err) {
      setError('Failed to get name suggestions. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function handleThemeToggle(theme: string) {
    setSelectedThemes(prev =>
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    );
  }

  async function handleFavorite(name: NameEntity) {
    try {
      const isFavorited = favorites.some(f => f.name_entity_id === name.id);
      
      if (isFavorited) {
        const favorite = favorites.find(f => f.name_entity_id === name.id);
        if (favorite) {
          await deleteFavorite(favorite.id, userId);
          setFavorites(prev => prev.filter(f => f.id !== favorite.id));
        }
      } else {
        const newFavorite = await createFavorite({
          name_entity_id: name.id,
          user_id: userId,
        });
        setFavorites(prev => [...prev, newFavorite]);
      }
    } catch (err) {
      console.error('Failed to update favorite:', err);
      alert('Failed to update favorite. Please try again.');
    }
  }

  function isFavorited(nameId: number): boolean {
    return favorites.some(f => f.name_entity_id === nameId);
  }

  // Apply filters and sorting to suggestions
  const filteredAndSortedSuggestions = suggestions
    .filter(name => {
      if (showFavoritesOnly && !isFavorited(name.id)) return false;
      if (filterGender && name.gender && name.gender !== filterGender && name.gender !== 'unisex') return false;
      if (filterOrigin && name.origin && !name.origin.toLowerCase().includes(filterOrigin.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'popularity':
          return (b.popularity_score || 0) - (a.popularity_score || 0);
        case 'relevance':
        default:
          return (b.relevance_score || 0) - (a.relevance_score || 0);
      }
    });

  return (
    <>
      <Head>
        <title>Name Generator - Deen Hidaya</title>
        <meta name="description" content="Generate names for babies, pets, vehicles, companies, and more" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <AccessibilityBar className="sticky top-0 z-50" />
      <main id="main-content" className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Suggestive Name Generator
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
              Find the perfect name for your baby, pet, vehicle, company, or any other entity
            </p>
            <Link href="/" className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
              ← Back to Home
            </Link>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Input Form */}
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 sticky top-20">
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                  Preferences
                </h2>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Entity Type */}
                  <div>
                    <label htmlFor="entityType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Entity Type *
                    </label>
                    <select
                      id="entityType"
                      value={entityType}
                      onChange={(e) => setEntityType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      required
                    >
                      <option value="">Select type...</option>
                      {entityTypes.map(type => (
                        <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                      ))}
                    </select>
                  </div>

                  {/* Subtype */}
                  {subtypes.length > 0 && (
                    <div>
                      <label htmlFor="subtype" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Category
                      </label>
                      <select
                        id="subtype"
                        value={subtype}
                        onChange={(e) => setSubtype(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      >
                        <option value="">All categories</option>
                        {subtypes.map(st => (
                          <option key={st} value={st}>{st.replace('_', ' ')}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Gender */}
                  <div>
                    <label htmlFor="gender" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Gender
                    </label>
                    <select
                      id="gender"
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="">Any</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="unisex">Unisex</option>
                    </select>
                  </div>

                  {/* Origin */}
                  <div>
                    <label htmlFor="origin" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Origin
                    </label>
                    <select
                      id="origin"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="">Any origin</option>
                      {origins.map(orig => (
                        <option key={orig} value={orig}>{orig}</option>
                      ))}
                    </select>
                  </div>

                  {/* Meaning */}
                  <div>
                    <label htmlFor="meaning" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Desired Meaning
                    </label>
                    <input
                      type="text"
                      id="meaning"
                      value={meaning}
                      onChange={(e) => setMeaning(e.target.value)}
                      placeholder="e.g., strength, joy, beauty"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>

                  {/* Themes */}
                  {themes.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Themes
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {themes.map(theme => (
                          <button
                            key={theme}
                            type="button"
                            onClick={() => handleThemeToggle(theme)}
                            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                              selectedThemes.includes(theme)
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                            }`}
                          >
                            {theme}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Phonetic Preference */}
                  <div>
                    <label htmlFor="phonetic" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Phonetic Preference
                    </label>
                    <input
                      type="text"
                      id="phonetic"
                      value={phoneticPreference}
                      onChange={(e) => setPhoneticPreference(e.target.value)}
                      placeholder="e.g., starts with 'A'"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Generating...' : 'Generate Names'}
                  </button>
                </form>
              </div>
            </div>

            {/* Results */}
            <div className="lg:col-span-2">
              {error && (
                <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {suggestions.length > 0 && (
                <>
                  {/* Filters and Sorting */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-4">
                    <div className="flex flex-wrap gap-4 items-center">
                      <div className="flex-1 min-w-[200px]">
                        <label htmlFor="filterGender" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Filter by Gender
                        </label>
                        <select
                          id="filterGender"
                          value={filterGender}
                          onChange={(e) => setFilterGender(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                        >
                          <option value="">All</option>
                          <option value="male">Male</option>
                          <option value="female">Female</option>
                          <option value="unisex">Unisex</option>
                        </select>
                      </div>

                      <div className="flex-1 min-w-[200px]">
                        <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Sort by
                        </label>
                        <select
                          id="sortBy"
                          value={sortBy}
                          onChange={(e) => setSortBy(e.target.value as any)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                        >
                          <option value="relevance">Relevance</option>
                          <option value="name">Name (A-Z)</option>
                          <option value="popularity">Popularity</option>
                        </select>
                      </div>

                      <div className="flex items-center mt-6">
                        <input
                          type="checkbox"
                          id="showFavorites"
                          checked={showFavoritesOnly}
                          onChange={(e) => setShowFavoritesOnly(e.target.checked)}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="showFavorites" className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                          Favorites only
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Results Count */}
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Showing {filteredAndSortedSuggestions.length} of {suggestions.length} results
                  </p>

                  {/* Results Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {filteredAndSortedSuggestions.map((name) => (
                      <div
                        key={name.id}
                        className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                            {name.name}
                          </h3>
                          <button
                            onClick={() => handleFavorite(name)}
                            className="text-2xl focus:outline-none"
                            aria-label={isFavorited(name.id) ? 'Remove from favorites' : 'Add to favorites'}
                          >
                            {isFavorited(name.id) ? '❤️' : '🤍'}
                          </button>
                        </div>

                        {name.phonetic && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                            {name.phonetic}
                          </p>
                        )}

                        {name.meaning && (
                          <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                            <span className="font-semibold">Meaning:</span> {name.meaning}
                          </p>
                        )}

                        <div className="flex flex-wrap gap-2 mb-2">
                          {name.gender && (
                            <span className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs px-2 py-1 rounded">
                              {name.gender}
                            </span>
                          )}
                          {name.origin && (
                            <span className="inline-block bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs px-2 py-1 rounded">
                              {name.origin}
                            </span>
                          )}
                          {name.relevance_score !== undefined && (
                            <span className="inline-block bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs px-2 py-1 rounded">
                              Match: {Math.round(name.relevance_score * 100)}%
                            </span>
                          )}
                        </div>

                        {name.themes && name.themes.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-2">
                            {name.themes.map(theme => (
                              <span
                                key={theme}
                                className="inline-block bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs px-2 py-1 rounded"
                              >
                                {theme}
                              </span>
                            ))}
                          </div>
                        )}

                        {name.associated_traits && name.associated_traits.length > 0 && (
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            <span className="font-semibold">Traits:</span> {name.associated_traits.join(', ')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>

                  {filteredAndSortedSuggestions.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-500 dark:text-gray-400">
                        No names match your current filters. Try adjusting your criteria.
                      </p>
                    </div>
                  )}
                </>
              )}

              {!loading && suggestions.length === 0 && !error && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
                  <p className="text-gray-500 dark:text-gray-400 text-lg mb-4">
                    Set your preferences and click "Generate Names" to get started!
                  </p>
                  <p className="text-gray-400 dark:text-gray-500 text-sm">
                    We'll suggest names based on your criteria including entity type, gender, origin, meaning, and themes.
                  </p>
                </div>
              )}

              {loading && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-500 dark:text-gray-400">
                    Generating name suggestions...
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
