# Weather reminder

A weather notification application for the subscribed cities via email.  
The application is provided API for getting information about the weather. 
User (or third-party service) can register and get auth by JWT 
The user can subscribe/unsubscribe to one or a few cities with a period of notification parameter (1, 3, 6, 12 hours), etc. 
The user can edit the parameters of subscribing or delete subscriptions. 
The user can get a list of subscribing

# Local deployment:
Installing and run:

Require python~=3.10
```
git clone https://github.com/NLeech/Weather-reminder.git
cd Weather-reminder
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
chmod 755 postgres/postgres_init.sh
```

Create ".env" file with your credentials.
For example:
```
# Django secret key, example of how to create: https://www.educative.io/answers/how-to-generate-a-django-secretkey
SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Postgres database credentials
PG_DATABASE=weather_reminder
PG_USER=db_user
PG_PASSWD=dbuser_strong_password
PG_DATABASE_ADDRESS=127.0.0.1
PG_DATABASE_PORT=5432

# Redis
REDIS_CREDENTIALS='redis_user:redis_password@'
REDIS_ADDRESS='127.0.0.1'

# Credentials for email sending
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=example_user@gmail.com
EMAIL_HOST_PASSWORD=XXXXXXXXXXXXXXXX
EMAIL_PORT=587

# credentials for google authentication,
# please see: https://django-allauth.readthedocs.io/en/latest/providers.html#google
GOOGLE_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenWeather API key, please see https://openweathermap.org/api
OPENWEATHER_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# The URLs of the application in production. You must enter your real application URLs here, separated by commas.
APPLICATION_URLS=weather-reminder.net,192.168.1.1
```

If the database and database user don't exist, you can create them by running:
```    
export $(grep -v '^#' .env | grep -v '^\s*$' | xargs -d '\n') && \
sudo -E -u postgres bash ./postgres/postgres_init.sh
```
If it needs, edit postgresql config file pg_hba.conf, refer to 
[documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server.

WARNING: by default server is running in debug mode. 
To turn off debug mode change DEBUG option in 'Weather-reminder/django_weather_reminder/settings.py' to FALSE:
```
DEBUG = False
```
Next run:
```
cd django_weather_reminder
python manage.py migrate
python manage.py collectstatic 
```

Create an admin user:
```
python manage.py createsuperuser
```

Optionally, run command to fill the database with demo data. 
```
python manage.py add_demo_data
```

Run:
```
celery -A django_weather_reminder beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach
celery -A django_weather_reminder worker -l INFO -c 2 #--detach
python manage.py runserver 8080
```
Then go to [localhost:8080](localhost:8080)

Running tests:  
in virtual environment run:
```
coverage run --source='.' djangogramm/manage.py test auth_with_email files_cleanup posts -v 2
coverage report -m
```
# Docker deployment:

Get source:
```
git clone https://github.com/NLeech/Weather-reminder.git
cd Weather-reminder
```

Create ".env" file with your credentials.
For example, see ".env_example" file:
```
# Django secret key, example of how to create: https://www.educative.io/answers/how-to-generate-a-django-secretkey
SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Django superuser password for automatic superuser generation.
# During the first container start, will be created superuser "admin" with email admin@example.com
# with that password:
SUPERUSER_PASSWORD=django_superuser_strong_password

# Postgres database credentials
PG_DATABASE=weather_reminder
PG_USER=db_user
PG_PASSWD=dbuser_strong_password
PG_DATABASE_PORT=5432
# Postgres superuser (postgres) password for the docker DB image creation
POSTGRES_PASSWORD=postgres_admin_user_strong_password

# Credentials for email sending
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=example_user@gmail.com
EMAIL_HOST_PASSWORD=XXXXXXXXXXXXXXXX
EMAIL_PORT=587

# credentials for google authentication,
# please see: https://django-allauth.readthedocs.io/en/latest/providers.html#google
GOOGLE_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenWeather API key, please see https://openweathermap.org/api
OPENWEATHER_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# The URLs of the application in production. You must enter your real application URLs here, separated by commas.
APPLICATION_URLS=weather-reminder.net,192.168.1.1
```

Build images:
    
    docker compose build

Run containers:

    docker compose up -d

Optionally, you can fill the database with demo data for the first container run. 
For this run your container with the command:

    FILL_DATABASE="fill" docker compose up
 
Then go to [localhost](localhost)

[GitHub](https://github.com/NLeech/Weather-reminder)
