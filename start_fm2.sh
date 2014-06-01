nohup celery worker -A cl.cl --loglevel=Info --concurrency=4 & > celery.output
nohup python runserver.py & > fm2_server.output
