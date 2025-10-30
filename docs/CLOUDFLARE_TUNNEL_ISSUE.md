# Sub-issue: Setup Cloudflare Tunnel for Local Sharing

## Issue Number
**Suggested: #12** (or next available issue number)

## Title
🌐 Setup Cloudflare Tunnel for Local Sharing

## Labels
- `enhancement`
- `role:lead`
- `infrastructure`

## Parent Issue
[#1 - MASTER: Deen Hidaya Base (Local Docker MVP)](https://github.com/Rafi653/Deen-Hidaya/issues/1)

## Summary
Setup Cloudflare Tunnel (cloudflared) to enable secure sharing of the locally-running Deen Hidaya application with friends for initial testing and feedback, without requiring public server deployment.

## Background
The Deen Hidaya application currently runs entirely locally via Docker Compose. To share the application with friends for early feedback without deploying to a public server, we need a secure tunneling solution. Cloudflare Tunnel provides a free, secure way to expose local services to the internet through Cloudflare's network.

## Goals
- Enable secure remote access to the local Deen Hidaya application
- Allow friends to test the application without complex setup
- Maintain security and privacy of local development environment
- Provide easy-to-share URLs for frontend and backend API

## Requirements

### Functional Requirements
1. Install and configure cloudflared on the host system
2. Create Cloudflare Tunnel configuration for frontend (port 3000) and backend (port 8000)
3. Setup persistent tunnel with authentication
4. Generate shareable URLs for both services
5. Document the tunnel setup and usage process

### Non-Functional Requirements
- Tunnel should automatically reconnect on network disruptions
- Minimal performance overhead (<100ms latency)
- Secure authentication and access control
- Easy to start/stop tunnel service

## Technical Approach

### Option 1: cloudflared CLI (Recommended for initial testing)
```bash
# Quick start with cloudflared
cloudflared tunnel --url http://localhost:3000
cloudflared tunnel --url http://localhost:8000
```

### Option 2: Named Tunnel with Config (Recommended for persistent use)
```bash
# 1. Install cloudflared
# 2. Login to Cloudflare
cloudflared tunnel login

# 3. Create tunnel
cloudflared tunnel create deen-hidaya

# 4. Configure tunnel routes
# 5. Run tunnel as service
cloudflared tunnel run deen-hidaya
```

### Configuration File Structure
Create `infra/cloudflared-config.yml`:
```yaml
tunnel: <TUNNEL_ID>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: deen-hidaya.example.com
    service: http://localhost:3000
  - hostname: api.deen-hidaya.example.com
    service: http://localhost:8000
  - service: http_status:404
```

## Implementation Tasks

### Setup Tasks
- [ ] Install cloudflared on host system
- [ ] Authenticate with Cloudflare account
- [ ] Create named tunnel for Deen Hidaya
- [ ] Configure tunnel routes for frontend and backend
- [ ] Test tunnel connectivity and performance
- [ ] Setup tunnel to run as system service (optional)

### Documentation Tasks
- [ ] Create `docs/CLOUDFLARE_TUNNEL_SETUP.md` with step-by-step instructions
- [ ] Document how to start/stop the tunnel
- [ ] Document how to share URLs with friends
- [ ] Add security best practices and warnings
- [ ] Update main README with tunnel information

### Security Tasks
- [ ] Review Cloudflare Tunnel security settings
- [ ] Configure access policies (optional: Cloudflare Access)
- [ ] Document what data is exposed through tunnel
- [ ] Add .gitignore entries for tunnel credentials
- [ ] Create environment variables for tunnel configuration

## Acceptance Criteria

### Must Have
- [ ] Cloudflared is installed and configured
- [ ] Frontend is accessible via Cloudflare tunnel URL
- [ ] Backend API is accessible via Cloudflare tunnel URL
- [ ] Documentation exists with clear setup instructions
- [ ] Tunnel credentials are properly secured (not in git)
- [ ] Tunnel can be easily started and stopped

### Nice to Have
- [ ] Tunnel runs as system service (auto-start)
- [ ] Multiple tunnel configurations (dev/staging)
- [ ] Access logging for security monitoring
- [ ] Integration with docker-compose (optional tunnel service)

## Testing Checklist
- [ ] Tunnel URL is accessible from external network
- [ ] Frontend loads correctly through tunnel
- [ ] Backend API endpoints respond correctly through tunnel
- [ ] Authentication works properly through tunnel
- [ ] Websockets/real-time features work (if applicable)
- [ ] Performance is acceptable (<200ms additional latency)
- [ ] Tunnel reconnects automatically after network disruption

## Documentation Deliverables

### 1. Setup Guide (`docs/CLOUDFLARE_TUNNEL_SETUP.md`)
Should include:
- Prerequisites (Cloudflare account, cloudflared installation)
- Step-by-step setup instructions
- Configuration file examples
- Troubleshooting section

### 2. Usage Guide
Should include:
- How to start the tunnel
- How to get shareable URLs
- How to stop the tunnel
- How to monitor tunnel status

### 3. Security Guidelines
Should include:
- What data is exposed
- How to secure the tunnel
- Best practices for sharing URLs
- How to revoke access

## Security Considerations

### ⚠️ Important Warnings
- Tunnel exposes your local application to the internet
- Anyone with the URL can access your application
- Database and backend services may be exposed
- Consider implementing authentication before sharing widely

### Security Recommendations
1. Use Cloudflare Access for authentication (optional)
2. Set up rate limiting
3. Monitor access logs
4. Use temporary tunnels for quick sharing
5. Implement proper CORS settings
6. Review exposed environment variables
7. Don't commit tunnel credentials to git

## Resources
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub Repository](https://github.com/cloudflare/cloudflared)
- [Cloudflare Tunnel Installation Guide](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/)

## Related Issues
- [#1 - MASTER: Deen Hidaya Base (Local Docker MVP)](https://github.com/Rafi653/Deen-Hidaya/issues/1)
- [#2 - Repo & Local Docker bootstrap](https://github.com/Rafi653/Deen-Hidaya/issues/2) (closed)

## Estimated Effort
- Setup: 1-2 hours
- Documentation: 1-2 hours
- Testing: 30 minutes
- **Total: 3-4 hours**

## Priority
**Medium** - Useful for early testing but not blocking for local development

## Notes
- This is infrastructure/deployment work, appropriate for Lead/Architect role
- Consider this a temporary solution; production deployment would use different approach
- Cloudflare Tunnel is free for personal use
- Can be disabled when not needed to maintain security
