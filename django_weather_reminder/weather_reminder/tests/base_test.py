from datetime import datetime

from django.contrib.auth import get_user_model
from django.conf import settings


from weather_reminder.models import City, Subscription, WeatherForecast

user_model = get_user_model()

sample_city = [
    {'name': 'City_40_40',
     'local_names': {'en': 'City_40_40'},
     'lat': 39.9719,
     'lon': 40.0217,
     'country': 'CC'
     },
]


def mocked_make_geocoding_request(*args, **kwargs):
    return sample_city


def mocked_make_geocoding_request_city_not_found(*args, **kwargs):
    return []


def mocked_make_weather_forecast_request(*args, **kwargs):
    return {
        'cod': '200',
        'message': 0,
        'cnt': 40,
        'list': [
            {
                'dt': 1668438000,
                'main': {
                    'temp': 28.03,
                    'feels_like': 26.66,
                    'temp_min': 27.54,
                    'temp_max': 28.03,
                    'pressure': 1015,
                    'sea_level': 1015,
                    'grnd_level': 963,
                    'humidity': 14,
                    'temp_kf': 0.49
                },
                'weather': [
                    {
                        'id': 800,
                        'main': 'Clear',
                        'description': 'clear sky',
                        'icon': '01d'
                    },
                ],
                'clouds': {'all': 3},
                'wind': {
                    'speed': 4.8,
                    'deg': 34,
                    'gust': 5.9
                },
                'visibility': 10000,
                'pop': 0,
                'sys': {'pod': 'd'},
                'dt_txt': '2022-11-14 15:00:00'},
            {
                'dt': 1668448800,
                'main': {
                    'temp': 24.16,
                    'feels_like': 23.13,
                    'temp_min': 22.11,
                    'temp_max': 24.16,
                    'pressure': 1016,
                    'sea_level': 1016,
                    'grnd_level': 963,
                    'humidity': 19,
                    'temp_kf': 2.05
                },
                'weather': [
                    {
                        'id': 800,
                        'main': 'Clear',
                        'description': 'clear sky',
                        'icon': '01n'
                    }
                ],
                'clouds': {'all': 3},
                'wind': {
                    'speed': 5.75,
                    'deg': 22,
                    'gust': 10.22
                },
                'visibility': 10000,
                'pop': 0,
                'sys': {'pod': 'n'},
                'dt_txt': '2022-11-14 18:00:00'},
            {
                'dt': 1668459600,
                'main': {
                    'temp': 19.63,
                    'feels_like': 18.25,
                    'temp_min': 19.63,
                    'temp_max': 19.63,
                    'pressure': 1017,
                    'sea_level': 1017,
                    'grnd_level': 964,
                    'humidity': 23,
                    'temp_kf': 0
                },
                'weather': [
                    {
                        'id': 800,
                        'main': 'Clear',
                        'description': 'clear sky',
                        'icon': '01n'
                    }
                ],
                'clouds': {'all': 0},
                'wind': {
                    'speed': 5.03,
                    'deg': 46,
                    'gust': 9.4
                },
                'visibility': 10000,
                'pop': 0,
                'sys': {'pod': 'n'},
                'dt_txt': '2022-11-14 21:00:00'
            },
            {
                'dt': 1668470400,
                'main': {'temp': 17.8,
                         'feels_like': 16.31,
                         'temp_min': 17.8,
                         'temp_max': 17.8,
                         'pressure': 1017,
                         'sea_level': 1017,
                         'grnd_level': 964,
                         'humidity': 26,
                         'temp_kf': 0},
                'weather': [
                    {
                        'id': 800,
                        'main': 'Clear',
                        'description': 'clear sky',
                        'icon': '01n'
                    }
                ],
                'clouds': {'all': 0},
                'wind': {
                    'speed': 5.12,
                    'deg': 50,
                    'gust': 10.53
                },
                'visibility': 10000,
                'pop': 0,
                'sys': {'pod': 'n'},
                'dt_txt': '2022-11-15 00:00:00'
            },
        ],
        'city': {
            'id': 0,
            'name': 'City_50_50',
            'coord':
                {
                    'lat': 49.8574839,
                    'lon': 49.59065964972933
                },
            'country': 'CC',
            'population': 0,
            'timezone': 3600,
            'sunrise': 1668400772,
            'sunset': 1668441444
        }
    }


class BaseTestMixin:
    user = None

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # create test users
        cls.user = user_model.objects.create_user(
            username='user',
            email=f'user@example.com',
            password='some_password'
        )

    @classmethod
    def create_sample_city(cls) -> City:
        city = sample_city[0]
        return City.objects.create(
            name=city['name'],
            latitude=city['lat'],
            longitude=city['lon'],
            country_code=city['country'],
            timezone=3600
        )

    @classmethod
    def create_test_forecast(cls, city: City, number_of_dates=1) -> None:
        for date_number in range(number_of_dates):
            WeatherForecast.objects.create(
                city=city,
                datetime=datetime(2022, 1, 1, date_number),
                temperature=1,
                temperature_feels_like=2,
                pressure=3,
                humidity=4,
                pop=5,
                cloudiness=6,
                wind_speed=7,
                weather_description='Sample description',
            )

    def setUp(self) -> None:
        self.client.force_login(self.user)


class BaseTestListMixin(BaseTestMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        for i in range(10):
            city = City.objects.create(
                name="Test city" + str(i),
                country_code='CC',
                latitude=i,
                longitude=i,
                timezone=3600
            )

            Subscription.objects.create(
                city=city,
                user=cls.user,
                notification_frequency=1
            )

    def pagination_check(self, data: dict, qty: int):
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertIn('next', data)

        self.assertEqual(data['count'], qty)

        result = data['results']
        self.assertEqual(len(result), settings.REST_FRAMEWORK['PAGE_SIZE'])
