# Deen Hidaya Infrastructure

Infrastructure configuration and initialization scripts for Deen Hidaya.

## Database Setup

The `init-db.sql` script initializes the PostgreSQL database with required extensions:

- **pgvector**: For vector similarity search (used for semantic search with embeddings)
- **pg_trgm**: For trigram-based text search (efficient fuzzy text matching)

These extensions are automatically installed when the database container starts.

## Docker Network

All services run on the `deen-hidaya-network` bridge network, allowing them to communicate with each other using service names.

## Volumes

- `postgres_data`: Persistent storage for PostgreSQL data
