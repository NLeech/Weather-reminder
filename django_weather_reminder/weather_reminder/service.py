from datetime import datetime, timezone
from collections.abc import Iterable

from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer

from weather_reminder.models import City, WeatherForecast, LastUpdateTime, Subscription
from weather_reminder.openweather import OpenWeatherConnector
from weather_reminder.connector import ServiceConnector, WeatherForecastData, CityData, round_coordinate
from weather_reminder.serializers import CityWeatherForecast


user_model = settings.AUTH_USER_MODEL


class CityNotFound(NotFound):
    """
    Exception
    """
    city_data: CityData = None

    def __init__(self, *args, **kwargs):
        self.city_data = kwargs.pop('city_data', None)
        super().__init__(*args, **kwargs)


class WeatherInterface:
    """
    Interface for online weather services.
    Contains methods for get geodata and weather forecast from online weather services
    and store them into database.

    """
    service_connector: ServiceConnector

    def __init__(self, service_connector=None):
        self.service_connector = service_connector

        if self.service_connector is None:
            self.service_connector = OpenWeatherConnector()

    @staticmethod
    def _save_weather_forecasts(city: City, weather_forecasts: list[WeatherForecastData]) -> None:
        """
        Save weather forecasts to the database
        :param city: City instance
        :param weather_forecasts: received from the weather service forecast

        """
        # possible it needs to make a bulk update or create
        for forecast in weather_forecasts:
            WeatherForecast.objects.update_or_create(city=city, **forecast.__dict__)

    def get_nearest_city(self, latitude: float, longitude: float) -> CityData | None:
        """
        Get the nearest city from the weather service by the coordinates
        :param latitude: latitude coordinate
        :param longitude: longitude coordinate
        :return: City data or None if no city near the coordinates

        """
        city_info = self.service_connector.get_city_info_by_coordinates(
            {
                'lat': latitude,
                'lon': longitude,
            }
        )

        if len(city_info) == 0:
            return None

        return city_info[0]

    def get_city(self, latitude: float, longitude: float) -> City:
        """
        Get a city by the coordinates from the database, if a city with such coordinates was not found in the database -
        try to find the nearest city in the database.
        Raise CityNotFound exception if the nearest city with such coordinates was not found in db
        Raise NotFound exception if no city with such coordinates
        :param latitude: latitude coordinate
        :param longitude: longitude coordinate
        :return: City instance

        """
        try:
            city = City.objects.get(latitude=round_coordinate(latitude), longitude=round_coordinate(longitude))
        except City.DoesNotExist:
            # get the nearest city by the coordinates
            city_data = self.get_nearest_city(latitude, longitude)

            if city_data is None:
                raise NotFound(detail=f'City with coordinates latitude: {latitude}, longitude: {longitude} not found!')

            # if the nearest city is found, check city already exists in the database, otherwise rise exception
            try:
                city = City.objects.get(latitude=city_data.latitude, longitude=city_data.longitude)
            except City.DoesNotExist:
                raise CityNotFound(
                    city_data=city_data,
                    detail=f'City with coordinates latitude: {latitude}, longitude: {longitude} not found!'
                )

        return city

    def get_or_create_city(self, latitude: float, longitude: float) -> City:
        """
        Get a city by the coordinates from the database, if a city with such coordinates was not found in the database -
        try to find the nearest city and create a new city from the weather service info by the coordinates.
        Raise NotFound exception if no city with such coordinates was found neither in db nor in the weather service
        :param latitude: latitude coordinate
        :param longitude: longitude coordinate
        :return: City instance

        """
        try:
            city = self.get_city(latitude=latitude, longitude=longitude)
        except CityNotFound as e:
            city = self.create_city(e.city_data)

        return city

    def create_city(self, city_data: CityData) -> City:
        """
        Create a new city from the weather service info.
        Also, get initial weather forecast and store it to the database
        :param city_data: city data from the weather service
        :return: City instance

        """
        # add timezone fot the city
        # take timezone from weather forecast
        weather_forecast, timezone = self.service_connector.get_city_weather_forecast(city_data)

        city = City.objects.create(**city_data.__dict__, timezone=timezone)
        city.save()

        self._save_weather_forecasts(city=city, weather_forecasts=weather_forecast)

        return city

    def update_city_weather_forecast(self, city: City) -> None:
        """
        Gets city weather forecast data from the weather service,
        clear all previous forecasts for the city and store received forecasts in the database.
        :param city: city

        """

        weather_forecast, timezone = self.service_connector.get_city_weather_forecast(city=city.toCityData())

        WeatherForecast.objects.filter(city=city).delete()

        self._save_weather_forecasts(city, weather_forecast)

    def update_weather_forecast(self) -> None:
        """
        Gets weather forecast data from the weather service for all cities in the database,
        clear all previous forecasts and store received forecasts in the database.

        """
        for city in City.objects.all():
            self.update_city_weather_forecast(city)

        LastUpdateTime.objects.update_or_create()


class WeatherForecastSender:
    """
    Makes sending weather forecasts to users according to the users' subscriptions

    """
    @staticmethod
    def _get_forecast_json_for_city_list(city_list: Iterable[City]) -> str:
        result = []
        for city in city_list:
            serializer = CityWeatherForecast(city)
            result.append(serializer.data)

        return JSONRenderer().render(result)

    @staticmethod
    def _get_subscriptions_for_sending() -> list[Subscription]:
        """
        Gets subscriptions for sending according to a subscription notification period
        :return Subscriptions with a notification period that fits entirely into the number
        of hours from 2022.01.01 to now

        """
        # number of hours from 2022.01.01 to now
        delta = datetime.now(timezone.utc) - datetime(2022, 1, 1, tzinfo=timezone.utc)
        hours = int(delta.total_seconds() // (60*60))

        subscriptions_for_sending = [
            subscription
            for subscription in Subscription.objects.all().select_related('user').select_related('city')
            if divmod(hours, subscription.notification_frequency)[1] == 0
        ]

        return subscriptions_for_sending

    @staticmethod
    def _send_forecast_email_to_user(user: user_model, subscriptions: list[Subscription]) -> None:
        """
        Sends forecast to user by email
        :param user: user
        :param subscriptions: subscriptions for sending (all)

        """

        # get city list from subscription
        city_list = set([
            sub.city
            for sub in subscriptions
            if sub.user == user
        ])

        mail = EmailMessage(
            subject='You weather forecast.',
            body='',
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )

        mail.attach(
            filename='forecast.json',
            content=WeatherForecastSender._get_forecast_json_for_city_list(city_list),
            mimetype='application/json'
        )

        try:
            mail.send()
        except BadHeaderError:
            # TODO handle sending exception
            pass

    @staticmethod
    def _send_forecasts_by_email(subscriptions: list[Subscription]) -> None:
        """
        Sends forecast to all users in subscriptions by email
        :param subscriptions: subscriptions for sending

        """
        # get users list
        users = set([sub.user for sub in subscriptions])

        for user in users:
            WeatherForecastSender._send_forecast_email_to_user(user, subscriptions)

    @staticmethod
    def send_weather_forecast() -> None:
        """
        Sends forecast to users for subscriptions with a notification period that fits entirely into the number
        of hours from 2022.01.01 to now

        """
        subscriptions = WeatherForecastSender._get_subscriptions_for_sending()
        WeatherForecastSender._send_forecasts_by_email(subscriptions)
