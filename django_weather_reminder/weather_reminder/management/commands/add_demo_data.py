from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

from weather_reminder.service import WeatherInterface
from weather_reminder.models import Subscription, City

user_model = get_user_model()
cities = [
    {  # Kyiv
        'latitude': 50.433,
        'longitude': 30.517,
        'notification_frequency': 1
    },
    {  # Lviv
        'latitude': 49.843,
        'longitude': 24.031,
        'notification_frequency': 1
    },
    {  # Dnipro
        'latitude': 48.45,
        'longitude': 34.983,
        'notification_frequency': 1
    },
    {  # Uzhhorod
        'latitude': 48.621,
        'longitude': 22.288,
        'notification_frequency': 1
    },
    {  # Sevastopol
        'latitude': 44.623,
        'longitude': 33.536,
        'notification_frequency': 1
    },
    {  # Kharkiv
        'latitude': 49.988,
        'longitude': 36.233,
        'notification_frequency': 1
    },
    {  # Odesa
        'latitude': 46.483,
        'longitude': 30.712,
        'notification_frequency': 1
    },
    {  # Donetsk
        'latitude': 48.003,
        'longitude': 37.805,
        'notification_frequency': 1
    },
    {  # Ternopil
        'latitude': 49.553,
        'longitude': 25.595,
        'notification_frequency': 1
    },
    {  # Kherson
        'latitude': 46.656,
        'longitude': 32.618,
        'notification_frequency': 1
    },

]


class Command(BaseCommand):
    @staticmethod
    def add_demo_user() -> user_model:
        user = user_model.objects.create_user(
            username='user',
            email=f'user@example.com',
            password='123'
        )
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            primary=True,
            verified=True
        )
        return user

    @staticmethod
    def add_city(city_data: dict) -> City:
        return WeatherInterface().get_or_create_city(
            city_data['latitude'],
            city_data['longitude']
        )

    def handle(self, *args, **options):
        if City.objects.count() > 0:
            # don't run on a non-empty database
            return

        print("The procedure takes several minutes, please wait!")

        user = self.add_demo_user()

        for city_data in cities:
            city = self.add_city(city_data)
            Subscription.objects.create(user=user, city=city, notification_frequency=1)

        WeatherInterface().update_weather_forecast()

        print("Data was generated successfully!")
