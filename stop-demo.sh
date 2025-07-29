#!/bin/bash
echo "--- Shutting Down Demo Environment ---"
sudo brew services stop nginx
docker compose down -v --remove-orphans
lsof -t -i:5173 | xargs kill -9 > /dev/null 2>&1
echo "Cleanup complete."