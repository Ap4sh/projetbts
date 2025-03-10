import os
import django
import datetime

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetbts.settings')
django.setup()

# Importer les modèles après avoir configuré Django
from weather.models import Alert, TypeAlert

# Créer des types d'alertes s'ils n'existent pas déjà
type_pluie, _ = TypeAlert.objects.get_or_create(label="Fortes pluies")
type_vent, _ = TypeAlert.objects.get_or_create(label="Vents violents")
type_orage, _ = TypeAlert.objects.get_or_create(label="Orages")
type_neige, _ = TypeAlert.objects.get_or_create(label="Chutes de neige")

# Créer des alertes de test
alerts_to_create = [
    {
        'fk_type': type_pluie,
        'region': 'Île-de-France',
        'description': 'Fortes précipitations attendues avec plus de 30mm de pluie en 24h.',
        'active': 1,
        'date_alert': datetime.date.today()
    },
    {
        'fk_type': type_vent,
        'region': 'Bretagne',
        'description': 'Vents violents pouvant atteindre 100 km/h sur le littoral.',
        'active': 1,
        'date_alert': datetime.date.today()
    },
    {
        'fk_type': type_orage,
        'region': 'Provence-Alpes-Côte d\'Azur',
        'description': 'Orages violents avec risque de grêle et fortes rafales.',
        'active': 1,
        'date_alert': datetime.date.today()
    },
    {
        'fk_type': type_neige,
        'region': 'Auvergne-Rhône-Alpes',
        'description': 'Chutes de neige importantes prévues en montagne, 20-30cm attendus.',
        'active': 1,
        'date_alert': datetime.date.today()
    }
]

# Supprimer les alertes existantes pour éviter les doublons
Alert.objects.all().delete()

# Créer les nouvelles alertes
for alert_data in alerts_to_create:
    Alert.objects.create(**alert_data)
    print(f"Alerte créée: {alert_data['fk_type'].label} - {alert_data['region']}")

print(f"Nombre total d'alertes créées: {Alert.objects.count()}") 