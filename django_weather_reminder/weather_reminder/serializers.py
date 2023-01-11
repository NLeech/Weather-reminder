from rest_framework import serializers

from weather_reminder import models


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for cities retrieving
    """
    class Meta:
        model = models.City
        fields = (
            'name',
            'country_code',
            'latitude',
            'longitude',
            'timezone',
        )


class SubscriptionListSerializer(serializers.ModelSerializer):
    """
    Serializer for subscription creating, retrieving (objects list)

    """

    city = CitySerializer(read_only=True)
    latitude = serializers.DecimalField(max_digits=7, decimal_places=4, write_only=True)
    longitude = serializers.DecimalField(max_digits=7, decimal_places=4, write_only=True)

    class Meta:
        model = models.Subscription
        fields = (
            'city',
            'latitude',
            'longitude',
            'notification_frequency',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for subscription retrieving (object), updating and  destroying

    """

    city = CitySerializer(read_only=True)

    class Meta:
        model = models.Subscription
        fields = (
            'city',
            'notification_frequency',
        )


class WeatherForecastSerializer(serializers.ModelSerializer):
    """
    Serializer for weather forecast retrieving

    """
    class Meta:
        model = models.WeatherForecast
        fields = (
            'datetime',
            'local_datetime',
            'temperature',
            'temperature_feels_like',
            'pressure',
            'humidity',
            'pop',
            'cloudiness',
            'wind_speed',
            'weather_description',
        )


class CityWeatherForecast(serializers.ModelSerializer):
    """
    Serializer for the city weather forecast retrieving

    """
    forecast = serializers.SerializerMethodField('get_forecast')

    class Meta:
        model = models.City
        fields = CitySerializer.Meta.fields + ('forecast',)

    def get_forecast(self, city):
        return (WeatherForecastSerializer(item).data for item in city.weather_forecasts.all())
