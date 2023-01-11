from django.contrib import admin

from weather_reminder import models

admin.site.register(models.LastUpdateTime)
admin.site.register(models.City)
admin.site.register(models.WeatherForecast)
admin.site.register(models.Subscription)
