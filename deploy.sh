#!/bin/bash

echo "📦 Pulling latest changes from Git..."
git pull origin main

echo "🔧 Rebuilding Docker containers..."
docker compose down
docker compose up -d --build

echo "📦 Running migrations..."
docker compose exec web python manage.py migrate

echo "🎨 Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

echo "✅ Done. Deployed latest version!"