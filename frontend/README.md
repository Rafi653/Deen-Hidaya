# Deen Hidaya Frontend

Next.js frontend application for the Deen Hidaya Islamic knowledge platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## API Endpoints

- `GET /api/health` - Health check endpoint

## Docker

Build and run with Docker:
```bash
docker build -t deen-hidaya-frontend .
docker run -p 3000:3000 deen-hidaya-frontend
```
