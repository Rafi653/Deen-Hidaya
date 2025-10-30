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

## Cloudflare Tunnel

The `start-tunnel.sh` script provides an easy way to expose your local Deen Hidaya application to the internet for sharing with friends.

### Quick Start

```bash
# Make sure services are running first
docker compose up -d

# Start the tunnel
./infra/start-tunnel.sh
```

The script offers two modes:

1. **Quick/Temporary Tunnel** - Perfect for one-time sharing, no configuration needed
2. **Named/Persistent Tunnel** - For ongoing access with custom domains

### Documentation

See [docs/CLOUDFLARE_TUNNEL_SETUP.md](../docs/CLOUDFLARE_TUNNEL_SETUP.md) for:
- Detailed setup instructions
- Security best practices
- Troubleshooting guide
- Configuration examples

### Security Note

⚠️ **Important**: When you expose your local application through a tunnel, anyone with the URL can access it. Review the security guidelines in the setup documentation before sharing widely.
