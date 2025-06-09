#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Deleting migrations directory..."
rm -rf migrations/

echo "Removing database file..."
rm -f app.db  # Replace with your DB file name if different

echo "Re-initializing Alembic..."
flask db init

echo "Creating initial migration..."
flask db migrate -m "initial migration"

echo "Upgrading database..."
flask db upgrade

echo "✅ Database and migrations reset complete."
