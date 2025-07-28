#!/bin/bash

# --- Intelligent Docker Compose Service Restart & Rebuild Script ---
# This script rebuilds and restarts a specified service and any other
# services that depend on it.

# Exit immediately if a command fails
set -e

# --- Color Codes ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# --- 1. Input Validation ---
if [ -z "$1" ]; then
    echo -e "${RED}Error: No service name provided.${NC}"
    echo -e "Usage: ${YELLOW}./restart-service.sh <service_name>${NC}"
    echo -e "Example: ${YELLOW}./restart-service.sh api${NC}"
    exit 1
fi

TARGET_SERVICE=$1
COMPOSE_FILES="-f compose.yml -f compose.dev.yml"

# --- 2. Prerequisite Check ---
if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: 'yq' not found.${NC} Please run: ${YELLOW}brew install yq${NC}"; exit 1;
fi
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: 'docker-compose' not found.${NC}"; exit 1;
fi

echo -e "🔎 Analyzing dependencies for service: ${YELLOW}${TARGET_SERVICE}${NC}"

# --- 3. Find Dependent Services ---
SERVICES_TO_RESTART=("$TARGET_SERVICE")
MERGED_CONFIG=$(docker-compose $COMPOSE_FILES config)
ALL_SERVICES=$(echo "$MERGED_CONFIG" | yq '.services | keys | .[]')

for service in $ALL_SERVICES; do
    if [ "$service" == "$TARGET_SERVICE" ]; then
        continue
    fi
    dependencies=$(echo "$MERGED_CONFIG" | yq ".services.${service}.depends_on // [] | .[]")
    if [[ "$dependencies" =~ "$TARGET_SERVICE" ]]; then
        echo -e "  -> Found dependent service: ${YELLOW}${service}${NC}"
        if [[ ! " ${SERVICES_TO_RESTART[@]} " =~ " ${service} " ]]; then
            SERVICES_TO_RESTART+=("$service")
        fi
    fi
done

# --- 4. Execute the Rebuild and Restart Command ---
echo -e "\n${GREEN}The following services will be rebuilt and restarted in order:${NC}"
printf "  - %s\n" "${SERVICES_TO_RESTART[@]}"

echo -e "\n🚀 Executing rebuild and restart command..."
# The new command uses 'up' with the '--build' and '--force-recreate' flags.
# '--no-deps' is crucial to prevent restarting the entire stack.
docker-compose $COMPOSE_FILES up --build --force-recreate --no-deps -d "${SERVICES_TO_RESTART[@]}"

echo -e "\n${GREEN}--- ✅ Rebuild and Restart Complete ---${NC}"
echo -e "To view logs, run: ${YELLOW}docker-compose logs -f ${SERVICES_TO_RESTART[*]}${NC}"