#!/bin/bash

# Setup PostgreSQL with Podman for Jamanger FastAPI app

echo "🐘 Setting up PostgreSQL with Podman..."

# Create a pod for the database
echo "Creating pod..."
podman pod create --name jamvote-pod -p 5432:5432

# Run PostgreSQL container
echo "Starting PostgreSQL container..."
podman run -d \
  --name jamvote-postgres \
  --pod jamvote-pod \
  -e POSTGRES_DB=jamvote \
  -e POSTGRES_USER=jamvote \
  -e POSTGRES_PASSWORD=jamvote \
  -v jamvote-data:/var/lib/postgresql/data \
  postgres:15

echo "⏳ Waiting for PostgreSQL to start..."
sleep 10

# Test connection
echo "Testing PostgreSQL connection..."
podman exec jamvote-postgres psql -U jamvote -d jamvote -c "SELECT version();"

echo "✅ PostgreSQL is ready!"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: jamvote"
echo "  Username: jamvote"
echo "  Password: jamvote"
echo ""
echo "To stop the database:"
echo "  podman pod stop jamvote-pod"
echo ""
echo "To start the database:"
echo "  podman pod start jamvote-pod"
echo ""
echo "To remove everything:"
echo "  podman pod rm -f jamvote-pod"
echo "  podman volume rm jamvote-data"

