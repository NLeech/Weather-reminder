from datetime import timedelta

from django.db import models
from django.conf import settings

from weather_reminder.connector import CityData


class LastUpdateTime(models.Model):
    """
    One-row table for storing specific Openweather last update time

    """
    key = models.CharField(
        max_length=1,
        primary_key=True,
        default='-'
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Last update time',
    )

    class Meta:
        verbose_name_plural = 'Last update time'

    def __str__(self):
        return str(self.updated)


class City(models.Model):
    """
    Cities for which weather information will be stored

    """
    name = models.CharField(
        max_length=250,
        verbose_name='City name',
    )
    country_code = models.CharField(
        max_length=2,
        verbose_name='Country code',
        help_text='ISO 3166-1 alpha-2 country code',
    )
    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name='Latitude',
        help_text='Geographical coordinates (latitude)',
    )
    longitude = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name='Longitude',
        help_text='Geographical coordinates (longitude)',
    )
    timezone = models.IntegerField(
        verbose_name='Timezone shift',
        help_text='Shift in seconds from UTC',
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'
        constraints = [
            models.UniqueConstraint(fields=['latitude', 'longitude'], name='unique_coordinates'),
        ]

    def toCityData(self) -> CityData:
        """
        Convert city instance to CityData dataclass
        :return: CityData instance

        """
        return CityData(
            name=self.name,
            country_code=self.country_code,
            latitude=float(self.latitude),
            longitude=float(self.longitude),
        )

    def __str__(self):
        return f'{self.name}, {self.country_code}'


class WeatherForecast(models.Model):
    """
    Weather forecast for the city at a certain time

    """
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='weather_forecasts',
        verbose_name='City',
    )
    datetime = models.DateTimeField(
        verbose_name='Forecast date and time',
        help_text='Time of data forecasted, UTC',
    )
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='Temperature',
        help_text='Temperature in Celsius',
    )
    temperature_feels_like = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='Temperature feels like',
        help_text='Temperature in Celsius for the human perception of weather',
    )
    pressure = models.DecimalField(
        max_digits=4,
        decimal_places=0,
        verbose_name='Atmospheric pressure',
        help_text='Atmospheric pressure on the ground level, hPa',
    )
    humidity = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        verbose_name='Humidity',
        help_text='Humidity, %',
    )
    pop = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        verbose_name='Probability of precipitation',
        help_text='Probability of precipitation, %',
    )
    cloudiness = models.DecimalField(
        max_digits=3,
        decimal_places=0,
        verbose_name='Cloudiness',
        help_text='Cloudiness, %',
    )
    wind_speed = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name='Wind speed',
        help_text='Wind speed, meter/sec',
    )
    weather_description = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Weather conditions',
        help_text='Weather conditions description (Rain, Snow, Extreme etc.)',
    )

    @property
    def local_datetime(self) -> datetime:
        return self.datetime + timedelta(seconds=self.city.timezone)

    class Meta:
        ordering = ['datetime']
        verbose_name_plural = 'Weather forecast'
        constraints = [
            models.UniqueConstraint(fields=['city', 'datetime'], name='unique_forecast'),
        ]

    def __str__(self):
        return f'{self.city}, {self.datetime}, {self.weather_description}'


class Subscription(models.Model):
    """
    User subscribed cities for retrieving weather forecasts

    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribed_cities',
    )
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='subscribed_users',
    )
    notification_frequency = models.PositiveSmallIntegerField(
        verbose_name='Notification frequency',
        help_text='Notification frequency, in hours',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'city'], name='unique_subscribe'),
        ]

    def __str__(self):
        return f'{self.user}, {self.city} - every {self.notification_frequency} hour(s)'
