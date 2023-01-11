import sys

from django.apps import AppConfig


class WeatherReminderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather_reminder'
    verbose_name = 'Weather reminder'

    @staticmethod
    def _check_or_add_task(schedule, name: str, task: str) -> None:
        """
        Creates a periodic task if it doesn't exist
        :param schedule: task schedule
        :param name: task description
        :param task: task name

        """
        from django_celery_beat.models import PeriodicTask

        try:
            PeriodicTask.objects.get(
                name=name,
                task=task,
            )
        except PeriodicTask.DoesNotExist:
            PeriodicTask.objects.create(
                crontab=schedule,
                name=name,
                task=task,
            )

    def ready(self):
        if 'migrate' in sys.argv:
            # avoid executing code if it called with "manage.py migrate"
            return

        from django_celery_beat.models import CrontabSchedule

        # execute at 50 minutes past the hour every hour
        weather_forecast_update_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='50',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # execute every hour
        weather_forecast_send_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='*/1',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # check necessary tasks existence and create them if they don't exist
        self._check_or_add_task(
            schedule=weather_forecast_update_schedule,
            name='Update weather forecast from the weather service',
            task='weather_reminder.tasks.update_weather_forecast'
        )

        self._check_or_add_task(
            schedule=weather_forecast_send_schedule,
            name='Send weather forecast to users',
            task='weather_reminder.tasks.send_weather_forecast'
        )
