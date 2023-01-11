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
