import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class OpenWeatherMapService:
    """
    Service pour interagir avec l'API OpenWeatherMap
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        # Récupérer la clé API depuis les variables d'environnement ou settings
        self.api_key = os.environ.get('OPENWEATHER_API_KEY', 'a6b2d8524308570bedd6e593c1f5a8b6')
    
    def get_current_weather(self, city, country_code="FR", units="metric", lang="fr"):
        """
        Récupère les données météo actuelles pour une ville
        
        Args:
            city (str): Nom de la ville
            country_code (str): Code du pays (par défaut "FR" pour la France)
            units (str): Unités de mesure (metric, imperial, standard)
            lang (str): Langue des données (fr, en, etc.)
            
        Returns:
            dict: Données météo formatées ou None en cas d'erreur
        """
        endpoint = f"{self.BASE_URL}/weather"
        params = {
            'q': f"{city},{country_code}",
            'appid': self.api_key,
            'units': units,
            'lang': lang
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Lève une exception si la requête a échoué
            
            data = response.json()
            return self._format_current_weather(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données météo pour {city}: {str(e)}")
            return None
    
    def get_weather_by_coordinates(self, lat, lon, units="metric", lang="fr"):
        """
        Récupère les données météo actuelles par coordonnées géographiques
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str): Unités de mesure (metric, imperial, standard)
            lang (str): Langue des données (fr, en, etc.)
            
        Returns:
            dict: Données météo formatées ou None en cas d'erreur
        """
        endpoint = f"{self.BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': units,
            'lang': lang
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_current_weather(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données météo pour lat={lat}, lon={lon}: {str(e)}")
            return None
    
    def get_forecast(self, city, country_code="FR", units="metric", lang="fr", days=5):
        """
        Récupère les prévisions météo pour une ville
        
        Args:
            city (str): Nom de la ville
            country_code (str): Code du pays (par défaut "FR" pour la France)
            units (str): Unités de mesure (metric, imperial, standard)
            lang (str): Langue des données (fr, en, etc.)
            days (int): Nombre de jours de prévision (max 5 pour l'API gratuite)
            
        Returns:
            list: Liste des prévisions météo formatées ou None en cas d'erreur
        """
        endpoint = f"{self.BASE_URL}/forecast"
        params = {
            'q': f"{city},{country_code}",
            'appid': self.api_key,
            'units': units,
            'lang': lang,
            'cnt': days * 8  # 8 prévisions par jour (toutes les 3 heures)
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_forecast(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des prévisions météo pour {city}: {str(e)}")
            return None
    
    def get_weather_alerts(self, lat, lon, units="metric", lang="fr"):
        """
        Simule les alertes météo en utilisant les API gratuites
        
        Note: L'API OneCall 3.0 qui fournit les alertes nécessite un abonnement payant.
        Cette méthode utilise les données de prévision pour générer des alertes simulées
        basées sur les conditions météo extrêmes.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str): Unités de mesure (metric, imperial, standard)
            lang (str): Langue des données (fr, en, etc.)
            
        Returns:
            list: Liste des alertes météo simulées ou liste vide s'il n'y a pas d'alertes
        """
        # Utiliser l'API de prévision gratuite au lieu de OneCall
        endpoint = f"{self.BASE_URL}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': units,
            'lang': lang,
            'cnt': 40  # Maximum de prévisions (5 jours)
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Générer des alertes basées sur les conditions météo extrêmes
            return self._generate_alerts_from_forecast(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données pour les alertes météo pour lat={lat}, lon={lon}: {str(e)}")
            return []
    
    def _generate_alerts_from_forecast(self, forecast_data):
        """
        Génère des alertes basées sur les données de prévision
        
        Args:
            forecast_data (dict): Données de prévision brutes
            
        Returns:
            list: Liste des alertes météo simulées
        """
        if not forecast_data or 'list' not in forecast_data:
            return []
        
        alerts = []
        city_name = forecast_data.get('city', {}).get('name', 'Inconnue')
        
        # Définir les seuils pour les conditions extrêmes
        thresholds = {
            'rain': 10.0,  # mm de pluie en 3h
            'snow': 5.0,   # mm de neige en 3h
            'wind': 15.0,  # m/s (environ 54 km/h)
            'temp_high': 35.0,  # °C
            'temp_low': 0.0,    # °C
        }
        
        # Parcourir les prévisions pour détecter les conditions extrêmes
        for item in forecast_data['list']:
            dt = datetime.fromtimestamp(item.get('dt', 0))
            temp = item.get('main', {}).get('temp', 20)
            wind_speed = item.get('wind', {}).get('speed', 0)
            rain = item.get('rain', {}).get('3h', 0)
            snow = item.get('snow', {}).get('3h', 0)
            weather_id = item.get('weather', [{}])[0].get('id', 800)
            weather_desc = item.get('weather', [{}])[0].get('description', '')
            
            # Vérifier les conditions extrêmes
            if rain > thresholds['rain']:
                alerts.append(self._create_alert_object(
                    'Fortes pluies', 
                    f"Fortes précipitations prévues à {city_name} avec {rain}mm de pluie en 3h.",
                    dt, dt + timedelta(hours=3)
                ))
            
            if snow > thresholds['snow']:
                alerts.append(self._create_alert_object(
                    'Chutes de neige', 
                    f"Chutes de neige importantes prévues à {city_name} avec {snow}mm en 3h.",
                    dt, dt + timedelta(hours=3)
                ))
            
            if wind_speed > thresholds['wind']:
                alerts.append(self._create_alert_object(
                    'Vents forts', 
                    f"Vents forts prévus à {city_name} avec des vitesses atteignant {wind_speed}m/s.",
                    dt, dt + timedelta(hours=3)
                ))
            
            if temp > thresholds['temp_high']:
                alerts.append(self._create_alert_object(
                    'Canicule', 
                    f"Températures élevées prévues à {city_name} avec {temp}°C.",
                    dt, dt + timedelta(hours=3)
                ))
            
            if temp < thresholds['temp_low']:
                alerts.append(self._create_alert_object(
                    'Gel', 
                    f"Températures négatives prévues à {city_name} avec {temp}°C.",
                    dt, dt + timedelta(hours=3)
                ))
            
            # Alertes basées sur les codes météo
            if weather_id < 300:  # Orages
                alerts.append(self._create_alert_object(
                    'Orages', 
                    f"Orages prévus à {city_name}: {weather_desc}.",
                    dt, dt + timedelta(hours=3)
                ))
            
        # Supprimer les doublons et limiter le nombre d'alertes
        unique_alerts = []
        event_types = set()
        
        for alert in alerts:
            if alert['event'] not in event_types:
                event_types.add(alert['event'])
                unique_alerts.append(alert)
                
                # Limiter à 3 types d'alertes différentes
                if len(unique_alerts) >= 3:
                    break
        
        return unique_alerts
    
    def _create_alert_object(self, event, description, start_time, end_time):
        """
        Crée un objet d'alerte formaté
        
        Args:
            event (str): Type d'événement
            description (str): Description de l'alerte
            start_time (datetime): Heure de début
            end_time (datetime): Heure de fin
            
        Returns:
            dict: Objet d'alerte formaté
        """
        return {
            'event': event,
            'description': description,
            'start': int(start_time.timestamp()),
            'end': int(end_time.timestamp()),
            'start_time': start_time,
            'end_time': end_time
        }
    
    def _format_current_weather(self, data):
        """
        Formate les données météo actuelles
        
        Args:
            data (dict): Données brutes de l'API
            
        Returns:
            dict: Données météo formatées
        """
        if not data:
            return None
            
        weather = {
            'city': data.get('name', ''),
            'country': data.get('sys', {}).get('country', ''),
            'temperature': data.get('main', {}).get('temp', 0),
            'feels_like': data.get('main', {}).get('feels_like', 0),
            'humidity': data.get('main', {}).get('humidity', 0),
            'pressure': data.get('main', {}).get('pressure', 0),
            'description': data.get('weather', [{}])[0].get('description', ''),
            'icon': data.get('weather', [{}])[0].get('icon', ''),
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_direction': data.get('wind', {}).get('deg', 0),
            'clouds': data.get('clouds', {}).get('all', 0),
            'timestamp': data.get('dt', 0),
            'sunrise': data.get('sys', {}).get('sunrise', 0),
            'sunset': data.get('sys', {}).get('sunset', 0),
            'coordinates': {
                'lat': data.get('coord', {}).get('lat', 0),
                'lon': data.get('coord', {}).get('lon', 0)
            }
        }
        
        # Convertir les timestamps en datetime
        weather['datetime'] = datetime.fromtimestamp(weather['timestamp'])
        weather['sunrise_time'] = datetime.fromtimestamp(weather['sunrise'])
        weather['sunset_time'] = datetime.fromtimestamp(weather['sunset'])
        
        return weather
    
    def _format_forecast(self, data):
        """
        Formate les données de prévision météo
        
        Args:
            data (dict): Données brutes de l'API
            
        Returns:
            list: Liste des prévisions météo formatées
        """
        if not data or 'list' not in data:
            return []
            
        forecasts = []
        
        for item in data['list']:
            forecast = {
                'timestamp': item.get('dt', 0),
                'datetime': datetime.fromtimestamp(item.get('dt', 0)),
                'temperature': item.get('main', {}).get('temp', 0),
                'feels_like': item.get('main', {}).get('feels_like', 0),
                'humidity': item.get('main', {}).get('humidity', 0),
                'pressure': item.get('main', {}).get('pressure', 0),
                'description': item.get('weather', [{}])[0].get('description', ''),
                'icon': item.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': item.get('wind', {}).get('speed', 0),
                'wind_direction': item.get('wind', {}).get('deg', 0),
                'clouds': item.get('clouds', {}).get('all', 0),
                'rain': item.get('rain', {}).get('3h', 0),
                'snow': item.get('snow', {}).get('3h', 0)
            }
            forecasts.append(forecast)
        
        return forecasts


# Fonction utilitaire pour obtenir une instance du service
def get_weather_service():
    """
    Retourne une instance du service OpenWeatherMap
    
    Returns:
        OpenWeatherMapService: Instance du service
    """
    return OpenWeatherMapService()

# Constantes pour les principales villes françaises
MAIN_FRENCH_CITIES = [
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
    {"name": "Lyon", "lat": 45.7578, "lon": 4.8320},
    {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442},
    {"name": "Nice", "lat": 43.7102, "lon": 7.2620},
    {"name": "Nantes", "lat": 47.2184, "lon": -1.5536},
    {"name": "Strasbourg", "lat": 48.5734, "lon": 7.7521},
    {"name": "Montpellier", "lat": 43.6108, "lon": 3.8767},
    {"name": "Bordeaux", "lat": 44.8378, "lon": -0.5792},
    {"name": "Lille", "lat": 50.6292, "lon": 3.0573},
] 