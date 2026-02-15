#!/usr/bin/env bash
set -o errexit

# Install Poetry
pip install poetry

# Configure Poetry
poetry config virtualenvs.in-project true

# Install dependencies (fix typo: oetry -> poetry)
poetry install --no-root --no-interaction


# Collect static files
poetry run python manage.py collectstatic --noinput

# Apply migrations
poetry run python manage.py migrate