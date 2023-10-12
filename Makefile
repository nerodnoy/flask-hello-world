start:
	flask --app example --debug run --port 8000

start-guni:
	gunicorn --workers=4 --bind=127.0.0.1:8000 example:app