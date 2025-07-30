#!/bin/bash

echo "🚀 Starting local development stack..."

# Start LiveKit server in background
echo "▶️ Starting LiveKit..."
livekit-server --dev > /dev/null 2>&1 &

# Wait briefly to avoid race conditions
sleep 2

# Start Docker services in detached mode
echo "📦 Starting Docker infrastructure..."
docker compose -f compose.infra.yml up --build -d

# Start FastAPI backend in background
echo "🐍 Launching FastAPI backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# Start frontend
echo "🖼️ Starting frontend..."
cd frontend || exit

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing frontend dependencies..."
  npm install
fi

# Start frontend in background
npm run dev > /dev/null 2>&1 &

cd ..

echo "✅ All services started. You can now visit the app at http://localhost:5173"
# #!/bin/bash

# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# RED='\033[0;31m'
# NC='\033[0m'

# echo -e "${GREEN}--- Preparing Demo Environment ---${NC}"

# # 1. Pre-flight Cleanup (Aggressive)
# echo "🧹 Performing pre-flight cleanup..."
# sudo brew services stop nginx > /dev/null 2>&1
# docker compose -f compose.yml down -v --remove-orphans > /dev/null 2>&1
# sudo rm -f /opt/homebrew/etc/nginx/servers/todo-app.conf
# echo "✅ Cleanup complete."

# # 2. Detect Local IP
# LOCAL_IP=$(ipconfig getifaddr en0)
# if [ -z "$LOCAL_IP" ]; then echo -e "${RED}Error: Could not detect IP.${NC}"; exit 1; fi
# echo -e "✅ Detected local IP: ${YELLOW}${LOCAL_IP}${NC}"

# # 3. Generate SSL Certificate
# CERT_DIR="$(pwd)/certs"; mkdir -p "$CERT_DIR"
# CERT_FILE="$CERT_DIR/local-cert.pem"; KEY_FILE="$CERT_DIR/local-cert-key.pem"
# echo "🔑 Generating SSL certificate..."
# mkcert -cert-file "$CERT_FILE" -key-file "$KEY_FILE" localhost "$LOCAL_IP" > /dev/null 2>&1
# echo -e "✅ Certificate generated."

# # 4. Generate NGINX Configuration
# NGINX_CONF_PATH="/opt/homebrew/etc/nginx/servers/todo-app.conf"
# echo "📝 Creating NGINX configuration..."
# sudo tee "$NGINX_CONF_PATH" > /dev/null <<EOF
# # This is the config for the NGINX server on your Mac.
# # It proxies requests to your Docker containers.

# server {
#     listen 443 ssl http2;
#     server_name localhost ${LOCAL_IP};
#     ssl_certificate ${CERT_FILE};
#     ssl_certificate_key ${KEY_FILE};

#     # This proxies ALL API traffic (HTTP and WebSocket) to the 'api' container.
#     location /api/ {
#         proxy_pass http://localhost:8000;
#         proxy_set_header Host \$host;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade \$http_upgrade;
#         proxy_set_header Connection "upgrade";
#     }

#     # This proxies all other traffic to the production 'ui' container.
#     location / {
#         proxy_pass http://localhost:5173;
#         proxy_set_header Host \$host;
#     }
# }
# EOF
# echo -e "✅ NGINX configuration created."

# # 5. Start Services
# echo "🚀 Starting services..."
# echo "-> Starting Docker stack..."
# if ! docker compose -f compose.yml up --build -d; then
#     echo -e "${RED}Docker Compose failed.${NC}"; exit 1;
# fi
# echo "✅ Docker stack is up."

# echo "-> Starting host NGINX proxy..."
# # Use the most reliable method to start/reload NGINX
# if ! sudo nginx -t; then
#     echo -e "${RED}NGINX config test failed. Aborting.${NC}"; docker compose down; exit 1;
# fi
# sudo nginx -s reload || sudo brew services start nginx
# echo "✅ NGINX is running."

# # 6. Final Instructions
# DEMO_URL="https://${LOCAL_IP}"
# echo -e "\n${GREEN}--- 🎉 Demo is Ready! ---${NC}"
# echo -e "Access the demo at: ${YELLOW}${DEMO_URL}${NC}"
# echo "${DEMO_URL}" | qrencode -t UTF8
# echo -e "\nTo shut down, run: ${YELLOW}./stop-demo.sh${NC}"
