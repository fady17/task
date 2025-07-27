#!/bin/bash

# --- Robust Demo Shutdown Script ---

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}--- Tearing Down Demo Environment ---${NC}"

echo "-> Stopping and removing Docker containers..."
# The -v flag removes anonymous volumes associated with the containers.
docker-compose -f compose.yml -f compose.dev.yml down -v
echo "✅ Docker stack is down."

echo "-> Stopping NGINX reverse proxy..."
sudo brew services stop nginx
echo "✅ NGINX is stopped."

# We don't need to remove the config file, as the start script will overwrite it.

echo -e "\n${GREEN}--- ✅ Shutdown Complete ---${NC}"