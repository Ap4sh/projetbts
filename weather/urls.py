from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('weather/<str:city>/', views.weather_detail, name='weather_detail'),
    path('htmx-example/', views.htmx_example, name='htmx_example'),
    path('alerts/', views.alerts, name='alerts'),
    path('api/alerts/', views.api_alerts, name='api_alerts'),
    path('api/weather/<str:city>/', views.api_weather, name='api_weather'),
    path('api/forecast/<str:city>/', views.api_forecast, name='api_forecast'),
    
    # Nouvelles routes pour la recherche et le filtrage
    path('search/', views.search_city, name='search_city'),
    path('filter-alerts/', views.filter_alerts, name='filter_alerts'),
] 