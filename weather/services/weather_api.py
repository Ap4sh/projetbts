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
            logger.warning(f"Requête de recherche trop courte ou vide: '{query}'")
            return []
        
        # Vérifier d'abord si la requête correspond à une ville française connue
        query_lower = query.lower().strip()
        logger.info(f"Recherche de ville avec la requête: '{query_lower}'")
        
        # Vérifier si la requête correspond à une ville française connue
        matching_cities = []
        for city_name in MAIN_FRENCH_CITIES:
            if isinstance(city_name, str) and (city_name.lower() == query_lower or city_name.lower().startswith(query_lower)):
                # Si c'est une ville connue, récupérer directement les données météo
                weather_data = self.get_current_weather(city_name, country_code)
                if weather_data:
                    logger.info(f"Ville trouvée dans MAIN_FRENCH_CITIES: {city_name}")
                    matching_cities.append(weather_data)
        
        if matching_cities:
            return matching_cities
        
        # Utiliser l'API Geocoding pour trouver les villes correspondantes
        endpoint = f"{self.GEO_URL}/direct"
        params = {
            'q': query,
            'limit': limit,
            'appid': self.api_key
        }
        
        try:
            logger.info(f"Recherche de villes avec l'API Geocoding: {query}")
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            cities_data = response.json()
            logger.info(f"Résultats de l'API Geocoding: {len(cities_data)} villes trouvées")
            
            # Filtrer les résultats pour ne garder que les villes françaises si spécifié
            if country_code:
                cities_data = [city for city in cities_data if city.get('country') == country_code]
                logger.info(f"Après filtrage par pays ({country_code}): {len(cities_data)} villes")
            
            # Récupérer les données météo pour chaque ville trouvée
            cities_with_weather = []
            for city_data in cities_data:
                city_name = city_data.get('name')
                if not city_name:
                    continue
                
                # Récupérer les données météo pour cette ville
                lat = city_data.get('lat')
                lon = city_data.get('lon')
                if lat is not None and lon is not None:
                    weather_data = self.get_weather_by_coordinates(lat, lon)
                    if weather_data:
                        # S'assurer que le nom de la ville est bien défini
                        weather_data['name'] = city_name
                        cities_with_weather.append(weather_data)
            
            logger.info(f"Nombre de villes avec données météo: {len(cities_with_weather)}")
            return cities_with_weather
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de villes: {str(e)}")
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
            dict: Données formatées
        """
        if not data:
            return None
            
        try:
            # Extraire les données principales
            main_data = data.get('main', {})
            weather_data = data.get('weather', [{}])[0] if data.get('weather') else {}
            wind_data = data.get('wind', {})
            sys_data = data.get('sys', {})
            
            # S'assurer que l'icône est correctement formatée
            icon = weather_data.get('icon', '01d')
            
            # Formater les données
            formatted_data = {
                'name': data.get('name', ''),
                'coordinates': {
                    'lat': data.get('coord', {}).get('lat'),
                    'lon': data.get('coord', {}).get('lon')
                },
                'main': {
                    'temp': main_data.get('temp'),
                    'feels_like': main_data.get('feels_like'),
                    'temp_min': main_data.get('temp_min'),
                    'temp_max': main_data.get('temp_max'),
                    'pressure': main_data.get('pressure'),
                    'humidity': main_data.get('humidity')
                },
                'weather': {
                    'id': weather_data.get('id'),
                    'main': weather_data.get('main'),
                    'description': weather_data.get('description', ''),
                    'icon': icon
                },
                'wind': {
                    'speed': wind_data.get('speed'),
                    'deg': wind_data.get('deg')
                },
                'visibility': data.get('visibility'),
                'sys': {
                    'country': sys_data.get('country'),
                    'sunrise': datetime.fromtimestamp(sys_data.get('sunrise', 0)) if sys_data.get('sunrise') else None,
                    'sunset': datetime.fromtimestamp(sys_data.get('sunset', 0)) if sys_data.get('sunset') else None
                },
                'dt': datetime.fromtimestamp(data.get('dt', 0)) if data.get('dt') else None
            }
            
            return formatted_data
        except Exception as e:
            logger.error(f"Erreur lors du formatage des données météo actuelles: {str(e)}")
            return None
    
    def _format_forecast(self, data, days):
        """
        Formate les données de prévision météo
        
        Args:
            data (dict): Données brutes de l'API
            days (int): Nombre de jours de prévision
            
        Returns:
            list: Liste des prévisions météo formatées par jour
        """
        if not data or 'list' not in data:
            return []
            
        forecasts = []
        
        # Récupérer toutes les prévisions
        for item in data['list']:
            try:
                timestamp = item.get('dt', 0)
                if not timestamp:
                    logger.warning("Prévision sans timestamp, ignorée")
                    continue
                
                # S'assurer que le timestamp est valide
                try:
                    dt = datetime.fromtimestamp(timestamp)
                except (ValueError, TypeError, OverflowError):
                    logger.warning(f"Timestamp invalide: {timestamp}, ignoré")
                    continue
                    
                forecast = {
                    'timestamp': timestamp,
                    'datetime': dt,
                    'temperature': item.get('main', {}).get('temp', 0),
                    'feels_like': item.get('main', {}).get('feels_like', 0),
                    'humidity': item.get('main', {}).get('humidity', 0),
                    'pressure': item.get('main', {}).get('pressure', 0),
                    'description': item.get('weather', [{}])[0].get('description', ''),
                    'icon': item.get('weather', [{}])[0].get('icon', ''),
                    'weather_id': item.get('weather', [{}])[0].get('id', 0),
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'wind_direction': item.get('wind', {}).get('deg', 0),
                    'clouds': item.get('clouds', {}).get('all', 0),
                    'rain': item.get('rain', {}).get('3h', 0),
                    'snow': item.get('snow', {}).get('3h', 0)
                }
                forecasts.append(forecast)
            except Exception as e:
                logger.error(f"Erreur lors du formatage d'une prévision: {str(e)}")
                continue
        
        # Regrouper les prévisions par jour
        daily_forecasts = {}
        
        for forecast in forecasts:
            date = forecast['datetime'].date()
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'date': date,
                    'datetime': datetime.combine(date, datetime.min.time()),  # Ajouter datetime pour éviter les erreurs
                    'temp': {'min': float('inf'), 'max': float('-inf')},
                    'humidity': 0,
                    'wind_speed': 0,
                    'weather': {'description': '', 'icon': ''},
                    'forecasts': []
                }
            
            # Ajouter la prévision à la liste des prévisions du jour
            daily_forecasts[date]['forecasts'].append(forecast)
            
            # Mettre à jour les températures min/max
            daily_forecasts[date]['temp']['min'] = min(daily_forecasts[date]['temp']['min'], forecast['temperature'])
            daily_forecasts[date]['temp']['max'] = max(daily_forecasts[date]['temp']['max'], forecast['temperature'])
        
        # Calculer les moyennes et déterminer l'icône et la description les plus représentatives
        result = []
        for date, day_data in sorted(daily_forecasts.items()):
            forecasts_count = len(day_data['forecasts'])
            if forecasts_count == 0:
                continue
                
            # Calculer les moyennes
            humidity_sum = sum(f['humidity'] for f in day_data['forecasts'])
            wind_speed_sum = sum(f['wind_speed'] for f in day_data['forecasts'])
            
            day_data['humidity'] = round(humidity_sum / forecasts_count)
            day_data['wind_speed'] = round(wind_speed_sum / forecasts_count, 1)
            
            # Déterminer l'icône et la description les plus représentatives (milieu de journée)
            midday_forecasts = [f for f in day_data['forecasts'] 
                               if 10 <= f['datetime'].hour <= 16]
            
            if midday_forecasts:
                # Prendre la prévision la plus proche de midi
                midday_forecasts.sort(key=lambda x: abs(x['datetime'].hour - 12))
                representative = midday_forecasts[0]
            else:
                # Si pas de prévision de milieu de journée, prendre la première
                representative = day_data['forecasts'][0]
            
            day_data['weather']['description'] = representative['description']
            day_data['weather']['icon'] = representative['icon']
            
            # S'assurer que l'icône est définie
            if not day_data['weather']['icon']:
                # Attribuer une icône par défaut en fonction de la description ou de l'ID météo
                weather_id = representative.get('weather_id', 0)
                if 'pluie' in representative['description'].lower() or 'rain' in representative['description'].lower():
                    day_data['weather']['icon'] = '10d'  # Pluie
                elif 'nuage' in representative['description'].lower() or 'cloud' in representative['description'].lower():
                    day_data['weather']['icon'] = '03d'  # Nuageux
                elif 'soleil' in representative['description'].lower() or 'sun' in representative['description'].lower() or 'clear' in representative['description'].lower():
                    day_data['weather']['icon'] = '01d'  # Ensoleillé
                elif 'neige' in representative['description'].lower() or 'snow' in representative['description'].lower():
                    day_data['weather']['icon'] = '13d'  # Neige
                elif 'orage' in representative['description'].lower() or 'thunder' in representative['description'].lower():
                    day_data['weather']['icon'] = '11d'  # Orage
                else:
                    # Attribuer une icône en fonction de l'ID météo
                    if 200 <= weather_id < 300:  # Orage
                        day_data['weather']['icon'] = '11d'
                    elif 300 <= weather_id < 400:  # Bruine
                        day_data['weather']['icon'] = '09d'
                    elif 500 <= weather_id < 600:  # Pluie
                        day_data['weather']['icon'] = '10d'
                    elif 600 <= weather_id < 700:  # Neige
                        day_data['weather']['icon'] = '13d'
                    elif 700 <= weather_id < 800:  # Atmosphère (brouillard, etc.)
                        day_data['weather']['icon'] = '50d'
                    elif weather_id == 800:  # Ciel dégagé
                        day_data['weather']['icon'] = '01d'
                    elif 801 <= weather_id < 900:  # Nuages
                        day_data['weather']['icon'] = '03d'
                    else:
                        day_data['weather']['icon'] = '01d'  # Icône par défaut
            
            # Supprimer la liste des prévisions pour alléger le résultat
            del day_data['forecasts']
            
            result.append(day_data)
        
        # Limiter au nombre de jours demandés
        return result[:days]

    def _parse_date(self, date_str):
        """
        Convertit une chaîne de date en objet datetime
        
        Args:
            date_str (str): Chaîne de date à convertir
            
        Returns:
            datetime: Objet datetime ou date actuelle si la conversion échoue
        """
        if not date_str:
            return datetime.now()
            
        try:
            # Gérer le format ISO avec timezone Z (2025-03-09T15:00:00.000Z)
            if 'Z' in date_str:
                # Supprimer le Z et les millisecondes si présents
                date_str = date_str.replace('Z', '')
                if '.' in date_str:
                    date_str = date_str.split('.')[0]
                return datetime.fromisoformat(date_str)
                
            # Essayer différents formats de date
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            # Si aucun format ne correspond, retourner la date actuelle
            logger.warning(f"Format de date non reconnu: {date_str}")
            return datetime.now()
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de la date: {str(e)}")
            return datetime.now()

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
                - type_label: Type d'alerte (ex: 'Vent violent', 'Orages', etc.)
                - region: Département concerné
                - description: Description de l'alerte
                - severity: Niveau de sévérité (green, yellow, orange, red)
                - date_alert: Date de l'alerte
                - severity_display: Affichage du niveau (Vert, Jaune, Orange, Rouge)
        """
        try:
            # Récupérer les données de vigilance
            texts = self.get_vigilance_texts()
            if not texts or 'product' not in texts:
                logger.warning("Aucune donnée de vigilance textuelle récupérée")
                return []
            
            alerts = []
            
            # Mapping des niveaux de risque
            risk_mapping = {
                '1': 'green',
                '2': 'yellow',
                '3': 'orange',
                '4': 'red'
            }
            
            risk_display = {
                '1': 'Vert',
                '2': 'Jaune',
                '3': 'Orange',
                '4': 'Rouge'
            }
            
            # Parcourir les blocs de texte pour chaque département
            for bloc in texts['product'].get('text_bloc_items', []):
                domain_id = bloc.get('domain_id')
                domain_name = bloc.get('domain_name')
                
                # Ignorer les blocs qui ne sont pas des départements
                if not domain_id or not domain_id.isdigit() and domain_id not in ['2A', '2B']:
                    continue
                
                # Parcourir les items du bloc
                for item in bloc.get('bloc_items', []):
                    for text_item in item.get('text_items', []):
                        for term_item in text_item.get('term_items', []):
                            risk_code = term_item.get('risk_code')
                            if not risk_code:
                                continue
                                
                            # Récupérer les informations de l'alerte
                            severity = risk_mapping.get(risk_code, 'yellow')
                            severity_display = risk_display.get(risk_code, 'Jaune')
                            
                            # Construire la description à partir des subdivisions de texte
                            description_parts = []
                            for subdivision in term_item.get('subdivision_text', []):
                                if subdivision.get('bold_text'):
                                    description_parts.append(f"{subdivision['bold_text']}")
                                if subdivision.get('text'):
                                    description_parts.extend(subdivision['text'])
                            
                            description = ' '.join(description_parts).strip()
                            if not description:
                                continue
                            
                            # Créer l'alerte
                            alert = {
                                'type_label': text_item.get('hazard_name', 'Vigilance météo'),
                                'region': f"{domain_name} ({domain_id})",
                                'description': description,
                                'severity': severity,
                                'severity_display': severity_display,
                                'date_alert': datetime.now()
                            }
                            
                            # Ajouter l'alerte uniquement si elle n'existe pas déjà
                            if not any(a['region'] == alert['region'] and 
                                     a['type_label'] == alert['type_label'] and
                                     a['severity'] == alert['severity'] for a in alerts):
                                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des alertes de vigilance: {str(e)}")
            return []
    
    def _parse_date(self, date_str):
        """
        Convertit une chaîne de date en objet datetime
        
        Args:
            date_str (str): Chaîne de date à convertir
            
        Returns:
            datetime: Objet datetime ou date actuelle si la conversion échoue
        """
        if not date_str:
            return datetime.now()
            
        try:
            # Gérer le format ISO avec timezone Z (2025-03-09T15:00:00.000Z)
            if 'Z' in date_str:
                # Supprimer le Z et les millisecondes si présents
                date_str = date_str.replace('Z', '')
                if '.' in date_str:
                    date_str = date_str.split('.')[0]
                return datetime.fromisoformat(date_str)
                
            # Essayer différents formats de date
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            # Si aucun format ne correspond, retourner la date actuelle
            logger.warning(f"Format de date non reconnu: {date_str}")
            return datetime.now()
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de la date: {str(e)}")
            return datetime.now()