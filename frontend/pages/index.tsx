import Head from 'next/head'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>('checking...')
  const [frontendStatus, setFrontendStatus] = useState<string>('checking...')

  useEffect(() => {
    // Check frontend health
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setFrontendStatus(data.status))
      .catch(() => setFrontendStatus('error'))

    // Check backend health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setBackendStatus(data.status))
      .catch(() => setBackendStatus('error'))
  }, [])

  return (
    <>
      <Head>
        <title>Deen Hidaya</title>
        <meta name="description" content="Islamic knowledge platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-16 max-w-4xl">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-green-800 dark:text-green-400 mb-4">
              Deen Hidaya
            </h1>
            <p className="text-xl text-gray-700 dark:text-gray-300 mb-8">
              Islamic Knowledge Platform
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/reader"
                className="px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg shadow-lg transition-colors text-lg text-center"
              >
                📖 Read Quran
              </Link>
              <Link
                href="/qa"
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg transition-colors text-lg text-center"
              >
                💬 Ask Questions
              </Link>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              System Status
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded">
                <span className="font-medium text-gray-700 dark:text-gray-300">Frontend:</span>
                <span className={`font-semibold ${frontendStatus === 'healthy' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {frontendStatus}
                </span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded">
                <span className="font-medium text-gray-700 dark:text-gray-300">Backend:</span>
                <span className={`font-semibold ${backendStatus === 'healthy' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {backendStatus}
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
