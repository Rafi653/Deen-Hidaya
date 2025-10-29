// API service for communicating with backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Surah {
  id: number;
  number: number;
  name_arabic: string;
  name_english: string;
  name_transliteration?: string;
  revelation_place?: string;
  total_verses: number;
}

export interface Translation {
  id: number;
  language: string;
  translator: string;
  text: string;
  license?: string;
  source?: string;
}

export interface Verse {
  id: number;
  verse_number: number;
  text_arabic: string;
  text_simple?: string;
  text_transliteration?: string;
  juz_number?: number;
  hizb_number?: number;
  rub_number?: number;
  sajda: boolean;
  translations: Translation[];
}

export interface SurahDetail extends Surah {
  verses: Verse[];
}

export interface TranslationMetadata {
  language: string;
  translator: string;
  source?: string;
  license?: string;
}

// Mock data for demo purposes when backend is unavailable
const MOCK_SURAHS: Surah[] = [
  { id: 1, number: 1, name_arabic: 'الفاتحة', name_english: 'Al-Fatihah', name_transliteration: 'The Opening', revelation_place: 'Makkah', total_verses: 7 },
  { id: 2, number: 2, name_arabic: 'البقرة', name_english: 'Al-Baqarah', name_transliteration: 'The Cow', revelation_place: 'Madinah', total_verses: 286 },
  { id: 3, number: 3, name_arabic: 'آل عمران', name_english: 'Ali \'Imran', name_transliteration: 'The Family of Imran', revelation_place: 'Madinah', total_verses: 200 },
  { id: 4, number: 4, name_arabic: 'النساء', name_english: 'An-Nisa', name_transliteration: 'The Women', revelation_place: 'Madinah', total_verses: 176 },
  { id: 5, number: 5, name_arabic: 'المائدة', name_english: 'Al-Ma\'idah', name_transliteration: 'The Table Spread', revelation_place: 'Madinah', total_verses: 120 },
];

export async function fetchSurahs(): Promise<Surah[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/surahs`);
    if (!response.ok) {
      console.warn('Backend unavailable, using mock data');
      return MOCK_SURAHS;
    }
    return response.json();
  } catch (error) {
    console.warn('Backend unavailable, using mock data', error);
    return MOCK_SURAHS;
  }
}

export async function fetchSurahDetail(surahNumber: number): Promise<SurahDetail> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/surahs/${surahNumber}`);
    if (!response.ok) {
      // Return mock data for Surah Al-Fatihah as demo
      return {
        id: 1,
        number: 1,
        name_arabic: 'الفاتحة',
        name_english: 'Al-Fatihah',
        name_transliteration: 'The Opening',
        revelation_place: 'Makkah',
        total_verses: 7,
        verses: [
          {
            id: 1,
            verse_number: 1,
            text_arabic: 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
            text_transliteration: 'Bismillāhir-Raḥmānir-Raḥīm',
            sajda: false,
            translations: [
              { id: 1, language: 'english', translator: 'Sahih International', text: 'In the name of Allah, the Entirely Merciful, the Especially Merciful.' },
              { id: 2, language: 'telugu', translator: 'Telugu Translation', text: 'అత్యంత కరుణామయుడు, అపార కృపాశీలుడు అయిన అల్లాహ్ పేరుతో (ప్రారంభిస్తున్నాను).' }
            ]
          },
          {
            id: 2,
            verse_number: 2,
            text_arabic: 'ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ',
            text_transliteration: 'Al-hamdu lillahi rabbil-alamin',
            sajda: false,
            translations: [
              { id: 3, language: 'english', translator: 'Sahih International', text: '[All] praise is [due] to Allah, Lord of the worlds.' },
              { id: 4, language: 'telugu', translator: 'Telugu Translation', text: 'సర్వ ప్రపంచాలకు ప్రభువైన అల్లాహ్‌కే సమస్త స్తుతులు.' }
            ]
          },
          {
            id: 3,
            verse_number: 3,
            text_arabic: 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
            text_transliteration: 'Ar-Rahmanir-Rahim',
            sajda: false,
            translations: [
              { id: 5, language: 'english', translator: 'Sahih International', text: 'The Entirely Merciful, the Especially Merciful.' },
              { id: 6, language: 'telugu', translator: 'Telugu Translation', text: 'అత్యంత కరుణామయుడు, అపార కృపాశీలుడు.' }
            ]
          }
        ]
      };
    }
    return response.json();
  } catch (error) {
    // Return mock data for demo
    return {
      id: 1,
      number: 1,
      name_arabic: 'الفاتحة',
      name_english: 'Al-Fatihah',
      name_transliteration: 'The Opening',
      revelation_place: 'Makkah',
      total_verses: 7,
      verses: [
        {
          id: 1,
          verse_number: 1,
          text_arabic: 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
          text_transliteration: 'Bismillahir-Rahmanir-Rahim',
          sajda: false,
          translations: [
            { id: 1, language: 'english', translator: 'Sahih International', text: 'In the name of Allah, the Entirely Merciful, the Especially Merciful.' },
            { id: 2, language: 'telugu', translator: 'Telugu Translation', text: 'అత్యంత కరుణామయుడు, అపార కృపాశీలుడు అయిన అల్లాహ్ పేరుతో (ప్రారంభిస్తున్నాను).' }
          ]
        },
        {
          id: 2,
          verse_number: 2,
          text_arabic: 'ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ',
          text_transliteration: 'Al-hamdu lillahi rabbil-alamin',
          sajda: false,
          translations: [
            { id: 3, language: 'english', translator: 'Sahih International', text: '[All] praise is [due] to Allah, Lord of the worlds.' },
            { id: 4, language: 'telugu', translator: 'Telugu Translation', text: 'సర్వ ప్రపంచాలకు ప్రభువైన అల్లాహ్‌కే సమస్త స్తుతులు.' }
          ]
        },
        {
          id: 3,
          verse_number: 3,
          text_arabic: 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
          text_transliteration: 'Ar-Rahmanir-Rahim',
          sajda: false,
          translations: [
            { id: 5, language: 'english', translator: 'Sahih International', text: 'The Entirely Merciful, the Especially Merciful.' },
            { id: 6, language: 'telugu', translator: 'Telugu Translation', text: 'అత్యంత కరుణామయుడు, అపార కృపాశీలుడు.' }
          ]
        }
      ]
    };
  }
}

export async function fetchAvailableTranslations(): Promise<TranslationMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translations`);
  if (!response.ok) {
    throw new Error('Failed to fetch translations');
  }
  return response.json();
}
