#!/bin/bash
docker container stop $(docker container ls -aq) && docker system prune -af --volumes
# Build and run containers
docker-compose up -d

# Hack to wait for postgres container to be up before running alembic migrations
sleep 10;

# Run migrations
docker-compose run --rm backend alembic upgrade head

# Create initial data
# docker-compose run --rm backend python3 app/initial_data.py
