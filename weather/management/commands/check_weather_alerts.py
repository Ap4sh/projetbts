import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.models import Alert, TypeAlert, CustomUser, Departments
from weather.services.weather_api import OpenWeatherMapService, MAIN_FRENCH_CITIES
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Vérifie les alertes météo et les enregistre dans la base de données'
    
    def handle(self, *args, **options):
        self.stdout.write('Vérification des alertes météo...')
        
        # Initialiser le service météo
        weather_service = OpenWeatherMapService()
        
        # Définir les seuils pour les conditions météo extrêmes
        thresholds = {
            'rain_heavy': 10.0,     # mm de pluie en 3h (>10mm = fortes pluies)
            'rain_very_heavy': 20.0, # mm de pluie en 3h (>20mm = très fortes pluies)
            'snow_heavy': 5.0,      # mm de neige en 3h
            'wind_strong': 10.8,    # m/s (environ 39 km/h) - Force 6 sur échelle Beaufort
            'wind_gale': 17.2,      # m/s (environ 62 km/h) - Force 8 sur échelle Beaufort
            'temp_very_hot': 32.0,  # °C - Seuil d'alerte canicule
            'temp_hot': 28.0,       # °C - Forte chaleur
            'temp_cold': 0.0,       # °C - Gel
            'temp_very_cold': -5.0  # °C - Grand froid
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
        
        alerts_count = 0
        
        # Vérifier les alertes pour chaque ville principale
        for city in MAIN_FRENCH_CITIES:
            city_name = city['name']
            
            # 1. Vérifier les conditions météo actuelles
            current_weather = weather_service.get_current_weather(city_name)
            if current_weather:
                # Vérifier les conditions extrêmes
                self._check_current_conditions(current_weather, thresholds, weather_alerts, city_name)
            
            # 2. Vérifier les prévisions pour les prochains jours
            forecast = weather_service.get_forecast(city_name, days=5)
            if forecast:
                for day_forecast in forecast:
                    # Vérifier si la prévision a une date valide (soit datetime soit date)
                    forecast_date = None
                    
                    if 'datetime' in day_forecast:
                        forecast_date = day_forecast['datetime'].date() if isinstance(day_forecast['datetime'], datetime) else None
                    elif 'date' in day_forecast:
                        forecast_date = day_forecast['date'] if isinstance(day_forecast['date'], (datetime, date)) else None
                    
                    if forecast_date is None:
                        self.stdout.write(self.style.WARNING(f"Prévision sans date pour {city_name}, ignorée"))
                        continue
                        
                    # Ne traiter que les prévisions futures (pas celles du passé)
                    if forecast_date >= timezone.now().date():
                        alerts = self._check_forecast_conditions(day_forecast, thresholds, weather_alerts, city_name, forecast_date)
                        alerts_count += len(alerts)
        
        if alerts_count == 0:
            self.stdout.write("Aucune nouvelle alerte météo trouvée.")
        else:
            self.stdout.write(self.style.SUCCESS(f"{alerts_count} nouvelles alertes météo créées."))
        
        self.stdout.write(self.style.SUCCESS('Vérification des alertes terminée'))
    
    def _check_current_conditions(self, weather_data, thresholds, weather_alerts, city_name):
        """
        Vérifie les conditions météo actuelles et crée des alertes si nécessaire
        """
        alerts_created = []
        
        # Extraire les données météo
        temp = weather_data.get('temperature', {}).get('temp', 20)
        wind_speed = weather_data.get('wind', {}).get('speed', 0)
        weather_id = weather_data.get('weather', {}).get('id', 800)
        weather_desc = weather_data.get('weather', {}).get('description', '')
        
        # Vérifier les conditions extrêmes
        
        # 1. Phénomènes dangereux (tornades, orages violents)
        if weather_id == 781:  # Tornade
            alert = self._create_alert("Tornade", 
                f"Risque de tornade à {city_name}. Phénomène dangereux et rare en France. Mettez-vous à l'abri.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif weather_id == 771:  # Tempête
            alert = self._create_alert("Tempête violente", 
                f"Tempête violente à {city_name}. Rafales destructrices possibles.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif weather_id in weather_alerts['thunderstorm'] and weather_id < 210:  # Orages violents
            alert = self._create_alert("Orages violents", 
                f"Orages violents à {city_name}. {weather_desc.capitalize()}.",
                city_name)
            if alert:
                alerts_created.append(alert)
        
        # 2. Vents forts
        elif wind_speed > thresholds['wind_gale']:
            alert = self._create_alert("Vents violents", 
                f"Vents violents à {city_name} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h). Risque de dégâts.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif wind_speed > thresholds['wind_strong']:
            alert = self._create_alert("Vents forts", 
                f"Vents forts à {city_name} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h).",
                city_name)
            if alert:
                alerts_created.append(alert)
        
        # 3. Températures extrêmes
        if temp > thresholds['temp_very_hot']:
            alert = self._create_alert("Canicule", 
                f"Canicule à {city_name} avec {temp:.1f}°C. Protégez-vous de la chaleur.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif temp > thresholds['temp_hot']:
            alert = self._create_alert("Forte chaleur", 
                f"Températures élevées à {city_name} avec {temp:.1f}°C.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif temp < thresholds['temp_very_cold']:
            alert = self._create_alert("Grand froid", 
                f"Températures très basses à {city_name} avec {temp:.1f}°C. Risque de gel important.",
                city_name)
            if alert:
                alerts_created.append(alert)
                
        elif temp < thresholds['temp_cold']:
            alert = self._create_alert("Gel", 
                f"Températures négatives à {city_name} avec {temp:.1f}°C. Risque de verglas.",
                city_name)
            if alert:
                alerts_created.append(alert)
        
        # 4. Autres phénomènes notables
        elif weather_id in weather_alerts['fog']:
            alert = self._create_alert("Brouillard", 
                f"Brouillard dense à {city_name}. Visibilité réduite, prudence sur les routes.",
                city_name)
            if alert:
                alerts_created.append(alert)
        
        return alerts_created
    
    def _check_forecast_conditions(self, forecast, thresholds, weather_alerts, city_name, forecast_date):
        """
        Vérifie les conditions météo prévues et crée des alertes si nécessaire
        """
        alerts_created = []
        
        # Extraire les données de prévision
        temp = forecast.get('temperature', 20)
        wind_speed = forecast.get('wind_speed', 0)
        rain = forecast.get('rain', 0)
        snow = forecast.get('snow', 0)
        weather_id = forecast.get('weather_id', 800)
        weather_desc = forecast.get('description', '')
        
        # Formater la date pour l'affichage
        date_str = forecast_date.strftime('%d/%m/%Y')
        
        # Vérifier les conditions extrêmes
        
        # 1. Précipitations extrêmes
        if rain > thresholds['rain_very_heavy']:
            alert = self._create_alert("Pluies diluviennes", 
                f"Précipitations exceptionnelles prévues à {city_name} le {date_str} avec {rain:.1f}mm de pluie en 3h. Risque d'inondation.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif rain > thresholds['rain_heavy']:
            alert = self._create_alert("Fortes pluies", 
                f"Fortes précipitations prévues à {city_name} le {date_str} avec {rain:.1f}mm de pluie en 3h.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif snow > thresholds['snow_heavy']:
            alert = self._create_alert("Chutes de neige importantes", 
                f"Chutes de neige importantes prévues à {city_name} le {date_str} avec {snow:.1f}mm en 3h. Conditions de circulation difficiles.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
        
        # 2. Vents forts
        elif wind_speed > thresholds['wind_gale']:
            alert = self._create_alert("Vents violents", 
                f"Vents violents prévus à {city_name} le {date_str} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h). Risque de dégâts.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif wind_speed > thresholds['wind_strong']:
            alert = self._create_alert("Vents forts", 
                f"Vents forts prévus à {city_name} le {date_str} avec des vitesses atteignant {wind_speed:.1f}m/s ({wind_speed*3.6:.1f}km/h).",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
        
        # 3. Températures extrêmes
        elif temp > thresholds['temp_very_hot']:
            alert = self._create_alert("Canicule", 
                f"Canicule prévue à {city_name} le {date_str} avec {temp:.1f}°C. Protégez-vous de la chaleur.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif temp > thresholds['temp_hot']:
            alert = self._create_alert("Forte chaleur", 
                f"Températures élevées prévues à {city_name} le {date_str} avec {temp:.1f}°C.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif temp < thresholds['temp_very_cold']:
            alert = self._create_alert("Grand froid", 
                f"Températures très basses prévues à {city_name} le {date_str} avec {temp:.1f}°C. Risque de gel important.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
                
        elif temp < thresholds['temp_cold']:
            alert = self._create_alert("Gel", 
                f"Températures négatives prévues à {city_name} le {date_str} avec {temp:.1f}°C. Risque de verglas.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
        
        # 4. Phénomènes spécifiques basés sur les codes météo
        elif weather_id in weather_alerts['thunderstorm']:
            alert = self._create_alert("Orages", 
                f"Orages prévus à {city_name} le {date_str}. {weather_desc.capitalize()}.",
                city_name, forecast_date)
            if alert:
                alerts_created.append(alert)
        
        return alerts_created
    
    def _create_alert(self, alert_type_label, description, region, date=None):
        """
        Crée une alerte dans la base de données
        
        Args:
            alert_type_label (str): Libellé du type d'alerte
            description (str): Description de l'alerte
            region (str): Région concernée
            date (date, optional): Date de l'alerte. Par défaut, date du jour.
            
        Returns:
            Alert: L'alerte créée ou None si elle existe déjà
        """
        if date is None:
            date = timezone.now().date()
        
        # Créer ou récupérer le type d'alerte
        alert_type, created = TypeAlert.objects.get_or_create(
            label=alert_type_label
        )
        
        # Vérifier si l'alerte existe déjà
        existing_alert = Alert.objects.filter(
            fk_type=alert_type,
            region=region,
            date_alert=date
        ).first()
        
        if not existing_alert:
            try:
                # Trouver un département valide pour cette région
                department = Departments.objects.first()  # Utiliser le premier département disponible
                
                if not department:
                    self.stdout.write(self.style.WARNING(
                        f"Impossible de créer l'alerte : aucun département disponible"
                    ))
                    return None
                
                # Créer l'alerte
                alert = Alert.objects.create(
                    fk_type=alert_type,
                    region=region,
                    description=description,
                    active=1,
                    date_alert=date,
                    department=department  # Utiliser le département trouvé
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Nouvelle alerte créée pour {region}: {alert_type.label}"
                ))
                return alert
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Erreur lors de la création de l'alerte: {str(e)}"
                ))
                return None
        
        return None 