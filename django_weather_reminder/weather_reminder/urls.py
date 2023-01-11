from django.urls import path, register_converter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from weather_reminder import views
from weather_reminder.converters import CoordinateConverter


register_converter(CoordinateConverter, 'coordinate')

app_name = "weather_reminder"

urlpatterns = [
    path(
        '',
        views.HomePageView.as_view(),
        name='home'),
    path(
        'api/v1/',
        views.APIRoot.as_view(),
        name='api_root'),
    path(
        'api/v1/cities/',
        views.CityAPIView.as_view(),
        name='cities'),
    path(
        'api/v1/subscriptions/',
        views.SubscriptionsListAPIView.as_view(),
        name='subscriptions_list'),
    path(
        'api/v1/subscriptions/<coordinate:latitude>/<coordinate:longitude>/',
        views.SubscriptionAPIView.as_view(),
        name='subscription'),
    path(
        'api/v1/forecasts/',
        views.WeatherForecastListAPIView.as_view(),
        name='forecasts_list'),
    path(
        'api/v1/forecasts/<coordinate:latitude>/<coordinate:longitude>/',
        views.CityWeatherForecastAPIView.as_view(),
        name='city_forecast'),
    path(
        'api/v1/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path(
        'api/v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'),
]
