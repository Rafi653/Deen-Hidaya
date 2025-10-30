# Cloudflare Tunnel Setup Guide

This guide will help you setup Cloudflare Tunnel to share your locally-running Deen Hidaya application with friends.

## What is Cloudflare Tunnel?

Cloudflare Tunnel creates a secure connection between your local machine and Cloudflare's network, allowing you to expose local services (like your Deen Hidaya app) to the internet without opening firewall ports or configuring your router.

## Prerequisites

- ✅ Deen Hidaya running locally (via `docker compose up`)
- ✅ Cloudflare account (free tier works)
- ✅ Domain name managed by Cloudflare (optional, can use Cloudflare's free subdomain)
- ✅ Command line access to your system

## Quick Start (Temporary Tunnel)

For quick sharing, use the temporary tunnel option:

### 1. Install cloudflared

#### macOS
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### Linux
```bash
# Debian/Ubuntu
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Or use package manager
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared
```

#### Windows
```powershell
# Using Chocolatey
choco install cloudflared

# Or download from GitHub releases
# https://github.com/cloudflare/cloudflared/releases
```

### 2. Start Temporary Tunnels

Open two terminal windows:

**Terminal 1 - Frontend Tunnel:**
```bash
cloudflared tunnel --url http://localhost:3000
```

**Terminal 2 - Backend API Tunnel:**
```bash
cloudflared tunnel --url http://localhost:8000
```

Each command will output a URL like:
```
https://randomly-generated-name.trycloudflare.com
```

### 3. Share the URLs

Share the frontend URL with your friends. They can access your local Deen Hidaya app through this URL.

> **Note:** The backend API URL is also needed for the frontend to work properly. Make sure to update the frontend configuration if needed.

### 4. Stop the Tunnels

Press `Ctrl+C` in each terminal window to stop the tunnels.

---

## Persistent Setup (Named Tunnel)

For more permanent sharing, setup a named tunnel with a custom domain.

### 1. Install cloudflared

Follow the installation instructions above if not already installed.

### 2. Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This will open a browser window. Select your Cloudflare account and authorize the tunnel.

### 3. Create a Named Tunnel

```bash
cloudflared tunnel create deen-hidaya
```

This creates a tunnel and saves credentials to:
- Linux/macOS: `~/.cloudflared/<TUNNEL_ID>.json`
- Windows: `%USERPROFILE%\.cloudflared\<TUNNEL_ID>.json`

**Important:** Save the Tunnel ID shown in the output!

### 4. Create Tunnel Configuration

Create a configuration file at:
- Linux/macOS: `~/.cloudflared/config.yml`
- Windows: `%USERPROFILE%\.cloudflared\config.yml`

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /home/your-username/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  # Frontend
  - hostname: deen-hidaya.your-domain.com
    service: http://localhost:3000
  
  # Backend API
  - hostname: api.deen-hidaya.your-domain.com
    service: http://localhost:8000
  
  # Catch-all rule (required)
  - service: http_status:404
```

**Without a custom domain:**
If you don't have a domain, you can use Cloudflare's free `trycloudflare.com` subdomain by configuring ingress rules differently, or use the quick start method above.

### 5. Configure DNS Records

For each hostname in your config, create a CNAME record:

```bash
# Frontend
cloudflared tunnel route dns deen-hidaya deen-hidaya.your-domain.com

# Backend API
cloudflared tunnel route dns deen-hidaya api.deen-hidaya.your-domain.com
```

Or manually in Cloudflare Dashboard:
1. Go to your domain's DNS settings
2. Add CNAME records:
   - Name: `deen-hidaya` → Target: `<TUNNEL_ID>.cfargotunnel.com`
   - Name: `api.deen-hidaya` → Target: `<TUNNEL_ID>.cfargotunnel.com`

### 6. Start the Tunnel

```bash
cloudflared tunnel run deen-hidaya
```

Your application is now accessible at:
- Frontend: `https://deen-hidaya.your-domain.com`
- Backend: `https://api.deen-hidaya.your-domain.com`

### 7. Run as System Service (Optional)

To run the tunnel automatically on system startup:

#### Linux (systemd)
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

#### macOS (launchd)
```bash
sudo cloudflared service install
sudo launchctl start com.cloudflare.cloudflared
```

#### Windows
```powershell
cloudflared service install
sc start cloudflared
```

---

## Docker Compose Integration (Optional)

You can add cloudflared as a service to your `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: deen-hidaya-tunnel
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    networks:
      - deen-hidaya-network
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

Get the `TUNNEL_TOKEN` from:
```bash
cloudflared tunnel token deen-hidaya
```

Add to your `.env` file:
```env
CLOUDFLARE_TUNNEL_TOKEN=your_token_here
```

---

## Configuration for Frontend

If using a named tunnel with custom domains, update your frontend environment variables:

**`.env` or frontend configuration:**
```env
NEXT_PUBLIC_API_URL=https://api.deen-hidaya.your-domain.com
```

Restart the frontend container:
```bash
docker compose restart frontend
```

---

## Security Best Practices

### 🔒 Essential Security Steps

1. **Don't Commit Credentials**
   ```bash
   # Add to .gitignore
   echo "*.json" >> .cloudflared/.gitignore
   echo "config.yml" >> .cloudflared/.gitignore
   ```

2. **Use Access Control (Recommended)**
   - Enable [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/applications/) for authentication
   - Require email verification or SSO login
   - Set up access policies for different user groups

3. **Monitor Access Logs**
   ```bash
   # View tunnel logs
   cloudflared tunnel info deen-hidaya
   
   # View real-time logs
   journalctl -u cloudflared -f  # Linux
   ```

4. **Use Environment-Specific Tunnels**
   - Development tunnel: `deen-hidaya-dev`
   - Testing tunnel: `deen-hidaya-test`
   - Never expose production databases through tunnels

5. **Rate Limiting**
   - Configure Cloudflare rate limiting rules
   - Protect API endpoints from abuse
   - Set up WAF rules if needed

6. **Review CORS Settings**
   - Update backend CORS configuration to allow tunnel domains
   - Don't use wildcard (`*`) in production

7. **Temporary Sharing**
   - Use quick start method for one-time sharing
   - Delete named tunnels when no longer needed
   ```bash
   cloudflared tunnel delete deen-hidaya
   ```

### ⚠️ What Gets Exposed

When you run a tunnel, the following are accessible:
- ✅ Frontend UI (intended)
- ✅ Backend API (intended)
- ❌ Database (should NOT be exposed - verify in config)
- ❌ Internal services (should NOT be exposed)

**Verify your configuration doesn't expose unintended services!**

---

## Troubleshooting

### Tunnel Won't Start

**Check if cloudflared is running:**
```bash
ps aux | grep cloudflared
```

**Check tunnel status:**
```bash
cloudflared tunnel info deen-hidaya
```

**View logs:**
```bash
# Linux systemd
journalctl -u cloudflared -f

# Direct run
cloudflared tunnel run deen-hidaya --loglevel debug
```

### Connection Timeout

1. Verify services are running locally:
   ```bash
   curl http://localhost:3000
   curl http://localhost:8000/health
   ```

2. Check ingress rules in `config.yml`
3. Verify DNS records are correct (may take a few minutes to propagate)

### Certificate Errors

```bash
# Re-authenticate
cloudflared tunnel login

# Recreate tunnel
cloudflared tunnel delete deen-hidaya
cloudflared tunnel create deen-hidaya
```

### Frontend Can't Connect to Backend

1. Update `NEXT_PUBLIC_API_URL` in frontend `.env`
2. Ensure CORS settings allow tunnel domain
3. Verify backend tunnel is running
4. Check browser console for specific errors

### Tunnel Disconnects Frequently

1. Check network stability
2. Update cloudflared to latest version:
   ```bash
   # macOS
   brew upgrade cloudflared
   
   # Linux
   sudo apt update && sudo apt upgrade cloudflared
   ```
3. Increase tunnel timeout in config:
   ```yaml
   tunnel: <TUNNEL_ID>
   credentials-file: /path/to/credentials.json
   grace-period: 30s
   
   ingress:
     # ... your ingress rules ...
   ```

---

## Managing Tunnels

### List All Tunnels
```bash
cloudflared tunnel list
```

### Get Tunnel Info
```bash
cloudflared tunnel info deen-hidaya
```

### Update Tunnel Routes
```bash
cloudflared tunnel route dns deen-hidaya new-subdomain.your-domain.com
```

### Delete a Tunnel
```bash
# Stop tunnel first
sudo systemctl stop cloudflared  # if running as service

# Delete tunnel
cloudflared tunnel delete deen-hidaya
```

### Cleanup DNS Records
```bash
# Remove DNS route
cloudflared tunnel route dns deen-hidaya --delete
```

---

## Cost and Limits

- **Free Tier:**
  - Unlimited tunnels
  - Unlimited bandwidth
  - No time limits
  - Standard DDoS protection

- **Paid Features (optional):**
  - Cloudflare Access for authentication
  - Advanced WAF rules
  - Analytics and logs
  - Load balancing

---

## Alternative Solutions

If Cloudflare Tunnel doesn't meet your needs:

1. **ngrok** - Similar tunneling service with free tier
2. **localtunnel** - Open-source alternative
3. **Tailscale** - VPN-based access (better for private sharing)
4. **SSH Tunneling** - Manual but free option
5. **VPS/Cloud Deployment** - More permanent solution

---

## Next Steps

After setting up the tunnel:

1. Test access from external network (mobile, friend's computer)
2. Share URLs with friends for feedback
3. Monitor usage and performance
4. Consider setting up authentication if sharing widely
5. Plan for permanent deployment when ready

---

## Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Cloudflare Access Setup](https://developers.cloudflare.com/cloudflare-one/applications/)
- [Cloudflare Zero Trust](https://www.cloudflare.com/products/zero-trust/)

---

## Getting Help

If you encounter issues:

1. Check [Cloudflare Community](https://community.cloudflare.com/)
2. Review [GitHub Issues](https://github.com/cloudflare/cloudflared/issues)
3. Open an issue in this repository
4. Tag with `infrastructure` and `role:lead` labels

---

**Happy Sharing! 🚀**
