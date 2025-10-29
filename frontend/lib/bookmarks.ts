// Bookmark management with localStorage
export interface Bookmark {
  surahNumber: number;
  verseNumber: number;
  surahName: string;
  timestamp: string;
}

const BOOKMARKS_KEY = 'deen-hidaya-bookmarks';

export function getBookmarks(): Bookmark[] {
  if (typeof window === 'undefined') return [];
  
  const stored = localStorage.getItem(BOOKMARKS_KEY);
  if (!stored) return [];
  
  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

export function addBookmark(bookmark: Bookmark): void {
  const bookmarks = getBookmarks();
  
  // Check if bookmark already exists
  const exists = bookmarks.some(
    b => b.surahNumber === bookmark.surahNumber && b.verseNumber === bookmark.verseNumber
  );
  
  if (!exists) {
    bookmarks.push(bookmark);
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
  }
}

export function removeBookmark(surahNumber: number, verseNumber: number): void {
  const bookmarks = getBookmarks();
  const filtered = bookmarks.filter(
    b => !(b.surahNumber === surahNumber && b.verseNumber === verseNumber)
  );
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(filtered));
}

export function isBookmarked(surahNumber: number, verseNumber: number): boolean {
  const bookmarks = getBookmarks();
  return bookmarks.some(
    b => b.surahNumber === surahNumber && b.verseNumber === verseNumber
  );
}
