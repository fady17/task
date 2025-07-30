#!/bin/bash

echo "🛑 Stopping local development stack..."

# Stop docker containers
docker compose -f compose.infra.yml down

# Kill LiveKit and FastAPI processes
echo "🧹 Cleaning up background processes..."
pkill -f livekit-server
pkill -f "uvicorn app.main:app"
lsof -ti :5173 | xargs kill
echo "✅ Dev stack stopped."

# #!/bin/bash
# echo "--- Shutting Down Demo Environment ---"
# sudo brew services stop nginx
# docker compose down -v --remove-orphans
# lsof -t -i:5173 | xargs kill -9 > /dev/null 2>&1
# echo "Cleanup complete."