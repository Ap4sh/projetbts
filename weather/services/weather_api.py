import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Liste des principales villes françaises
MAIN_FRENCH_CITIES = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", 
    "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
    "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon",
    "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne"
]

class OpenWeatherMapService:
    """
    Service pour interagir avec l'API OpenWeatherMap
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"
    
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
            'lang': lang
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_forecast(data, days)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des prévisions pour {city}: {str(e)}")
            return None
    
    def search_cities(self, query, limit=5, country_code="FR"):
        """
        Recherche des villes par nom
        
        Args:
            query (str): Nom ou partie du nom de la ville à rechercher
            limit (int): Nombre maximum de résultats à retourner
            country_code (str): Code du pays (par défaut "FR" pour la France)
            
        Returns:
            list: Liste des villes trouvées avec leurs données météo
        """
        if not query or len(query.strip()) < 2:
            return []
        
        # Utiliser l'API Geocoding pour trouver les villes correspondantes
        endpoint = f"{self.GEO_URL}/direct"
        params = {
            'q': query,
            'limit': limit,
            'appid': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            cities_data = response.json()
            
            # Filtrer les résultats pour ne garder que les villes françaises si spécifié
            if country_code:
                cities_data = [city for city in cities_data if city.get('country') == country_code]
            
            # Récupérer les données météo pour chaque ville trouvée
            cities_with_weather = []
            for city_data in cities_data:
                city_name = city_data.get('name')
                if not city_name:
                    continue
                    
                weather_data = self.get_current_weather(city_name, country_code)
                
                if weather_data:
                    cities_with_weather.append(weather_data)
            
            return cities_with_weather
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la recherche de villes pour '{query}': {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la recherche de villes pour '{query}': {str(e)}")
            return []
    
    def get_weather_alerts(self, lat, lon, units="metric", lang="fr"):
        """
        Génère des alertes météo basées sur les données de prévision d'OpenWeather
        
        Note: L'API OneCall 3.0 qui fournit les alertes nécessite un abonnement payant.
        Cette méthode utilise les données de prévision pour générer des alertes basées
        sur les conditions météo réelles prévues par OpenWeather.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str): Unités de mesure (metric, imperial, standard)
            lang (str): Langue des données (fr, en, etc.)
            
        Returns:
            list: Liste des alertes météo générées ou liste vide s'il n'y a pas d'alertes
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
            
            # Générer des alertes basées sur les conditions météo
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
            list: Liste des alertes météo générées
        """
        if not forecast_data or 'list' not in forecast_data:
            return []
        
        alerts = []
        city_name = forecast_data.get('city', {}).get('name', 'Inconnue')
        
        # Définir les seuils pour les conditions extrêmes (basés sur les standards météorologiques)
        thresholds = {
            'rain_heavy': 7.5,     # mm de pluie en 3h (>7.5mm = fortes pluies)
            'rain_very_heavy': 15.0, # mm de pluie en 3h (>15mm = très fortes pluies)
            'snow_heavy': 5.0,     # mm de neige en 3h
            'wind_strong': 10.8,   # m/s (environ 39 km/h) - Force 6 sur échelle Beaufort
            'wind_gale': 17.2,     # m/s (environ 62 km/h) - Force 8 sur échelle Beaufort
            'temp_very_hot': 32.0, # °C - Seuil d'alerte canicule
            'temp_hot': 28.0,      # °C - Forte chaleur
            'temp_cold': 0.0,      # °C - Gel
            'temp_very_cold': -5.0 # °C - Grand froid
        }
        
        # Codes météo importants pour les alertes
        weather_alerts = {
            # Orages
            'thunderstorm': list(range(200, 300)),
            # Pluie
            'rain': list(range(300, 600)),
            # Neige
            'snow': list(range(600, 700)),
            # Brouillard
            'fog': [741],
            # Tempête
            'squall': [771],
            'tornado': [781]
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
            
            alert_added = False
            
            # Vérifier les conditions extrêmes par ordre de priorité
            
            # 1. Phénomènes dangereux (tornades, orages violents)
            if weather_id == 781:  # Tornade
                alerts.append(self._create_alert_object(
                    'Tornade', 
                    f"Risque de tornade prévu à {city_name}. Phénomène dangereux et rare en France. Mettez-vous à l'abri.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif weather_id == 771:  # Tempête
                alerts.append(self._create_alert_object(
                    'Tempête violente', 
                    f"Tempête violente prévue à {city_name}. Rafales destructrices possibles.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif weather_id in weather_alerts['thunderstorm'] and weather_id < 210:  # Orages violents
                alerts.append(self._create_alert_object(
                    'Orages violents', 
                    f"Orages violents prévus à {city_name}. {weather_desc.capitalize()}.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
                
            # 2. Précipitations extrêmes
            elif rain > thresholds['rain_very_heavy'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Pluies diluviennes', 
                    f"Précipitations exceptionnelles prévues à {city_name} avec {rain:.1f}mm de pluie en 3h. Risque d'inondation.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif rain > thresholds['rain_heavy'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Fortes pluies', 
                    f"Fortes précipitations prévues à {city_name} avec {rain:.1f}mm de pluie en 3h.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif snow > thresholds['snow_heavy'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Chutes de neige importantes', 
                    f"Chutes de neige importantes prévues à {city_name} avec {snow:.1f}mm en 3h. Conditions de circulation difficiles.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
                
            # 3. Vents forts
            elif wind_speed > thresholds['wind_gale'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Vents violents', 
                    f"Vents violents prévus à {city_name} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h). Risque de dégâts.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif wind_speed > thresholds['wind_strong'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Vents forts', 
                    f"Vents forts prévus à {city_name} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h).",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
                
            # 4. Températures extrêmes
            elif temp > thresholds['temp_very_hot'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Canicule', 
                    f"Canicule prévue à {city_name} avec {temp:.1f}°C. Protégez-vous de la chaleur.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif temp > thresholds['temp_hot'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Forte chaleur', 
                    f"Températures élevées prévues à {city_name} avec {temp:.1f}°C.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif temp < thresholds['temp_very_cold'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Grand froid', 
                    f"Températures très basses prévues à {city_name} avec {temp:.1f}°C. Risque de gel important.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
            elif temp < thresholds['temp_cold'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Gel', 
                    f"Températures négatives prévues à {city_name} avec {temp:.1f}°C. Risque de verglas.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
                
            # 5. Autres phénomènes notables
            elif weather_id in weather_alerts['fog'] and not alert_added:
                alerts.append(self._create_alert_object(
                    'Brouillard', 
                    f"Brouillard dense prévu à {city_name}. Visibilité réduite, prudence sur les routes.",
                    dt, dt + timedelta(hours=3)
                ))
                alert_added = True
        
        # Supprimer les doublons et regrouper les alertes similaires
        unique_alerts = []
        event_types = {}
        
        for alert in alerts:
            event = alert['event']
            if event in event_types:
                # Si une alerte du même type existe déjà, ne garder que la plus sévère
                existing_alert = event_types[event]
                existing_desc = existing_alert['description']
                new_desc = alert['description']
                
                # Comparer les descriptions pour déterminer la plus sévère
                if "exceptionnelles" in new_desc or "diluviennes" in new_desc or "violents" in new_desc:
                    event_types[event] = alert
            else:
                event_types[event] = alert
        
        # Convertir le dictionnaire en liste
        unique_alerts = list(event_types.values())
        
        # Limiter à 5 types d'alertes différentes
        if len(unique_alerts) > 5:
            unique_alerts = unique_alerts[:5]
        
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
    
    def _format_forecast(self, data, days):
        """
        Formate les données de prévision météo
        
        Args:
            data (dict): Données brutes de l'API
            days (int): Nombre de jours de prévision
            
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
        
        # Limiter à 5 jours de prévision
        if len(forecasts) > days * 8:
            forecasts = forecasts[:days * 8]
        
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

class MeteoFranceVigilanceService:
    """Service pour récupérer les données de vigilance météo de Météo France"""
    
    BASE_URL = "https://public-api.meteofrance.fr/public/DPVigilance/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'accept': '*/*',
            'apikey': api_key
        }
    
    def get_vigilance_texts(self):
        """Récupère les bulletins de vigilance textuel"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/textesvigilance/encours",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des textes de vigilance: {str(e)}")
            return None
            
    def get_vigilance_map(self):
        """Récupère la carte de vigilance avec les prévisions de risque"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/cartevigilance/encours",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération de la carte de vigilance: {str(e)}")
            return None
            
    def get_vigilance_alerts(self):
        """
        Récupère et formate les alertes de vigilance actuelles
        
        Returns:
            list: Liste des alertes formatées avec:
                - type_label: Type d'alerte
                - region: Région/Département concerné
                - description: Description de l'alerte
                - severity: Niveau de sévérité (yellow, orange, red)
                - date_alert: Date de l'alerte
        """
        texts = self.get_vigilance_texts()
        if not texts:
            return []
            
        alerts = []
        
        # Parcourir les blocs de texte pour extraire les alertes
        for bloc in texts.get('product', {}).get('text_bloc_items', []):
            if bloc.get('bloc_items'):
                for item in bloc['bloc_items']:
                    if item.get('text_items'):
                        for text_item in item['text_items']:
                            for term_item in text_item.get('term_items', []):
                                # Extraire les informations d'alerte
                                alert = {
                                    'type_label': text_item.get('hazard_name', 'Alerte météo'),
                                    'region': bloc.get('domain_name', 'France'),
                                    'description': '',
                                    'severity': term_item.get('risk_color', '#f9ff00'),
                                    'date_alert': term_item.get('start_time'),
                                    'severity_display': term_item.get('risk_name', 'Jaune')
                                }
                                
                                # Construire la description à partir des subdivisions de texte
                                description_parts = []
                                for subdivision in term_item.get('subdivision_text', []):
                                    if subdivision.get('text'):
                                        description_parts.extend(subdivision['text'])
                                alert['description'] = ' '.join(description_parts)
                                
                                if alert['description']:  # Ne garder que les alertes avec une description
                                    alerts.append(alert)
        
        return alerts 