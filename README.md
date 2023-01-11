# Django weather reminder



Installing and run:
    
    git clone https://github.com/NLeech/Weather-reminder.git
    cd Weather-reminder
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt

WARNING: by default server is running in debug mode. 
To turn off debug mode change DEBUG option in 'djangogramm/djangogramm/settings.py' to FALSE:

    DEBUG = False


Create 'django_weather_reminder/django_weather_reminder/local_settings.py' file with API keys and passwords. See
'django_weather_reminder/django_weather_reminder/local_settings_example.py' for example:

    """
    Django API keys, passwords and settings for django_weather_reminder project.
    
    """
    # Database
    # https://docs.djangoproject.com/en/4.1/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'django_weather_reminder',
            'USER': 'user',
            'PASSWORD': 'some_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    
    # Settings for tasks subsystem,
    # see https://docs.celeryq.dev/en/master/getting-started/backends-and-brokers/index.html
    # and setup your broker, 
    # for example Redis - https://docs.celeryq.dev/en/master/getting-started/backends-and-brokers/redis.html
    CELERY_BROKER_URL = 'redis://redis_user:redis_password@127.0.0.1'
    
    # Settings for the Django email sending interface,
    # see https://docs.djangoproject.com/en/4.1/topics/email/ for reference.
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'example_user@gmail.com'
    EMAIL_HOST_PASSWORD = 'some_password'
    EMAIL_PORT = 587
    
    # allauth provider specific settings,
    # see https://django-allauth.readthedocs.io/en/latest/configuration.html
    # and https://django-allauth.readthedocs.io/en/latest/providers.html#googlefor for reference.
    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'APP': {
                'client_id': 'SOME_CLIENT_ID',
                'secret': 'SOME_SECRET_KEY',
                'key': ''
            }
        }
    }
    
    # OpenWeather API key, please see https://openweathermap.org/api
    OPENWEATHER_API_KEY = "some_API_key"

If it needs, edit postgresql config file pg_hba.conf, refer to 
[documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server.

Next run:

    python3 django_weather_reminder/manage.py migrate
    python3 django_weather_reminder/manage.py collectstatic 

Create an admin user:

    python3 django_weather_reminder/manage.py createsuperuser

Additionally, you can fill the database with demo data - run:

    python3 django_weather_reminder/manage.py add_demo_data


Run tasks and web server:

    cd django_weather_reminder
    celery -A django_weather_reminder beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach 
    celery -A django_weather_reminder worker -l INFO --detach    
    python3 manage.py runserver 8082

Then go to [localhost:8082](localhost:8082)

Running tests:  
in virtual environment run:

    coverage run --source='.' django_weather_reminder/manage.py test weather_reminder -v 2
    coverage report -m


[GitHub](https://github.com/NLeech/Weather-reminder.git)


