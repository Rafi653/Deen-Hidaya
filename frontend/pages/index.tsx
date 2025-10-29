import Head from 'next/head'
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
      <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
        <h1>Deen Hidaya</h1>
        <p>Islamic Knowledge Platform</p>
        
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>System Status</h2>
          <div style={{ marginTop: '1rem' }}>
            <p><strong>Frontend:</strong> <span style={{ color: frontendStatus === 'healthy' ? 'green' : 'red' }}>{frontendStatus}</span></p>
            <p><strong>Backend:</strong> <span style={{ color: backendStatus === 'healthy' ? 'green' : 'red' }}>{backendStatus}</span></p>
          </div>
        </div>
      </main>
    </>
  )
}
