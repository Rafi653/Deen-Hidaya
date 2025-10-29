-- Initialize database with required extensions
-- pgvector: For vector similarity search (embeddings)
-- pg_trgm: For trigram-based text search

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm extension for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify extensions are installed
SELECT * FROM pg_extension WHERE extname IN ('vector', 'pg_trgm');
