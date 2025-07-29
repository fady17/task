#!/bin/bash

# This script acts as a toggle for the Docker Compose project.
#
# - If the project's containers are running, it stops them.
# - If the project's containers are not running, it builds and starts them.

# Use docker-compose ps to find running services for this project.
# The --quiet flag returns only container IDs.
# If any containers are running, the output will not be empty.
RUNNING_CONTAINERS=$(docker-compose ps --quiet --filter "status=running")

if [ -n "$RUNNING_CONTAINERS" ]; then
    # If the variable is not empty, containers are running.
    echo "Todo API is running. Stopping containers..."
    docker-compose down
    echo "Project stopped."
else
    # If the variable is empty, no containers are running.
    echo "Todo API is not running. Starting containers..."
    # Start in detached mode (-d) and build if necessary (--build).
    docker-compose up --build -d
    echo "Project started. API will be available at http://localhost:8000/docs"
fi