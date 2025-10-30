#!/bin/bash
# Deen Hidaya - Cloudflare Tunnel Quick Start Script
# This script helps you quickly start a Cloudflare tunnel for local sharing

set -e

echo "🌐 Deen Hidaya - Cloudflare Tunnel Setup"
echo "========================================"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared is not installed!"
    echo ""
    echo "Please install cloudflared first:"
    echo ""
    echo "macOS:"
    echo "  brew install cloudflare/cloudflare/cloudflared"
    echo ""
    echo "Linux (Debian/Ubuntu):"
    echo "  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    echo "  sudo dpkg -i cloudflared-linux-amd64.deb"
    echo ""
    echo "For other systems, see: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/"
    exit 1
fi

echo "✅ cloudflared is installed"
echo ""

# Check if services are running
echo "Checking if Deen Hidaya services are running..."
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend is not running on port 3000"
    echo "   Please start services with: docker compose up -d"
    echo ""
fi

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend is not running on port 8000"
    echo "   Please start services with: docker compose up -d"
    echo ""
fi

echo ""
echo "Choose tunnel mode:"
echo "1) Quick/Temporary tunnel (recommended for first time)"
echo "2) Named/Persistent tunnel (requires Cloudflare account)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Starting temporary tunnels..."
        echo ""
        echo "📱 These URLs will be generated and can be shared with friends:"
        echo ""
        
        # Create a temporary directory for tunnel logs
        TUNNEL_LOG_DIR="/tmp/deen-hidaya-tunnels"
        mkdir -p "$TUNNEL_LOG_DIR"
        
        # Start frontend tunnel in background
        echo "Starting frontend tunnel..."
        cloudflared tunnel --url http://localhost:3000 > "$TUNNEL_LOG_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        
        # Wait a moment for the tunnel to initialize
        sleep 5
        
        # Extract frontend URL from log
        FRONTEND_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG_DIR/frontend.log" | head -1)
        
        # Start backend tunnel in background
        echo "Starting backend tunnel..."
        cloudflared tunnel --url http://localhost:8000 > "$TUNNEL_LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
        
        # Wait a moment for the tunnel to initialize
        sleep 5
        
        # Extract backend URL from log
        BACKEND_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG_DIR/backend.log" | head -1)
        
        echo ""
        echo "✅ Tunnels are running!"
        echo ""
        echo "📌 Share these URLs with friends:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Frontend (Main App):  $FRONTEND_URL"
        echo "Backend API:          $BACKEND_URL"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "⚠️  IMPORTANT:"
        echo "   - These URLs are temporary and will change when you restart"
        echo "   - Anyone with these URLs can access your local app"
        echo "   - The tunnels will stop when you close this terminal"
        echo ""
        echo "📝 Logs are saved in: $TUNNEL_LOG_DIR"
        echo ""
        echo "To stop the tunnels, press Ctrl+C"
        echo ""
        
        # Save PIDs to a file so we can clean up
        echo "$FRONTEND_PID" > "$TUNNEL_LOG_DIR/frontend.pid"
        echo "$BACKEND_PID" > "$TUNNEL_LOG_DIR/backend.pid"
        
        # Function to cleanup tunnels on exit
        cleanup() {
            echo ""
            echo "Stopping tunnels..."
            kill $FRONTEND_PID 2>/dev/null || true
            kill $BACKEND_PID 2>/dev/null || true
            rm -f "$TUNNEL_LOG_DIR/frontend.pid" "$TUNNEL_LOG_DIR/backend.pid"
            echo "✅ Tunnels stopped"
        }
        
        trap cleanup EXIT INT TERM
        
        # Wait for user to stop
        wait
        ;;
        
    2)
        echo ""
        echo "Setting up named tunnel..."
        echo ""
        
        # Check if user is authenticated
        if [ ! -f ~/.cloudflared/cert.pem ]; then
            echo "⚠️  You need to authenticate with Cloudflare first."
            echo ""
            read -p "Authenticate now? (y/n): " auth_choice
            if [ "$auth_choice" = "y" ]; then
                cloudflared tunnel login
            else
                echo "Exiting. Run 'cloudflared tunnel login' when ready."
                exit 1
            fi
        fi
        
        echo "✅ Authenticated with Cloudflare"
        echo ""
        
        # Check if tunnel already exists
        TUNNEL_NAME="deen-hidaya"
        if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
            echo "📝 Tunnel '$TUNNEL_NAME' already exists"
            read -p "Use existing tunnel? (y/n): " use_existing
            if [ "$use_existing" != "y" ]; then
                echo "Please use a different tunnel name or delete the existing one."
                exit 1
            fi
        else
            echo "Creating tunnel '$TUNNEL_NAME'..."
            cloudflared tunnel create "$TUNNEL_NAME"
            echo "✅ Tunnel created"
            echo ""
        fi
        
        echo ""
        echo "⚠️  NEXT STEPS:"
        echo ""
        echo "1. Create configuration file at ~/.cloudflared/config.yml"
        echo "2. Add DNS routes for your domain"
        echo "3. Run: cloudflared tunnel run $TUNNEL_NAME"
        echo ""
        echo "See docs/CLOUDFLARE_TUNNEL_SETUP.md for detailed instructions."
        echo ""
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
