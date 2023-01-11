from importlib import import_module

from django.test import TestCase
from django_celery_beat.models import PeriodicTask

from weather_reminder.apps import WeatherReminderConfig


class PeriodicTasksCreationTest(TestCase):
    def test_periodic_tasks_created(self):
        app_name = 'weather_reminder'
        WeatherReminderConfig(app_name, app_module=import_module(app_name)).ready()
        self.assertEqual(PeriodicTask.objects.count(), 2)
