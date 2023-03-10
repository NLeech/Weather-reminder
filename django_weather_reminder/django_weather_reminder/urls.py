"""django_weather_reminder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from authentication.views import PasswordSetView, PasswordChangeView

urlpatterns = [
    path('', include('weather_reminder.urls')),

    # fix issue : https://github.com/pennersr/django-allauth/issues/2195
    path('accounts/password/set/', PasswordSetView.as_view(), name="account_set_password"),
    path('accounts/password/change/', PasswordChangeView.as_view(), name="account_change_password"),

    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
]
