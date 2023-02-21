#!/bin/sh

cd django_weather_reminder

python3 manage.py migrate &&
python3 manage.py collectstatic --noinput

python manage.py createsuperuser --noinput --username admin --email admin@example.com

echo "Starting celery beat"
celery -A django_weather_reminder beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
#--detach

echo "Starting celery worker"
celery -A django_weather_reminder worker -l INFO -c 1 &
#--detach

gunicorn --timeout 600 --bind 0.0.0.0:80 -w 1 django_weather_reminder.wsgi