daphne -b 0.0.0.0 -p $PORT chatcampuspro.asgi:application 
celery -A chatcampuspro worker --loglevel=info'