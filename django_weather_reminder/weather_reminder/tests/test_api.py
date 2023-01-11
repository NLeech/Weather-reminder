import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from parameterized import parameterized_class

from weather_reminder import serializers
from weather_reminder.models import City, Subscription
from .base_test import (
    BaseTestMixin,
    BaseTestListMixin,
    sample_city,
    mocked_make_geocoding_request,
    mocked_make_geocoding_request_city_not_found,
    mocked_make_weather_forecast_request
)

test_weather_response = [
    {
        'datetime': '2022-01-01T00:00:00Z',
        'local_datetime': '2022-01-01T01:00:00Z',
        'temperature': 1.0,
        'temperature_feels_like': 2.0,
        'pressure': 3.0,
        'humidity': 4.0,
        'pop': 5.0,
        'cloudiness': 6.0,
        'wind_speed': 7.0,
        'weather_description': 'Sample description'
    },
    {
        'datetime': '2022-01-01T01:00:00Z',
        'local_datetime': '2022-01-01T02:00:00Z',
        'temperature': 1.0,
        'temperature_feels_like': 2.0,
        'pressure': 3.0,
        'humidity': 4.0,
        'pop': 5.0,
        'cloudiness': 6.0,
        'wind_speed': 7.0,
        'weather_description': 'Sample description'
    },
    {
        'datetime': '2022-01-01T02:00:00Z',
        'local_datetime': '2022-01-01T03:00:00Z',
        'temperature': 1.0,
        'temperature_feels_like': 2.0,
        'pressure': 3.0,
        'humidity': 4.0,
        'pop': 5.0,
        'cloudiness': 6.0,
        'wind_speed': 7.0,
        'weather_description': 'Sample description'
    }
]


class APIRootTest(TestCase):
    def test_API_root(self):
        res = self.client.get(reverse('weather_reminder:api_root'))
        data = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 7)


@parameterized_class(
    ('url',),
    [
        (reverse_lazy('weather_reminder:subscriptions_list'),),
        (reverse_lazy('weather_reminder:subscription', kwargs={'latitude': 40, 'longitude': 40}),),
        (reverse_lazy('weather_reminder:forecasts_list'),),
    ]
)
class AuthenticationTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        city = cls.create_sample_city()
        Subscription.objects.create(city=city, user=cls.user, notification_frequency=1)

    def setUp(self) -> None:
        pass

    def test_unauthenticated_access(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_JWT_authentication(self):
        # get token
        res = self.client.post(
            reverse('weather_reminder:token_obtain_pair'),
            data={
                'email': self.user.email,
                'password': 'some_password'
            }
        )

        self.assertEqual(res.status_code, 200)
        token = res.json().get('access')
        self.assertNotEqual(token, None)

        auth_header = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        res = self.client.get(self.url, **auth_header)
        self.assertEqual(res.status_code, 200)


class CityAPITestList(BaseTestListMixin, TestCase):
    def test_city_list_content(self):
        res = self.client.get(reverse('weather_reminder:cities'))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.pagination_check(data, City.objects.all().count())
        result = data['results']

        found_city = City.objects.filter(
            latitude=result[0]['latitude'],
            longitude=result[0]['longitude']
        ).first()

        self.assertNotEqual(found_city, None)

        for field in serializers.CitySerializer.Meta.fields:
            self.assertEqual(result[0].get(field), getattr(found_city, field))


class SubscriptionListAPITestList(BaseTestListMixin, TestCase):
    def test_subscriptions_list_content(self):
        res = self.client.get(reverse('weather_reminder:subscriptions_list'))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.pagination_check(data, Subscription.objects.all().count())
        result = data['results']

        self.assertIn('city', result[0])
        self.assertIn('notification_frequency', result[0])

        found_city = City.objects.filter(
            latitude=result[0]['city']['latitude'],
            longitude=result[0]['city']['longitude']
        ).first()

        self.assertNotEqual(found_city, None)

        for field in serializers.CitySerializer.Meta.fields:
            self.assertEqual(result[0]['city'].get(field), getattr(found_city, field))

        self.assertEqual(result[0]['notification_frequency'], 1)


@patch(
    'weather_reminder.openweather.OpenWeatherConnector._make_weather_forecast_request',
    mocked_make_weather_forecast_request
)
class SubscriptionAddTest(BaseTestMixin, TestCase):
    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_add_subscription_existing_city(self):
        new_city = self.create_sample_city()
        data = json.dumps(
            {
                'latitude': new_city.latitude,
                'longitude': new_city.longitude,
                'notification_frequency': 1
            }
        )
        res = self.client.post(
            reverse('weather_reminder:subscriptions_list'),
            data=data,
            content_type='application/json'
        )

        self.assertEqual(res.status_code, 201)

        # no new city was created
        self.assertEqual(City.objects.all().count(), 1)

        self.assertTrue(Subscription.objects.filter(city=new_city, user=self.user).exists())

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_add_existing_subscription(self):
        new_city = self.create_sample_city()

        # add subscription
        Subscription.objects.create(user=self.user, city=new_city, notification_frequency=1)

        data = json.dumps(
            {
                'latitude': new_city.latitude,
                'longitude': new_city.longitude,
                'notification_frequency': 1
            }
        )
        res = self.client.post(
            reverse('weather_reminder:subscriptions_list'),
            data=data,
            content_type='application/json'
        )

        self.assertEqual(res.status_code, 405)

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_add_subscription_existing_nearest_city(self):
        new_city = self.create_sample_city()
        data = json.dumps(
            {
                'latitude': 40,
                'longitude': 40,
                'notification_frequency': 1
            }
        )
        res = self.client.post(
            reverse('weather_reminder:subscriptions_list'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)

        # no new city was created
        self.assertEqual(City.objects.all().count(), 1)

        self.assertTrue(Subscription.objects.filter(city=new_city, user=self.user).exists())

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_add_subscription_new_city(self):
        data = json.dumps(
            {
                'latitude': 40,
                'longitude': 40,
                'notification_frequency': 1
            }
        )
        res = self.client.post(
            reverse('weather_reminder:subscriptions_list'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        created_city = City.objects.filter(latitude=sample_city[0]['lat'], longitude=sample_city[0]['lon']).first()
        self.assertNotEqual(created_city, None)
        self.assertTrue(Subscription.objects.filter(city=created_city, user=self.user).exists())

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request_city_not_found
    )
    def test_add_non_exited_city(self):
        data = json.dumps(
            {
                'latitude': 300,
                'longitude': 300,
                'notification_frequency': 1
            }
        )
        res = self.client.post(
            reverse('weather_reminder:subscriptions_list'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 404)


class SubscriptionModifyTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.city = cls.create_sample_city()
        cls.parameters = {'latitude': cls.city.latitude, 'longitude': cls.city.longitude}

    def setUp(self) -> None:
        super().setUp()
        self.subscription = Subscription.objects.create(city=self.city, user=self.user, notification_frequency=1)

    def test_get_subscription(self):
        res = self.client.get(reverse('weather_reminder:subscription', kwargs=self.parameters))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get('notification_frequency'), self.subscription.notification_frequency)

    @patch(
        'weather_reminder.openweather.OpenWeatherConnector._make_geocoding_request',
        mocked_make_geocoding_request
    )
    def test_get_subscription_nearest_city(self):
        res = self.client.get(reverse(
            'weather_reminder:subscription',
            kwargs={'latitude': 40, 'longitude': 40}
        ))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get('notification_frequency'), self.subscription.notification_frequency)

    def test_modify_subscription(self):
        set_value = {'notification_frequency': 2}
        res = self.client.put(
            reverse('weather_reminder:subscription', kwargs=self.parameters),
            data=set_value,
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get('notification_frequency'), 2)

        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.notification_frequency, 2)

    def test_delete_subscription(self):
        res = self.client.delete(reverse('weather_reminder:subscription', kwargs=self.parameters))
        self.assertEqual(res.status_code, 204)
        with self.assertRaises(Subscription.DoesNotExist):
            self.subscription.refresh_from_db()


class WeatherForecastListTest(BaseTestListMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.city = City.objects.first()
        cls.create_test_forecast(cls.city, 3)

        # create an additional user with the separate city for user filter testing
        test_user2 = get_user_model().objects.create_user(username="-", email='user2@examole.com')
        test_city2 = City.objects.create(
            latitude=100,
            longitude=100,
            name='test city',
            country_code='TC',
            timezone=0
        )
        Subscription.objects.create(city=test_city2, user=test_user2, notification_frequency=1)

    def test_weather_forecast(self):
        res = self.client.get(reverse('weather_reminder:forecasts_list'))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.pagination_check(data, Subscription.objects.filter(user=self.user).count())
        result = data['results']

        forecast = result[0].get('forecast')
        self.assertNotEqual(forecast, None)
        self.maxDiff = None
        self.assertListEqual(forecast, test_weather_response)


class CityWeatherForecastTest(WeatherForecastListTest):
    def test_weather_forecast(self):
        res = self.client.get(reverse(
            'weather_reminder:city_forecast',
            kwargs={'latitude': self.city.latitude, 'longitude': self.city.longitude}
        ))
        self.assertEqual(res.status_code, 200)

        data = res.json()
        forecast = data.get('forecast')
        self.assertNotEqual(forecast, None)
        self.maxDiff = None
        self.assertListEqual(forecast, test_weather_response)

