from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from weather_reminder.models import City, Subscription
from weather_reminder.views import display_forecast_fields
from .base_test import BaseTestListMixin


class HomePageViewTest(BaseTestListMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

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

    def test_homepage(self):
        res = self.client.get(reverse('weather_reminder:home'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(response=res, template_name='weather_reminder/homepage.html')

        context = res.context_data
        self.assertIn('object_list', context)
        self.assertIn('display_forecast_fields', context)

        self.assertListEqual(context['display_forecast_fields'], display_forecast_fields)
        self.assertEqual(len(context['object_list']), Subscription.objects.filter(user=self.user).count())

    def test_homepage_no_logged_user(self):
        self.client.logout()
        res = self.client.get(reverse('weather_reminder:home'))
        self.assertEqual(res.status_code, 200)

        context = res.context_data
        self.assertIn('object_list', context)
        self.assertEqual(len(context['object_list']), 3)
