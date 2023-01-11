from typing import Literal
import random

from django.views import generic
from django.db import IntegrityError
from rest_framework import generics as rest_generics
from rest_framework import views as rest_views
from rest_framework import mixins as rest_mixins
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from weather_reminder import models
from weather_reminder import serializers
from weather_reminder.service import WeatherInterface


display_forecast_fields = [
    'temperature',
    'temperature_feels_like',
    'pressure',
    'humidity',
    'pop',
    'cloudiness',
    'wind_speed',
]


class CoordinatesParserMixin:
    """
    Contains parser for coordinates fields in the URL
    """
    lookup_fields = (
        'latitude',
        'longitude'
    )

    def parse_coordinates(self) -> dict[Literal['latitude', 'longitude'], float]:
        for field in self.lookup_fields:
            assert field in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, field)
            )

        filter_fields = {}
        for field in self.lookup_fields:
            filter_fields[field] = self.kwargs[field]

        return filter_fields


class HomePageView(generic.ListView):
    template_name = 'weather_reminder/homepage.html'

    model = models.City

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # return up to 3 random cities
            return random.sample(list(models.City.objects.all()), min(models.City.objects.all().count(), 3))
        else:
            return models.City.objects.filter(id__in=self.request.user.subscribed_cities.values('city')).all()\
                .prefetch_related('weather_forecasts')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['display_forecast_fields'] = display_forecast_fields

        return context


class APIRoot(rest_views.APIView):
    """
    API for subscriptions management.
    For some API calls, you need to obtain an authentication token from
    http://weather-reminder-production-101664.up.railway.app/api/v1/token/
    and add it to your query header as: 'HTTP_AUTHORIZATION': 'Bearer ' + your_token.

    """
    def get(self, request):
        return Response(
            {
                'City list': reverse(
                    'weather_reminder:cities',
                    request=request),
                'Subscriptions list': reverse(
                    'weather_reminder:subscriptions_list',
                    request=request),
                'Subscription': reverse(
                    'weather_reminder:subscription',
                    kwargs={
                        'latitude': 0,
                        'longitude': 0},
                    request=request),
                'Weather forecast for the city list': reverse(
                    'weather_reminder:forecasts_list',
                    request=request),
                'Weather forecast for the city': reverse(
                    'weather_reminder:city_forecast',
                    kwargs={
                        'latitude': 0,
                        'longitude': 0},
                    request=request),
                'Get authentication token': reverse(
                    'weather_reminder:token_obtain_pair',
                    request=request),
                'Refresh authentication token': reverse(
                    'weather_reminder:token_refresh',
                    request=request),
            })


class CityAPIView(rest_generics.ListAPIView):
    """
    Returns a list of all cities in the system.
    """
    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer

    def get_view_name(self):
        return 'City list'


class SubscriptionsListAPIView(rest_mixins.CreateModelMixin, rest_generics.ListAPIView):
    """
    Returns subscriptions list for the user.
    User can add a new subscription.
    """
    serializer_class = serializers.SubscriptionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.subscribed_cities.all().select_related('city')

    def get_view_name(self):
        return 'Subscriptions list'

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # get existing city or create city by coordinates with the weather service
        city = WeatherInterface().get_or_create_city(
            serializer.validated_data.pop('latitude'),
            serializer.validated_data.pop('longitude'),
        )

        # if user subscription for the city already exists, raise MethodNotAllowed
        try:
            serializer.save(user=self.request.user, city=city)
        except IntegrityError as e:
            raise MethodNotAllowed(
                method='', detail=f'Subscription for the city: {city} with coordinates '
                                  f'latitude: {city.latitude}, longitude: {city.longitude} already exists!'
            )


class SubscriptionAPIView(CoordinatesParserMixin, rest_generics.RetrieveUpdateDestroyAPIView):
    """
    Returns user subscription by the coordinates.
    User can modify or delete subscription.

    """
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_view_name(self):
        return 'Subscription'

    def get_queryset(self):
        user = self.request.user
        return user.subscribed_cities.all().select_related('city')

    def get_object(self):
        # find city by coordinates
        city = WeatherInterface().get_city(**self.parse_coordinates())

        # Lookup the subscription
        obj = get_object_or_404(self.get_queryset(), **{'city': city})
        self.check_object_permissions(self.request, obj)
        return obj


class WeatherForecastListAPIView(rest_generics.ListAPIView):
    """
    Returns a list with the weather forecast for all user-subscribed cities.

    """
    serializer_class = serializers.CityWeatherForecast
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return models.City.objects.filter(id__in=user.subscribed_cities.values('city')).all()\
            .prefetch_related('weather_forecasts')

    def get_view_name(self):
        return 'Weather forecast for the city list'


class CityWeatherForecastAPIView(CoordinatesParserMixin, rest_generics.RetrieveAPIView):
    """
    Returns a list with the weather forecast for the city.

    """
    serializer_class = serializers.CityWeatherForecast

    def get_view_name(self):
        return 'Weather forecast for the city'

    def get_object(self):
        # find city by coordinates
        return WeatherInterface().get_city(**self.parse_coordinates())


