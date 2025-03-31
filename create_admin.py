#!/usr/bin/env python
import os
import django
import sys

# Configurer l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

# Importer les modèles nécessaires après avoir configuré Django
from weather.models import CustomUser, Cities, Departments, Regions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

# Récupérer les informations d'environnement (valeurs par défaut si non définies)
admin_email = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin@exemple.com')
admin_password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin')

def create_default_data():
    """Crée des données de base si elles n'existent pas encore"""
    print("Vérification des données de base...")
    
    try:
        # Vérifier si une région existe déjà
        if not Regions.objects.exists():
            print("Création d'une région par défaut")
            default_region = Regions.objects.create(label="Île-de-France")
        else:
            default_region = Regions.objects.first()
            
        # Vérifier si un département existe déjà
        if not Departments.objects.exists():
            print("Création d'un département par défaut")
            default_dept = Departments.objects.create(
                label="Paris",
                region=default_region
            )
        else:
            default_dept = Departments.objects.first()
            
        # Vérifier si une ville existe déjà
        if not Cities.objects.exists():
            print("Création d'une ville par défaut")
            default_city = Cities.objects.create(
                label="Paris",
                department=default_dept
            )
            # Ajouter d'autres villes principales
            for city_name in ["Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Bordeaux", "Lille"]:
                Cities.objects.create(
                    label=city_name,
                    department=default_dept
                )
            return default_city
        else:
            # Vérifier si Paris existe
            paris = Cities.objects.filter(label__iexact="Paris").first()
            if not paris:
                # Créer Paris si elle n'existe pas
                paris = Cities.objects.create(
                    label="Paris",
                    department=default_dept
                )
                print("Création de la ville de Paris")
            return paris or Cities.objects.first()
    except Exception as e:
        print(f"Erreur lors de la création des données par défaut : {e}")
        sys.exit(1)

# Fonction principale
def main():
    try:
        with transaction.atomic():
            # Essayer de trouver ou créer une ville par défaut
            default_city = create_default_data()
            
            # Vérifier si un utilisateur admin existe déjà
            if CustomUser.objects.filter(email=admin_email).exists():
                print(f"L'utilisateur admin '{admin_email}' existe déjà.")
                # Mettre à jour le mot de passe si demandé
                if len(sys.argv) > 1 and sys.argv[1] == '--update':
                    admin_user = CustomUser.objects.get(email=admin_email)
                    admin_user.set_password(admin_password)
                    admin_user.save()
                    print(f"Mot de passe mis à jour pour l'utilisateur '{admin_email}'.")
            else:
                # Créer un nouvel utilisateur admin
                admin_user = CustomUser.objects.create_superuser(
                    email=admin_email,
                    password=admin_password,
                    city=default_city
                )
                print(f"Utilisateur admin '{admin_email}' créé avec succès.")
                print("Mot de passe: [défini selon la configuration]")
    except Exception as e:
        print(f"Erreur lors de la création/mise à jour de l'utilisateur admin: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 