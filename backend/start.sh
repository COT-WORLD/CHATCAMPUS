poetry run daphne -b 0.0.0.0 -p $PORT chatcampuspro.asgi:application 
poetry run celery -A chatcampuspro worker --loglevel=info'