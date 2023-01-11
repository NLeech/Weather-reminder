from celery import shared_task

from weather_reminder.service import WeatherInterface, WeatherForecastSender


@shared_task
def update_weather_forecast():
    WeatherInterface().update_weather_forecast()


@shared_task
def send_weather_forecast():
    WeatherForecastSender.send_weather_forecast()
