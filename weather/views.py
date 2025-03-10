from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import Alert, CustomUser, TypeAlert
from .services.weather_api import OpenWeatherMapService, MAIN_FRENCH_CITIES

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
    alerts = Alert.objects.filter(active=1).order_by('-date_alert')[:5]
    
    context = {
        'cities_weather': cities_weather,
        'alerts': alerts
    }
    
    return render(request, 'weather/home.html', context)

@login_required
def profile(request):
    # Récupérer l'utilisateur personnalisé correspondant à l'utilisateur Django
    custom_user = None
    try:
        custom_user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        pass
    
    weather_data = None
    if custom_user and custom_user.city:
        # Récupérer les données météo pour la ville de l'utilisateur
        weather_service = OpenWeatherMapService()
        weather_data = weather_service.get_current_weather(custom_user.city)
        
        # Récupérer les prévisions pour les prochains jours
        forecast_data = weather_service.get_forecast(custom_user.city, days=5)
    
    context = {
        'custom_user': custom_user,
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
    api_alerts = []
    if current_weather and 'coordinates' in current_weather:
        lat = current_weather['coordinates']['lat']
        lon = current_weather['coordinates']['lon']
        api_alerts = weather_service.get_weather_alerts(lat, lon)
    
    # Récupérer également les alertes de la base de données pour cette région
    db_alerts = []
    if current_weather and 'country' in current_weather:
        # Rechercher des alertes pour la région correspondant à la ville
        db_alerts = Alert.objects.filter(
            region__icontains=city,
            active=1
        ).order_by('-date_alert')
    
    context = {
        'city': city,
        'current_weather': current_weather,
        'forecast': forecast,
        'api_alerts': api_alerts,
        'db_alerts': db_alerts
    }
    
    return render(request, 'weather/weather_detail.html', context)

# HTMX Views
def htmx_example(request):
    """
    Vue d'exemple pour HTMX
    """
    return render(request, 'weather/htmx_example.html')

def api_weather(request, city):
    """
    API endpoint pour récupérer les données météo actuelles d'une ville
    """
    weather_service = OpenWeatherMapService()
    weather_data = weather_service.get_current_weather(city)
    
    if request.headers.get('HX-Request'):
        # Si c'est une requête HTMX, retourner un fragment HTML
        if weather_data:
            return render(request, 'weather/partials/weather_card.html', {'weather': weather_data})
        else:
            return HttpResponse('<div class="alert alert-error">Ville non trouvée</div>')
    else:
        # Sinon, retourner du JSON
        if weather_data:
            return JsonResponse(weather_data)
        else:
            return JsonResponse({'error': 'Ville non trouvée'}, status=404)

def api_forecast(request, city):
    """
    API endpoint pour récupérer les prévisions météo d'une ville
    """
    weather_service = OpenWeatherMapService()
    forecast_data = weather_service.get_forecast(city, days=5)
    
    if request.headers.get('HX-Request'):
        # Si c'est une requête HTMX, retourner un fragment HTML
        if forecast_data:
            return render(request, 'weather/partials/forecast_table.html', {'forecast': forecast_data})
        else:
            return HttpResponse('<div class="alert alert-error">Prévisions non disponibles</div>')
    else:
        # Sinon, retourner du JSON
        if forecast_data:
            return JsonResponse({'forecast': forecast_data})
        else:
            return JsonResponse({'error': 'Prévisions non disponibles'}, status=404)

def alerts(request):
    """
    Vue pour afficher les alertes météo en France des 10 derniers jours
    """
    from datetime import datetime, timedelta
    
    # Initialiser le service météo
    weather_service = OpenWeatherMapService()
    
    # Récupérer les alertes de la base de données des 10 derniers jours
    ten_days_ago = datetime.now().date() - timedelta(days=10)
    alerts_from_db = Alert.objects.filter(active=1, date_alert__gte=ten_days_ago).order_by('-date_alert')
    
    # Si des alertes existent dans la base de données, les utiliser
    if alerts_from_db.exists():
        alerts_list = alerts_from_db
    else:
        # Sinon, récupérer les alertes depuis l'API pour les principales villes françaises
        alerts_list = []
        
        for city in MAIN_FRENCH_CITIES:
            city_alerts = weather_service.get_weather_alerts(city['lat'], city['lon'])
            
            if city_alerts:
                for alert in city_alerts:
                    # Créer un type d'alerte s'il n'existe pas déjà
                    alert_type, created = TypeAlert.objects.get_or_create(
                        label=alert.get('event', 'Alerte météo')
                    )
                    
                    # Convertir le timestamp en date
                    alert_date = datetime.fromtimestamp(alert.get('start', datetime.now().timestamp())).date()
                    
                    # Vérifier si l'alerte est dans les 10 derniers jours
                    if alert_date >= ten_days_ago:
                        # Créer l'alerte dans la base de données
                        new_alert = Alert.objects.create(
                            fk_type=alert_type,
                            region=city['name'],
                            description=alert.get('description', '')[:255],
                            active=1,
                            date_alert=alert_date
                        )
                        
                        alerts_list.append(new_alert)
        
        # Si aucune alerte n'a été trouvée via l'API, utiliser les données de prévision
        if not alerts_list:
            for city in MAIN_FRENCH_CITIES:
                forecast = weather_service.get_forecast(city['name'])
                
                if forecast:
                    # Analyser les prévisions pour détecter des conditions météo extrêmes
                    for day in forecast:
                        # Exemple: Fortes pluies (plus de 5mm)
                        if day.get('rain', 0) > 5:
                            alert_type, _ = TypeAlert.objects.get_or_create(label="Fortes pluies")
                            new_alert = Alert.objects.create(
                                fk_type=alert_type,
                                region=city['name'],
                                description=f"Fortes précipitations prévues avec {day.get('rain')}mm de pluie.",
                                active=1,
                                date_alert=day.get('datetime').date()
                            )
                            alerts_list.append(new_alert)
                        
                        # Exemple: Vents forts (plus de 10 m/s)
                        if day.get('wind_speed', 0) > 10:
                            alert_type, _ = TypeAlert.objects.get_or_create(label="Vents forts")
                            new_alert = Alert.objects.create(
                                fk_type=alert_type,
                                region=city['name'],
                                description=f"Vents forts prévus avec des vitesses atteignant {day.get('wind_speed')}m/s.",
                                active=1,
                                date_alert=day.get('datetime').date()
                            )
                            alerts_list.append(new_alert)
                        
                        # Exemple: Températures élevées (plus de 30°C)
                        if day.get('temperature', 0) > 30:
                            alert_type, _ = TypeAlert.objects.get_or_create(label="Canicule")
                            new_alert = Alert.objects.create(
                                fk_type=alert_type,
                                region=city['name'],
                                description=f"Températures élevées prévues avec {day.get('temperature')}°C.",
                                active=1,
                                date_alert=day.get('datetime').date()
                            )
                            alerts_list.append(new_alert)
                        
                        # Exemple: Températures basses (moins de 0°C)
                        if day.get('temperature', 20) < 0:
                            alert_type, _ = TypeAlert.objects.get_or_create(label="Gel")
                            new_alert = Alert.objects.create(
                                fk_type=alert_type,
                                region=city['name'],
                                description=f"Températures négatives prévues avec {day.get('temperature')}°C.",
                                active=1,
                                date_alert=day.get('datetime').date()
                            )
                            alerts_list.append(new_alert)
    
    context = {
        'alerts': alerts_list
    }
    
    return render(request, 'weather/alerts.html', context)