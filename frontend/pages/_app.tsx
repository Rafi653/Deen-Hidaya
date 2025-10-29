import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider } from '../lib/ThemeProvider'
import { SkipToContent } from '../components/SkipToContent'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <SkipToContent />
      <Component {...pageProps} />
    </ThemeProvider>
  )
}
