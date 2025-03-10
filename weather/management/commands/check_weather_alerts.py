import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.models import Alert, TypeAlert, CustomUser
from weather.services.weather_api import OpenWeatherMapService
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Vérifie les alertes météo et les enregistre dans la base de données'
    
    def handle(self, *args, **options):
        self.stdout.write('Vérification des alertes météo...')
        
        regions = CustomUser.objects.values_list('region', flat=True).distinct()
        
        region_coordinates = {
            'Île-de-France': {'lat': 48.8566, 'lon': 2.3522},  # Paris
            'Auvergne-Rhône-Alpes': {'lat': 45.7578, 'lon': 4.8320},  # Lyon
            'Provence-Alpes-Côte d\'Azur': {'lat': 43.2965, 'lon': 5.3698},  # Marseille
            'Occitanie': {'lat': 43.6047, 'lon': 1.4442},  # Toulouse
            'Nouvelle-Aquitaine': {'lat': 44.8378, 'lon': -0.5792},  # Bordeaux
            'Bretagne': {'lat': 48.1173, 'lon': -1.6778},  # Rennes
            'Normandie': {'lat': 49.4431, 'lon': 1.0993},  # Rouen
            'Hauts-de-France': {'lat': 50.6292, 'lon': 3.0573},  # Lille
            'Grand Est': {'lat': 48.5734, 'lon': 7.7521},  # Strasbourg
            'Pays de la Loire': {'lat': 47.2184, 'lon': -1.5536},  # Nantes
            'Bourgogne-Franche-Comté': {'lat': 47.3220, 'lon': 5.0415},  # Dijon
            'Centre-Val de Loire': {'lat': 47.9027, 'lon': 1.9090},  # Orléans
            'Corse': {'lat': 42.0396, 'lon': 9.0129}  # Ajaccio
        }
        
        weather_service = OpenWeatherMapService()
        
        for region in regions:
            if region in region_coordinates:
                lat = region_coordinates[region]['lat']
                lon = region_coordinates[region]['lon']
                
                alerts = weather_service.get_weather_alerts(lat, lon)
                
                if alerts:
                    for alert_data in alerts:
                        alert_type, created = TypeAlert.objects.get_or_create(
                            label=alert_data.get('event', 'Alerte météo')
                        )
                        
                        alert_date = datetime.fromtimestamp(alert_data.get('start', timezone.now().timestamp())).date()
                        
                        existing_alert = Alert.objects.filter(
                            fk_type=alert_type,
                            region=region,
                            date_alert=alert_date
                        ).first()
                        
                        if not existing_alert:
                            Alert.objects.create(
                                fk_type=alert_type,
                                region=region,
                                description=alert_data.get('description', '')[:255],  # 255 caractères
                                active=1,
                                date_alert=alert_date
                            )
                            self.stdout.write(self.style.SUCCESS(
                                f'Nouvelle alerte créée pour {region}: {alert_type.label}'
                            ))
                        else:
                            self.stdout.write(
                                f'Alerte existante pour {region}: {alert_type.label}'
                            )
            else:
                self.stdout.write(self.style.WARNING(
                    f'Coordonnées non disponibles pour la région: {region}'
                ))
        
        self.stdout.write(self.style.SUCCESS('Vérification des alertes terminée')) 