from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from .models import Alert, CustomUser, TypeAlert
from .services.weather_api import OpenWeatherMapService, MAIN_FRENCH_CITIES, MeteoFranceVigilanceService
from datetime import datetime, timedelta
from django.db.models import Q

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
    
    # Récupérer les alertes météo actives
    alerts = get_formatted_alerts()
    
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
    forecast_data = None
    if custom_user and custom_user.city:
        # Récupérer les données météo pour la ville de l'utilisateur
        weather_service = OpenWeatherMapService()
        weather_data = weather_service.get_current_weather(custom_user.city)
        
        # Récupérer les prévisions pour les prochains jours
        forecast_data = weather_service.get_forecast(custom_user.city, days=5)
    
    context = {
        'custom_user': custom_user,
        'weather_data': weather_data,
        'forecast_data': forecast_data
    }
    
    return render(request, 'weather/profile.html', context)

def login_view(request):
    return render(request, 'login.html')

def register(request):
    pass




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
    
    if not query or len(query) < 2:
        return render(request, 'weather/partials/search_results.html', {'query': query})
    
    # Initialiser le service météo
    weather_service = OpenWeatherMapService()
    
    # Rechercher les villes correspondant à la requête
    cities = weather_service.search_cities(query)
    
    # Filtrer les résultats pour ne garder que ceux avec un nom valide
    cities = [city for city in cities if city and 'name' in city and city['name']]
    
    # Limiter le nombre de résultats pour des raisons de performance
    cities = cities[:5]
    
    # Ajouter un message si aucune ville n'est trouvée
    no_results = len(cities) == 0
    
    context = {
        'query': query,
        'cities': cities,
        'no_results': no_results
    }
    
    return render(request, 'weather/partials/search_results.html', context)

def filter_alerts(request):
    """
    Vue pour filtrer les alertes par type
    """
    alert_type = request.GET.get('type', None)
    
    # Récupérer les alertes filtrées
    alerts = get_formatted_alerts(alert_type)
    
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
def get_formatted_alerts(alert_type=None):
    """
    Récupère et formate les alertes météo depuis l'API Météo France Vigilance
    et la base de données locale
    
    Args:
        alert_type (str, optional): Type d'alerte à filtrer. Defaults to None.
        
    Returns:
        list: Liste des alertes formatées
    """
    from datetime import datetime, timedelta
    from weather.services.weather_api import MeteoFranceVigilanceService
    
    # Définir la période : 1 semaine dans le passé et 2 semaines dans le futur
    one_week_ago = datetime.now().date() - timedelta(days=7)
    two_weeks_ahead = datetime.now().date() + timedelta(days=14)
    
    # Récupérer les alertes de la base de données
    alerts_query = Alert.objects.filter(
        active=1, 
        date_alert__gte=one_week_ago,
        date_alert__lte=two_weeks_ahead
    )
    
    # Mapping des types d'alertes pour le filtrage
    type_mapping = {
        'rain': ['pluie', 'précipitation', 'averse'],
        'wind': ['vent', 'rafale', 'tempête'],
        'storm': ['orage', 'foudre', 'éclair'],
        'snow': ['neige', 'verglas', 'gel'],
        'heat': ['canicule', 'chaleur', 'température élevée'],
        'flood': ['inondation', 'crue', 'montée des eaux'],
    }
    
    # Filtrer par type si spécifié
    if alert_type and alert_type in type_mapping:
        # Créer une requête OR pour tous les termes associés au type
        query = Q()
        for term in type_mapping[alert_type]:
            query |= Q(fk_type__label__icontains=term) | Q(description__icontains=term)
        
        alerts_query = alerts_query.filter(query)
    elif alert_type:
        # Si le type n'est pas dans le mapping mais est spécifié, rechercher directement
        alerts_query = alerts_query.filter(
            Q(fk_type__label__icontains=alert_type) | 
            Q(description__icontains=alert_type)
        )
    
    # Trier par date (plus récentes en premier)
    alerts_query = alerts_query.order_by('-date_alert')
    
    # Formater les alertes de la base de données
    formatted_alerts = []
    for alert in alerts_query:
        # Déterminer la sévérité de l'alerte
        severity = "yellow"  # Par défaut
        severity_terms = {
            'red': ['rouge', 'grave', 'extrême', 'danger'],
            'orange': ['orange', 'important', 'vigilance'],
            'yellow': ['jaune', 'modéré', 'attention']
        }
        
        # Vérifier les termes dans le label et la description
        label_lower = alert.fk_type.label.lower()
        desc_lower = alert.description.lower()
        
        for sev, terms in severity_terms.items():
            if any(term in label_lower or term in desc_lower for term in terms):
                severity = sev
                break
        
        # Déterminer le type d'alerte pour l'affichage
        alert_type_display = alert.fk_type.label
        
        # Formater l'alerte
        formatted_alerts.append({
            'id': alert.id,
            'type_label': alert_type_display,
            'region': alert.region,
            'description': alert.description,
            'date_alert': alert.date_alert,
            'severity': severity,
            'severity_display': {
                'red': 'Rouge',
                'orange': 'Orange',
                'yellow': 'Jaune'
            }.get(severity, 'Jaune')
        })
    
    # Récupérer les alertes de l'API Météo France Vigilance
    api_key = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzYW15dnZzQGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoic2FteXZ2cyIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjI1Mzc2LCJ1dWlkIjoiMDUyMjEwOGItNzhmMi00NzY4LTk2YTEtZmMyZDJjMTE5NTU4In0sImlzcyI6Imh0dHBzOlwvXC9wb3J0YWlsLWFwaS5tZXRlb2ZyYW5jZS5mcjo0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyI2MFJlcVBhck1pbiI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNWaWdpbGFuY2UiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQVmlnaWxhbmNlXC92MSIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjYwUmVxUGFyTWluIn1dLCJleHAiOjE4MzYzNTc4NjMsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3NDE2ODUwNjMsImp0aSI6IjQ5YTAzMTJmLTUyNjctNDRmNC1iNGYxLWI5YTFlZjY4N2Y4ZiJ9.i5QWxDyyQXgN8JbqYGDpDxdZXVld4mBoFtfVGfKquyboPp02lpT7huL6DJmh0Y4yMr6UmRVBTTB5rd1McC_oxBbk-uEBiLxXggMh23OkhtjjUzxbYkiktWWiVf5WTHPYvRHcXLxyxcd6freSL2XvTCIFyc41dTJK0a5YpZzlGfw6-UIQgxFHgx7vXBZmDkmthw1TrdFZRDWWyIs8Zyy6aEubdmHaJPI4s7G3l0mrQE4KyAsqwSrnCxWwVTWMD-XCbtcUdVYe6Ey3Vkr-3t3lUCH0zsAXOvfBvKP1n53pMzVOU-A5N33dSiCtq-xJ4vd9su1vchGDK1MO40CVWx_E8w=="
    vigilance_service = MeteoFranceVigilanceService(api_key)
    api_alerts = vigilance_service.get_vigilance_alerts()
    
    # Filtrer les alertes de l'API si un type est spécifié
    if alert_type and api_alerts:
        filtered_api_alerts = []
        for alert in api_alerts:
            alert_text = (alert.get('type_label', '') + ' ' + alert.get('description', '')).lower()
            if alert_type in type_mapping:
                if any(term in alert_text for term in type_mapping[alert_type]):
                    filtered_api_alerts.append(alert)
            elif alert_type.lower() in alert_text:
                filtered_api_alerts.append(alert)
        api_alerts = filtered_api_alerts
    
    # Combiner les alertes de la base de données et de l'API
    all_alerts = formatted_alerts + api_alerts
    
    # Si aucune alerte n'est trouvée, ajouter des alertes de test pour le développement
    if not all_alerts:
        today = datetime.now().date()
        test_alerts = [
            {
                'id': 1,
                'type_label': 'Alerte Vent',
                'region': 'Bretagne',
                'description': 'Vents violents attendus avec des rafales jusqu\'à 100 km/h.',
                'date_alert': today,
                'severity': 'orange',
                'severity_display': 'Orange'
            },
            {
                'id': 2,
                'type_label': 'Alerte Pluie',
                'region': 'Normandie',
                'description': 'Fortes précipitations prévues, risque d\'inondation localisée.',
                'date_alert': today + timedelta(days=1),
                'severity': 'yellow',
                'severity_display': 'Jaune'
            },
            {
                'id': 3,
                'type_label': 'Alerte Canicule',
                'region': 'Provence-Alpes-Côte d\'Azur',
                'description': 'Températures élevées dépassant les 35°C pendant plusieurs jours.',
                'date_alert': today + timedelta(days=2),
                'severity': 'red',
                'severity_display': 'Rouge'
            }
        ]
        
        # Si un type d'alerte est spécifié, ne retourner que les alertes de test correspondantes
        if alert_type:
            if alert_type == 'wind':
                all_alerts = [test_alerts[0]]
            elif alert_type == 'rain':
                all_alerts = [test_alerts[1]]
            elif alert_type == 'heat':
                all_alerts = [test_alerts[2]]
            else:
                all_alerts = []
        else:
            all_alerts = test_alerts
    
    return all_alerts