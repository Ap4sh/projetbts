from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Alert
from .services.weather_api import OpenWeatherMapService

def home(request):
    # Initialiser le service météo
    weather_service = OpenWeatherMapService()
    
    # Liste des principales villes françaises
    cities = [
        "Paris", "Marseille", "Lyon", "Toulouse", "Nice", 
        "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille"
    ]
    
    # Récupérer les données météo pour chaque ville
    cities_weather = []
    for city in cities:
        weather_data = weather_service.get_current_weather(city)
        if weather_data:
            cities_weather.append(weather_data)
    
    # Récupérer les alertes météo (pour l'instant, on utilise les alertes de la base de données)
    alerts = Alert.objects.all().order_by('-date_debut')[:5]
    
    context = {
        'cities_weather': cities_weather,
        'alerts': alerts
    }
    
    return render(request, 'weather/home.html', context)

@login_required
def profile(request):
    # Si l'utilisateur est connecté et a un profil avec une ville définie
    user_profile = request.user.userprofile if hasattr(request.user, 'userprofile') else None
    
    weather_data = None
    if user_profile and user_profile.ville:
        # Récupérer les données météo pour la ville de l'utilisateur
        weather_service = OpenWeatherMapService()
        weather_data = weather_service.get_current_weather(user_profile.ville)
        
        # Récupérer les prévisions pour les prochains jours
        forecast_data = weather_service.get_forecast(user_profile.ville, days=5)
    
    context = {
        'weather_data': weather_data,
        'forecast_data': forecast_data if 'forecast_data' in locals() else None
    }
    
    return render(request, 'weather/profile.html', context)

def weather_detail(request, city):
    """
    Vue détaillée pour une ville spécifique
    """
    weather_service = OpenWeatherMapService()
    
    # Récupérer les données météo actuelles
    current_weather = weather_service.get_current_weather(city)
    
    # Récupérer les prévisions pour les 5 prochains jours
    forecast = weather_service.get_forecast(city, days=5)
    
    # Si des coordonnées sont disponibles, récupérer les alertes
    alerts = []
    if current_weather and 'coordinates' in current_weather:
        lat = current_weather['coordinates']['lat']
        lon = current_weather['coordinates']['lon']
        alerts = weather_service.get_weather_alerts(lat, lon)
    
    context = {
        'city': city,
        'current_weather': current_weather,
        'forecast': forecast,
        'alerts': alerts
    }
    
    return render(request, 'weather/weather_detail.html', context)