#!/bin/bash

# Start Celery in background
poetry run celery -A chatcampuspro worker --loglevel=info &

# Start Daphne (foreground)
poetry run daphne -b 0.0.0.0 -p $PORT chatcampuspro.asgi:application