import json
from unittest.mock import patch
from datetime import datetime, timezone

from django.test import TestCase
from django.contrib.auth import get_user_model, get_user
from django.core import mail


from weather_reminder.models import LastUpdateTime, Subscription, WeatherForecast
from weather_reminder.service import WeatherInterface, WeatherForecastSender
from .base_test import BaseTestMixin, mocked_make_weather_forecast_request


@patch(
    'weather_reminder.openweather.OpenWeatherConnector._make_weather_forecast_request',
    mocked_make_weather_forecast_request
)
class WeatherForecastTasksTest(BaseTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.city = cls.create_sample_city()
        cls.subscription = Subscription.objects.create(city=cls.city, user=cls.user, notification_frequency=2)

        # create an additional user with the separate notification frequency in subscription
        test_user2 = get_user_model().objects.create_user(username="-", email='user2@example.com')
        Subscription.objects.create(city=cls.city, user=test_user2, notification_frequency=3)

    def setUp(self) -> None:
        pass

    def test_forecast_update(self):
        WeatherInterface().update_weather_forecast()

        self.assertEqual(WeatherForecast.objects.count(), 4)
        self.assertEqual(LastUpdateTime.objects.count(), 1)

    def test_forecast_send(self):
        with patch('weather_reminder.service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2022, 1, 1, hour=2, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            WeatherForecastSender.send_weather_forecast()
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "You weather forecast.")
            self.assertIn(self.user.email, mail.outbox[0].to)
            self.assertEqual(len(mail.outbox[0].attachments), 1)
            self.assertIn('forecast', json.loads(mail.outbox[0].attachments[0][1])[0])





