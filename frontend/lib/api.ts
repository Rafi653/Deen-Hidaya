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

export async function fetchSurahs(): Promise<Surah[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/surahs`);
  if (!response.ok) {
    throw new Error('Failed to fetch surahs');
  }
  return response.json();
}

export async function fetchSurahDetail(surahNumber: number): Promise<SurahDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/surahs/${surahNumber}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch surah ${surahNumber}`);
  }
  return response.json();
}

export async function fetchAvailableTranslations(): Promise<TranslationMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translations`);
  if (!response.ok) {
    throw new Error('Failed to fetch translations');
  }
  return response.json();
}
