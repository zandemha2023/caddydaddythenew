web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
worker: cd backend && celery -A app.services.queue.celery_app worker --loglevel=info
beat: cd backend && celery -A app.services.queue.celery_app beat --loglevel=info
