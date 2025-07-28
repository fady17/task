#!/bin/bash
GREEN='\033[0;32m'
NC='\033[0m'
echo -e "${GREEN}--- Tearing Down Demo Environment ---${NC}"
docker-compose -f compose.yml -f compose.dev.yml down -v
sudo brew services stop nginx
echo -e "\n${GREEN}--- ✅ Shutdown Complete ---${NC}"