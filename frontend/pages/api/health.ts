import type { NextApiRequest, NextApiResponse } from 'next'

type HealthResponse = {
  status: string
  service: string
  version: string
  timestamp: string
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  res.status(200).json({
    status: 'healthy',
    service: 'frontend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  })
}
