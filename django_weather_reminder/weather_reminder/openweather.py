from datetime import datetime, timezone
from typing import Literal
import requests
from django.conf import settings

from weather_reminder.connector import CityData, WeatherForecastData, ServiceConnector


class OpenWeatherConnector(ServiceConnector):
    """
    Interface for openweather.org
    Contains methods for getting geodata and weather forecast from openweathermap.org.

    """
    api_key = None

    def __init__(self) -> None:
        self.api_key = settings.OPENWEATHER_API_KEY

    @staticmethod
    def _parse_geocoding_response(geeodata: list[dict] | dict) -> list[CityData]:
        """
        Parse geodata response from openweather and put it to list[CityData]
        :param geeodata: geodata openweather response
        :return: parsed response into a list of CityData

        """
        if isinstance(geeodata, dict) and geeodata.get('code', None) is not None:
            # openweather service returned wrong response
            raise ValueError(geeodata['message'])

        result = []
        for city_info in geeodata:
            result.append(CityData(
                name=city_info['name'],
                country_code=city_info['country'],
                latitude=city_info['lat'],
                longitude=city_info['lon'],
            ))

        return result

    @staticmethod
    def _parse_weather_forecast_response(weather_data: dict) -> tuple[list[WeatherForecastData], int]:
        """
        Parse weather forecast response from openweather and put it to list[WeatherForecastData]
        :param weather_data: weather forecast response
        :return: parsed response into a list of WeatherForecastData and city timezone

        """

        if weather_data['cod'] != '200':
            # openweather service returned wrong response code
            raise ValueError(weather_data['message'])

        result = []
        for moment in weather_data['list']:
            weather_description_list = [
                f'{item["main"]}: {item["description"]}'
                for item in moment['weather']
            ]

            result.append(WeatherForecastData(
                datetime=datetime.fromtimestamp(moment['dt'], tz=timezone.utc),
                temperature=float(moment['main']['temp']),
                temperature_feels_like=float(moment['main']['feels_like']),
                pressure=int(moment['main']['pressure']),
                humidity=int(moment['main']['humidity']),
                pop=int(moment['pop']),
                cloudiness=int(moment['clouds']['all']),
                wind_speed=float(moment['wind']['speed']),
                weather_description='; '.join(weather_description_list),
            ))
        city_timezone = int(weather_data['city']['timezone'])
        return result, city_timezone

    def _make_geocoding_request(
            self,
            api_method: str,
            parameters: str | dict[Literal['lat', 'lon'], float]
    ) -> list[dict]:
        """
        Request geocoding API and get city info by name or coordinates
        :param api_method: 'direct' for getting cities info by city name (direct geocoding),
                            'reverse' for getting city info by coordinates (reverse geocoding)
        :param parameters: geocoding request parameters
        :return: parsed response

        """
        # up to 5 results can be returned by one city name
        params = parameters.copy() if api_method == 'reverse' else {'q': parameters, 'limit': 5}
        params['appid'] = self.api_key

        res = requests.get(f'{settings.OPENWEATHER_GEOCODING_URL}{api_method}', params=params)
        res.raise_for_status()
        return res.json()

    def _make_weather_forecast_request(
            self,
            city: CityData
    ) -> dict:
        """
        Request weather forecast API and get forecast by coordinates
        :param city: city info
        :return: parsed response

        """
        params = {
            'lat': city.latitude,
            'lon': city.longitude,
            'units': 'metric',
            'appid': self.api_key,
        }

        res = requests.get(f'{settings.OPENWEATHER_FORECAST_URL}', params=params)
        res.raise_for_status()
        return res.json()

    def get_cities_info_by_name(self, city_name: str) -> list[CityData]:
        """
        Get city info by the name by openweather geocoding API.
        Return all cities found by the name
        :param city_name: City name
        :return: list with city info for all found cities:
                 if a city with the name not found - returns an empty list

        """
        return self._parse_geocoding_response(self._make_geocoding_request('direct', city_name))

    def get_city_info_by_coordinates(self, coordinates: dict[Literal['lat', 'lon'], float]) -> list[CityData]:
        """
        Get city info by the coordinates.
        Return city indo found by the coordinates
        :param coordinates: City coordinates
        :return: list with city info for the found city:
                 if city with the name not found - returns empty list

        """
        return self._parse_geocoding_response(self._make_geocoding_request('reverse', coordinates))

    def get_city_weather_forecast(self, city: CityData) -> tuple[list[WeatherForecastData], int]:
        """
        Get a weather forecast for the city by openweather 5 day weather forecast API
        :param city: city info
        :return: list with weather forecast by time and city timezone

        """
        return self._parse_weather_forecast_response(self._make_weather_forecast_request(city))
