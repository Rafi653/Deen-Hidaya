import type { NextApiRequest, NextApiResponse } from 'next'

interface Verse {
  verse_id: string
  surah_number: number
  verse_number: number
  text_arabic: string
  text_translation: string
  relevance_score: number
}

interface QAResponse {
  question: string
  answer: string
  verses: Verse[]
  timestamp: string
}

interface ErrorResponse {
  error: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<QAResponse | ErrorResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { question } = req.body

  if (!question || typeof question !== 'string') {
    return res.status(400).json({ error: 'Question is required' })
  }

  try {
    // TODO: Replace with actual backend API call
    // const response = await fetch('http://localhost:8000/api/v1/qa', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({ question }),
    // })
    // const data = await response.json()
    // return res.status(200).json(data)

    // Mock response for development
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Mock data based on question keywords
    const lowerQuestion = question.toLowerCase()
    
    let mockResponse: QAResponse

    if (lowerQuestion.includes('patience') || lowerQuestion.includes('sabr')) {
      mockResponse = {
        question,
        answer: 'Patience (Sabr) is mentioned throughout the Quran as a key virtue for believers. It involves perseverance through hardship, gratitude during ease, and steadfastness in faith. The Quran emphasizes that Allah is with those who are patient and promises great rewards for those who practice patience.',
        verses: [
          {
            verse_id: '2:153',
            surah_number: 2,
            verse_number: 153,
            text_arabic: 'يَا أَيُّهَا الَّذِينَ آمَنُوا اسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ ۚ إِنَّ اللَّهَ مَعَ الصَّابِرِينَ',
            text_translation: 'O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.',
            relevance_score: 0.95
          },
          {
            verse_id: '3:200',
            surah_number: 3,
            verse_number: 200,
            text_arabic: 'يَا أَيُّهَا الَّذِينَ آمَنُوا اصْبِرُوا وَصَابِرُوا وَرَابِطُوا وَاتَّقُوا اللَّهَ لَعَلَّكُمْ تُفْلِحُونَ',
            text_translation: 'O you who have believed, persevere and endure and remain stationed and fear Allah that you may be successful.',
            relevance_score: 0.92
          },
          {
            verse_id: '16:127',
            surah_number: 16,
            verse_number: 127,
            text_arabic: 'وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ ۚ وَلَا تَحْزَنْ عَلَيْهِمْ وَلَا تَكُ فِي ضَيْقٍ مِّمَّا يَمْكُرُونَ',
            text_translation: 'And be patient, and your patience is not but through Allah. And do not grieve over them and do not be in distress over what they conspire.',
            relevance_score: 0.89
          }
        ],
        timestamp: new Date().toISOString()
      }
    } else if (lowerQuestion.includes('prayer') || lowerQuestion.includes('salah')) {
      mockResponse = {
        question,
        answer: 'Prayer (Salah) is one of the five pillars of Islam and is mentioned extensively throughout the Quran. It is described as a means of seeking help from Allah, maintaining a connection with the Creator, and purifying the soul. The Quran emphasizes establishing regular prayers and performing them with devotion.',
        verses: [
          {
            verse_id: '2:45',
            surah_number: 2,
            verse_number: 45,
            text_arabic: 'وَاسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ ۚ وَإِنَّهَا لَكَبِيرَةٌ إِلَّا عَلَى الْخَاشِعِينَ',
            text_translation: 'And seek help through patience and prayer, and indeed, it is difficult except for the humbly submissive [to Allah].',
            relevance_score: 0.93
          },
          {
            verse_id: '20:14',
            surah_number: 20,
            verse_number: 14,
            text_arabic: 'إِنَّنِي أَنَا اللَّهُ لَا إِلَٰهَ إِلَّا أَنَا فَاعْبُدْنِي وَأَقِمِ الصَّلَاةَ لِذِكْرِي',
            text_translation: 'Indeed, I am Allah. There is no deity except Me, so worship Me and establish prayer for My remembrance.',
            relevance_score: 0.91
          },
          {
            verse_id: '29:45',
            surah_number: 29,
            verse_number: 45,
            text_arabic: 'اتْلُ مَا أُوحِيَ إِلَيْكَ مِنَ الْكِتَابِ وَأَقِمِ الصَّلَاةَ ۖ إِنَّ الصَّلَاةَ تَنْهَىٰ عَنِ الْفَحْشَاءِ وَالْمُنكَرِ',
            text_translation: 'Recite what has been revealed to you of the Book and establish prayer. Indeed, prayer prohibits immorality and wrongdoing.',
            relevance_score: 0.88
          }
        ],
        timestamp: new Date().toISOString()
      }
    } else {
      // Generic response for other questions
      mockResponse = {
        question,
        answer: 'The Quran provides guidance on various aspects of life and spirituality. This answer is AI-generated based on semantic search of relevant verses. Please consult the actual verses and qualified scholars for detailed understanding.',
        verses: [
          {
            verse_id: '1:1',
            surah_number: 1,
            verse_number: 1,
            text_arabic: 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
            text_translation: 'In the name of Allah, the Entirely Merciful, the Especially Merciful.',
            relevance_score: 0.85
          },
          {
            verse_id: '2:2',
            surah_number: 2,
            verse_number: 2,
            text_arabic: 'ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِّلْمُتَّقِينَ',
            text_translation: 'This is the Book about which there is no doubt, a guidance for those conscious of Allah.',
            relevance_score: 0.82
          },
          {
            verse_id: '3:7',
            surah_number: 3,
            verse_number: 7,
            text_arabic: 'هُوَ الَّذِي أَنزَلَ عَلَيْكَ الْكِتَابَ مِنْهُ آيَاتٌ مُّحْكَمَاتٌ هُنَّ أُمُّ الْكِتَابِ',
            text_translation: 'It is He who has sent down to you the Book; in it are verses [that are] precise - they are the foundation of the Book.',
            relevance_score: 0.79
          }
        ],
        timestamp: new Date().toISOString()
      }
    }

    return res.status(200).json(mockResponse)
  } catch (error) {
    console.error('Error processing question:', error)
    return res.status(500).json({ error: 'Internal server error' })
  }
}
