#!/bin/bash

cd django_weather_reminder

python3 manage.py migrate &&
python3 manage.py collectstatic &&

python manage.py createsuperuser --noinput --username admin --email admin@example.com

echo "Starting celery beat"
celery -A django_weather_reminder beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach

echo "Starting celery worker"
celery -A django_weather_reminder worker -l INFO -c 2 --detach

python3 manage.py runserver 0.0.0.0:8000

