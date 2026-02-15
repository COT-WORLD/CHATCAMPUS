#!/bin/bash
set -e

echo "=== START DEBUG ==="
echo "PORT=$PORT"
echo "PWD=$(pwd)"
echo "FILES=$(ls -la)"
echo "==================="

# Test Django imports
poetry run python -c "import django; print('Django OK:', django.VERSION)"
poetry run python -c "from pro.asgi import application; print('ASGI OK')"

poetry run celery -A chatcampuspro worker --loglevel=info --concurrency=1 &
sleep 2

exec poetry run daphne -b 0.0.0.0 -p $PORT chatcampuspro.asgi:application