#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install poetry && poetry config virtualenvs.in-project true && poetry install --no-root --no-interaction

poetry run python manage.py collectstatic --noinput


# Apply any outstanding database migrations
poetry run python manage.py migrate