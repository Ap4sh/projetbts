import logging
import requests
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.models import Alert, TypeAlert

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Importe les alertes météo réelles depuis l\'API de Météo-France'
    
    def handle(self, *args, **options):
        self.stdout.write('Importation des alertes météo depuis Météo-France...')
        
        # URL de l'API de vigilance Météo-France (format JSON)
        vigilance_url = "https://vigilance.meteofrance.fr/fr/carte-de-vigilance.json"
        
        try:
            # Récupérer les données de vigilance
            response = requests.get(vigilance_url, timeout=10)
            response.raise_for_status()
            
            # Analyser le JSON
            data = response.json()
            
            # Vérifier si les données contiennent les informations de vigilance
            if 'meta' not in data or 'update_time' not in data['meta']:
                self.stdout.write(self.style.WARNING("Format de données inattendu dans la réponse de Météo-France"))
                return
            
            # Date de mise à jour des données
            update_time = data['meta']['update_time']
            self.stdout.write(f"Données de vigilance mises à jour le : {update_time}")
            
            # Dictionnaire pour mapper les niveaux de vigilance aux types d'alertes
            vigilance_levels = {
                "1": "Vert - Pas de vigilance particulière",
                "2": "Jaune - Soyez attentif",
                "3": "Orange - Soyez très vigilant",
                "4": "Rouge - Vigilance absolue"
            }
            
            # Dictionnaire pour mapper les phénomènes aux types d'alertes
            phenomena_types = {
                "1": "Vent violent",
                "2": "Pluie-inondation",
                "3": "Orages",
                "4": "Crues",
                "5": "Neige-verglas",
                "6": "Canicule",
                "7": "Grand froid",
                "8": "Avalanches",
                "9": "Vagues-submersion"
            }
            
            # Parcourir les données de vigilance des départements
            alerts_count = 0
            
            if 'data' in data and 'departments' in data['data']:
                for dept in data['data']['departments']:
                    dept_id = dept.get('department_code')
                    dept_name = dept.get('department_name')
                    vigilance_level = dept.get('vigilance_level')
                    
                    # Ne traiter que les alertes orange (3) ou rouge (4)
                    if vigilance_level in ["3", "4"]:
                        vigilance_type = vigilance_levels.get(vigilance_level, "Alerte météo")
                        
                        # Parcourir les phénomènes pour ce département
                        phenomena = dept.get('phenomenons_items', [])
                        for phenomenon in phenomena:
                            phenomenon_id = phenomenon.get('phenomenon_id')
                            phenomenon_level = phenomenon.get('phenomenon_max_level')
                            
                            # Ne traiter que les phénomènes en alerte orange ou rouge
                            if phenomenon_level in ["3", "4"] and phenomenon_id in phenomena_types:
                                phenomenon_type = phenomena_types[phenomenon_id]
                                
                                # Créer ou récupérer le type d'alerte
                                alert_type, created = TypeAlert.objects.get_or_create(
                                    label=f"{vigilance_type} - {phenomenon_type}"
                                )
                                
                                # Description de l'alerte
                                description = f"Vigilance {vigilance_type.split(' - ')[0]} pour {phenomenon_type} dans le département {dept_name} ({dept_id})"
                                
                                # Vérifier si l'alerte existe déjà
                                existing_alert = Alert.objects.filter(
                                    fk_type=alert_type,
                                    region=dept_name,
                                    date_alert=timezone.now().date()
                                ).first()
                                
                                if not existing_alert:
                                    # Créer l'alerte
                                    Alert.objects.create(
                                        fk_type=alert_type,
                                        region=dept_name,
                                        description=description,
                                        active=1,
                                        date_alert=timezone.now().date()
                                    )
                                    alerts_count += 1
                                    self.stdout.write(self.style.SUCCESS(
                                        f"Nouvelle alerte créée pour {dept_name}: {alert_type.label}"
                                    ))
            
            if alerts_count == 0:
                self.stdout.write("Aucune nouvelle alerte météo trouvée. Tous les départements sont en vigilance verte ou jaune.")
            else:
                self.stdout.write(self.style.SUCCESS(f"{alerts_count} nouvelles alertes météo importées."))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la récupération des données de vigilance: {str(e)}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de l'analyse du JSON: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur inattendue: {str(e)}")) 