# Cloudflare Tunnel - Quick Reference

Quick commands and tips for using Cloudflare Tunnel with Deen Hidaya.

## Installation

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux (Debian/Ubuntu)
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Windows
choco install cloudflared
```

## Quick Sharing (No Setup Required)

```bash
# 1. Start services
docker compose up -d

# 2. Run helper script
./infra/start-tunnel.sh
# Select option 1 for temporary tunnel

# 3. Share the URLs shown
```

## Named Tunnel Setup

```bash
# 1. Authenticate
cloudflared tunnel login

# 2. Create tunnel
cloudflared tunnel create deen-hidaya

# 3. Create config at ~/.cloudflared/config.yml
# See infra/cloudflared-config.example.yml

# 4. Add DNS routes
cloudflared tunnel route dns deen-hidaya your-subdomain.your-domain.com

# 5. Run tunnel
cloudflared tunnel run deen-hidaya
```

## Common Commands

```bash
# List all tunnels
cloudflared tunnel list

# Get tunnel info
cloudflared tunnel info deen-hidaya

# Delete tunnel
cloudflared tunnel delete deen-hidaya

# View logs (if running as service)
journalctl -u cloudflared -f

# Run with debug logging
cloudflared tunnel run deen-hidaya --loglevel debug
```

## Troubleshooting

```bash
# Test local services
curl http://localhost:3000
curl http://localhost:8000/health

# Check if cloudflared is running
ps aux | grep cloudflared

# View tunnel status
cloudflared tunnel info deen-hidaya

# Re-authenticate
cloudflared tunnel login
```

## Security Checklist

- [ ] Don't commit tunnel credentials to git
- [ ] Only share URLs with trusted people
- [ ] Stop tunnel when not needed
- [ ] Monitor access logs
- [ ] Consider enabling Cloudflare Access
- [ ] Review CORS settings in backend
- [ ] Use environment variables for tunnel config

## Quick Links

- 📖 [Full Setup Guide](./CLOUDFLARE_TUNNEL_SETUP.md)
- 📋 [Issue Template](./CLOUDFLARE_TUNNEL_ISSUE.md)
- 🔧 [Helper Script](../infra/start-tunnel.sh)
- ⚙️ [Config Example](../infra/cloudflared-config.example.yml)
- 📚 [Official Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

## Support

Need help? Check:
1. [Setup Guide Troubleshooting Section](./CLOUDFLARE_TUNNEL_SETUP.md#troubleshooting)
2. [Cloudflare Community](https://community.cloudflare.com/)
3. [cloudflared GitHub Issues](https://github.com/cloudflare/cloudflared/issues)
