from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from .models import Alert, CustomUser, TypeAlert, Cities
from .services.weather_api import OpenWeatherMapService, MAIN_FRENCH_CITIES, MeteoFranceVigilanceService
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import logging
from django.conf import settings
from django.contrib import messages


logger = logging.getLogger(__name__)

def home(request):
    # Initialiser le service météo
    weather_service = OpenWeatherMapService()
    
    # Liste des principales villes françaises avec leurs positions sur la carte
    cities = [
        {"name": "Paris", "map_position": {"top": 41.7, "left": 50}},
        {"name": "Marseille", "map_position": {"top": 70, "left": 58.3}},
        {"name": "Lyon", "map_position": {"top": 58.3, "left": 55}},
        {"name": "Toulouse", "map_position": {"top": 66.7, "left": 41.7}},
        {"name": "Nice", "map_position": {"top": 66.7, "left": 66.7}},
        {"name": "Nantes", "map_position": {"top": 50, "left": 33.3}},
        {"name": "Strasbourg", "map_position": {"top": 33.3, "left": 66.7}},
        {"name": "Montpellier", "map_position": {"top": 70, "left": 50}},
        {"name": "Bordeaux", "map_position": {"top": 58.3, "left": 36.7}},
        {"name": "Lille", "map_position": {"top": 25, "left": 50}}
    ]
    
    # Récupérer les données météo pour chaque ville
    cities_weather = []
    for city in cities:
        weather_data = weather_service.get_current_weather(city["name"])
        if weather_data:
            # Fusionner les données météo avec les positions sur la carte
            weather_data.update(city)
            cities_weather.append(weather_data)
    
    # Récupérer les alertes météo actives (limitées à 6 et seulement orange/rouge)
    alerts = get_formatted_alerts(limit=6, only_severe=True)
    
    context = {
        'cities_weather': cities_weather,
        'alerts': alerts
    }
    
    return render(request, 'weather/home.html', context)

@login_required
def profile(request):
    weather_data = None
    forecast_data = None
    
    if request.user.city:
        # Récupérer les données météo pour la ville de l'utilisateur
        weather_service = OpenWeatherMapService()
        weather_data = weather_service.get_current_weather(request.user.city.label)
        
        # Récupérer les prévisions pour les prochains jours
        forecast_data = weather_service.get_forecast(request.user.city.label, days=5)
    
    context = {
        'weather_data': weather_data,
        'forecast_data': forecast_data
    }
    
    return render(request, 'weather/profile.html', context)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'weather:profile')
            return redirect(next_url)
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    return render(request, 'weather/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('weather:home')

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        city_name = request.POST.get("city")
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Un compte utilisateur est déjà associé à cette adresse mail.")
            return render(request, 'weather/register.html')
        
        try:
            # Recherche insensible à la casse
            city = Cities.objects.filter(label__iexact=city_name).first()
            if not city and city_name:
                # Recherche partielle si pas de correspondance exacte
                city = Cities.objects.filter(label__icontains=city_name).first()
            
            if not city:
                # Si aucune ville n'est trouvée, utilisez Paris comme valeur par défaut
                city = Cities.objects.filter(label__iexact='Paris').first()
                if not city:
                    # Au cas où Paris n'existerait pas dans la base de données
                    city = Cities.objects.first()
                messages.warning(request, f"La ville spécifiée n'a pas été trouvée. Nous avons utilisé {city.label} comme ville par défaut.")
            
            user = CustomUser.objects.create_user(email=email, password=password, city=city)
            login(request, user)
            return redirect('weather:profile')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte: {str(e)}")
            return render(request, 'weather/register.html')
            
    return render(request, 'weather/register.html')




def weather_detail(request, city):
    """
    Vue détaillée pour une ville spécifique
    """
    weather_service = OpenWeatherMapService()
    
    # Récupérer les données météo actuelles
    current_weather = weather_service.get_current_weather(city)
    
    # Si la ville n'est pas trouvée, afficher une page 404 personnalisée
    if not current_weather:
        return render(request, 'weather/404.html', status=404)
    
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

def search_city(request):
    """
    Vue pour rechercher une ville et afficher les résultats
    """
    query = request.GET.get('query', '').strip()
    logger.info(f"Recherche de ville avec la requête: '{query}'")
    
    if not query or len(query) < 2:
        logger.warning(f"Requête de recherche trop courte ou vide: '{query}'")
        return render(request, 'weather/partials/search_results.html', {'query': query})
    
    # Initialiser le service météo
    weather_service = OpenWeatherMapService()
    
    try:
        # Rechercher les villes correspondant à la requête
        cities = weather_service.search_cities(query)
        logger.info(f"Nombre de villes trouvées: {len(cities)}")
        
        # Filtrer les résultats pour ne garder que ceux avec un nom valide
        cities = [city for city in cities if city and isinstance(city, dict) and 'name' in city and city['name']]
        logger.info(f"Nombre de villes après filtrage: {len(cities)}")
        
        # Créer un ensemble pour suivre les noms de villes déjà inclus
        city_names = set()
        unique_cities = []
        
        for city in cities:
            city_name = city.get('name')
            if city_name and city_name not in city_names:
                city_names.add(city_name)
                unique_cities.append(city)
        
        cities = unique_cities
        logger.info(f"Nombre de villes après dédoublonnage: {len(cities)}")
        
        # Limiter le nombre de résultats pour des raisons de performance
        cities = cities[:5]
        
        context = {
            'cities': cities,
            'query': query
        }
        
        return render(request, 'weather/partials/search_results.html', context)
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de villes: {str(e)}")
        return render(request, 'weather/partials/search_results.html', {'query': query, 'error': str(e)})

def filter_alerts(request):
    """
    Vue pour filtrer les alertes par type et région
    """
    alert_type = request.GET.get('type', None)
    region = request.GET.get('region', None)
    
    # Récupérer les alertes filtrées
    alerts = get_formatted_alerts(alert_type=alert_type, region=region)
    
    return render(request, 'weather/partials/alert_feed.html', {'alerts': alerts})

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
    Vue pour afficher les alertes météo en France
    """
    # Récupérer le type d'alerte à filtrer
    alert_type = request.GET.get('type', None)
    
    # Récupérer les alertes filtrées
    alerts_list = get_formatted_alerts(alert_type)
    
    context = {
        'alerts': alerts_list
    }
    
    return render(request, 'weather/alerts.html', context)

def api_alerts(request):
    """
    API pour récupérer les alertes météo en France des 2 prochaines semaines et de la semaine dernière
    """
    # Définir la période : 1 semaine dans le passé et 2 semaines dans le futur
    one_week_ago = datetime.now().date() - timedelta(days=7)
    two_weeks_ahead = datetime.now().date() + timedelta(days=14)
    
    # Récupérer les alertes existantes dans la base de données pour cette période
    alerts_from_db = Alert.objects.filter(
        active=1, 
        date_alert__gte=one_week_ago,
        date_alert__lte=two_weeks_ahead
    ).order_by('-date_alert')
    
    # Préparer la liste des alertes à retourner
    alerts_data = []
    
    # Ajouter les alertes de la base de données
    for alert in alerts_from_db:
        alerts_data.append({
            'type': alert.fk_type.label,
            'region': alert.region,
            'description': alert.description,
            'date': alert.date_alert.strftime('%Y-%m-%d'),
            'source': 'database'
        })
    
    # Retourner les alertes au format JSON
    return JsonResponse({
        'period': {
            'start': one_week_ago.strftime('%Y-%m-%d'),
            'end': two_weeks_ahead.strftime('%Y-%m-%d')
        },
        'count': len(alerts_data),
        'alerts': alerts_data
    })

# Fonctions utilitaires
def get_formatted_alerts(alert_type=None, region=None, limit=None, only_severe=False):
    """
    Récupère les alertes formatées depuis l'API Météo France Vigilance
    
    Args:
        alert_type (str, optional): Type d'alerte à filtrer
        region (str, optional): Code du département à filtrer (ex: "75" pour Paris)
        limit (int, optional): Nombre maximum d'alertes à retourner
        only_severe (bool, optional): Si True, ne retourne que les alertes orange et rouge
        
    Returns:
        list: Liste des alertes formatées
    """
    try:
        # Récupérer les alertes de Météo France
        meteo_france_service = MeteoFranceVigilanceService(settings.METEO_FRANCE_API_KEY)
        alerts = meteo_france_service.get_vigilance_alerts()
        
        if not alerts:
            return []

        # Mapping des types d'alertes avec leurs mots-clés associés
        type_mapping = {
            'rain': ['pluie-inondation', 'pluie', 'inondation', 'précipitations'],
            'wind': ['vent', 'vent violent'],
            'storm': ['orage', 'orages'],
            'snow': ['neige', 'neige-verglas', 'verglas'],
            'heat': ['canicule', 'chaleur'],
            'flood': ['crue', 'inondation', 'submersion']
        }
        
        # Filtrer par type d'alerte si spécifié
        if alert_type and alert_type in type_mapping:
            keywords = type_mapping[alert_type]
            filtered_alerts = []
            for alert in alerts:
                alert_type_lower = alert['type_label'].lower()
                if any(keyword in alert_type_lower for keyword in keywords):
                    filtered_alerts.append(alert)
            alerts = filtered_alerts

        # Filtrer par département si spécifié
        if region:
            filtered_alerts = []
            for alert in alerts:
                # Extraire le code du département entre parenthèses
                if f"({region})" in alert['region']:
                    filtered_alerts.append(alert)
            alerts = filtered_alerts
        
        # Filtrer pour ne garder que les alertes graves si demandé
        if only_severe:
            alerts = [
                alert for alert in alerts
                if alert['severity'] in ['orange', 'red']
            ]
        
        # Trier les alertes par sévérité puis par date
        severity_order = {'red': 1, 'orange': 2, 'yellow': 3, 'green': 4}
        alerts.sort(key=lambda x: (
            severity_order.get(x['severity'], 4),
            x['date_alert'].timestamp() if isinstance(x['date_alert'], datetime) else 0
        ))
        
        # Appliquer la limite si spécifiée
        if limit:
            alerts = alerts[:limit]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes: {str(e)}")
        return []