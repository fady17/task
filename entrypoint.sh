#!/bin/bash

# Abort on any error
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the main container command (the CMD from the Dockerfile)
exec "$@"