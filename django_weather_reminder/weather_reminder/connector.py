from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


def round_coordinate(coordinate: float) -> float:
    # 100m accuracy is enough
    return round(coordinate, 4)


@dataclass()
class CityData:
    """
    Contains city information
        name: city name
        country: ISO 3166-1 alpha-2 country code
        latitude - latitude
        longitude - longitude

    """
    name: str
    country_code: str
    latitude: float
    longitude: float

    def __post_init__(self):
        # 100m accuracy is enough
        self.latitude = round_coordinate(self.latitude)
        self.longitude = round_coordinate(self.longitude)


@dataclass(frozen=True)
class WeatherForecastData:
    """
    Contains the weather forecast for a certain city at a certain time:
        time: Time of data forecasted, UTC
        temperature: Temperature in Celsius
        temperature_feels_like: Temperature in Celsius for the human perception of weather
        pressure: Atmospheric pressure on the ground level, hPa
        humidity: Humidity, %
        pop: Probability of precipitation, %
        clouds: Cloudiness, %
        wind_speed: Wind speed, meter/sec
        weather: Weather conditions description (Rain, Snow, Extreme etc.)

    """
    datetime: datetime
    temperature: float
    temperature_feels_like: float
    pressure: int
    humidity: int
    pop: int
    cloudiness: int
    wind_speed: float
    weather_description: str


class ServiceConnector(ABC):
    """
    Base class for weather services
    You should redefine methods:
        get_cities_info_by_name
        get_city_weather_forecast
    in your service implementation.

    """
    @abstractmethod
    def get_cities_info_by_name(self, city_name: str) -> list[CityData]:
        """
        Get city info by the name from a weather service.
        Return all cities info found by the name
        :param city_name: City name
        :return: list with city info for all found cities:
                 if a city with the name not found - returns an empty list

        """
        pass

    @abstractmethod
    def get_city_info_by_coordinates(self, coordinates: dict[Literal['lat', 'lon'], float]) -> list[CityData]:
        """
        Get city info by the coordinates.
        Return all cities indo found by the name
        :param coordinates: City coordinates
        :return: list with city info for all found cities:
                 if city with the name not found - returns empty list

        """
        pass

    @abstractmethod
    def get_city_weather_forecast(self, city: CityData) -> list[WeatherForecastData]:
        """
        Get weather forecast for the city
        :param city: city
        :return: list with weather forecast by time

        """
        pass
