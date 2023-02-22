#!/bin/sh

cd django_weather_reminder

python manage.py migrate &&
python manage.py collectstatic --noinput

python manage.py createsuperuser --noinput --username admin --email admin@example.com

if [ "${FILL_DATABASE}" == "fill" ]; then
  python manage.py add_demo_data
fi

echo "Starting celery beat"
celery -A django_weather_reminder beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting celery worker"
celery -A django_weather_reminder worker -l INFO -c 1 &

gunicorn --timeout 600 --bind 0.0.0.0:80 -w 1 django_weather_reminder.wsgi