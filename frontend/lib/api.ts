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

const MOCK_SURAH_AL_FATIHAH: SurahDetail = {
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

export async function fetchSurahDetail(surahNumber: number): Promise<SurahDetail> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/surahs/${surahNumber}`);
    if (!response.ok) {
      console.warn('Backend unavailable, using mock data');
      return MOCK_SURAH_AL_FATIHAH;
    }
    return response.json();
  } catch (error) {
    console.warn('Backend unavailable, using mock data', error);
    return MOCK_SURAH_AL_FATIHAH;
  }
}

export async function fetchAvailableTranslations(): Promise<TranslationMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translations`);
  if (!response.ok) {
    throw new Error('Failed to fetch translations');
  }
  return response.json();
}

// Q&A Types
export interface CitedVerse {
  verse_id: number;
  surah_number: number;
  verse_number: number;
  surah_name: string;
  text_arabic: string;
  text_transliteration?: string;
  translations: Translation[];
  relevance_score: number;
}

export interface QAResponse {
  question: string;
  answer: string;
  cited_verses: CitedVerse[];
  confidence_score?: number;
  processing_time_ms?: number;
}

export interface QARequest {
  question: string;
  language?: string;
  max_verses?: number;
}

// Mock Q&A data for demo purposes
const MOCK_QA_RESPONSE: QAResponse = {
  question: "What does the Quran say about patience?",
  answer: "The Quran emphasizes patience (sabr) as a fundamental virtue for believers. It teaches that patience is essential during times of hardship and that Allah is with those who are patient. Believers are encouraged to seek help through patience and prayer.",
  cited_verses: [
    {
      verse_id: 156,
      surah_number: 2,
      verse_number: 153,
      surah_name: "Al-Baqarah",
      text_arabic: "يَا أَيُّهَا الَّذِينَ آمَنُوا اسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ إِنَّ اللَّهَ مَعَ الصَّابِرِينَ",
      text_transliteration: "Ya ayyuha allatheena amanoo istaAAeenoo bialsabri waalssalati inna Allaha maAAa alsabireen",
      translations: [
        {
          id: 156,
          language: "en",
          translator: "Sahih International",
          text: "O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.",
          license: "CC BY-NC-ND 4.0",
          source: "api.quran.com"
        }
      ],
      relevance_score: 0.95
    },
    {
      verse_id: 178,
      surah_number: 2,
      verse_number: 177,
      surah_name: "Al-Baqarah",
      text_arabic: "وَلَٰكِنَّ الْبِرَّ مَنْ آمَنَ بِاللَّهِ وَالْيَوْمِ الْآخِرِ وَالْمَلَائِكَةِ وَالْكِتَابِ وَالنَّبِيِّينَ وَآتَى الْمَالَ عَلَىٰ حُبِّهِ ذَوِي الْقُرْبَىٰ وَالْيَتَامَىٰ وَالْمَسَاكِينَ وَابْنَ السَّبِيلِ وَالسَّائِلِينَ وَفِي الرِّقَابِ وَأَقَامَ الصَّلَاةَ وَآتَى الزَّكَاةَ وَالْمُوفُونَ بِعَهْدِهِمْ إِذَا عَاهَدُوا وَالصَّابِرِينَ فِي الْبَأْسَاءِ وَالضَّرَّاءِ وَحِينَ الْبَأْسِ أُولَٰئِكَ الَّذِينَ صَدَقُوا وَأُولَٰئِكَ هُمُ الْمُتَّقُونَ",
      text_transliteration: "Walakinna albirra man amana biAllahi waalyawmi alakhiri waalmalaikati waalkitabi waalnnabiyyeena waata almala AAala hubbihi thawee alqurba waalyatama waalmasakeena waibna alssabeeli waalssaileena wafee alrriqabi waaqama alssalata waata alzzakata waalmoofoona biAAahdihim itha AAahadoo waalssabireena fee albasai waalddarrai waheena albasi olaika allatheena sadaqoo waolaika humu almuttaqoon",
      translations: [
        {
          id: 178,
          language: "en",
          translator: "Sahih International",
          text: "Righteousness is not that you turn your faces toward the east or the west, but [true] righteousness is [in] one who believes in Allah, the Last Day, the angels, the Book, and the prophets and gives wealth, in spite of love for it, to relatives, orphans, the needy, the traveler, those who ask [for help], and for freeing slaves; [and who] establishes prayer and gives zakah; [those who] fulfill their promise when they promise; and [those who] are patient in poverty and hardship and during battle. Those are the ones who have been true, and it is those who are the righteous.",
          license: "CC BY-NC-ND 4.0",
          source: "api.quran.com"
        }
      ],
      relevance_score: 0.88
    },
    {
      verse_id: 1262,
      surah_number: 16,
      verse_number: 127,
      surah_name: "An-Nahl",
      text_arabic: "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ وَلَا تَحْزَنْ عَلَيْهِمْ وَلَا تَكُ فِي ضَيْقٍ مِّمَّا يَمْكُرُونَ",
      text_transliteration: "Waosbir wama sabruka illa biAllahi wala tahzan AAalayhim wala taku fee dayqin mimma yamkuroona",
      translations: [
        {
          id: 1262,
          language: "en",
          translator: "Sahih International",
          text: "And be patient, [O Muhammad], and your patience is not but through Allah. And do not grieve over them and do not be in distress over what they conspire.",
          license: "CC BY-NC-ND 4.0",
          source: "api.quran.com"
        }
      ],
      relevance_score: 0.85
    }
  ],
  confidence_score: 0.89,
  processing_time_ms: 245
};

export async function askQuestion(request: QARequest): Promise<QAResponse> {
  const getMockResponse = () => ({
    ...MOCK_QA_RESPONSE,
    question: request.question,
  });

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/qa/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      console.warn('Q&A endpoint not available, using mock data');
      return getMockResponse();
    }
    
    return response.json();
  } catch (error) {
    console.warn('Q&A endpoint not available, using mock data', error);
    return getMockResponse();
  }
}
