from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('weather/<str:city>/', views.weather_detail, name='weather_detail'),
    path('alerts/', views.alerts, name='alerts'),
    
    # HTMX endpoints
    path('htmx/example/', views.htmx_example, name='htmx_example'),
    path('api/weather/<str:city>/', views.api_weather, name='api_weather'),
    path('api/forecast/<str:city>/', views.api_forecast, name='api_forecast'),
] 