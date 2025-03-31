#!/usr/bin/env python
import os
import django
import sys

# Configurer l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

# Importer le modèle CustomUser après avoir configuré Django
from weather.models import CustomUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Récupérer les informations d'environnement (valeurs par défaut si non définies)
admin_email = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin@exemple.com')
admin_password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin')

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
        password=admin_password
    )
    print(f"Utilisateur admin '{admin_email}' créé avec succès.")
    print("Mot de passe: [défini selon la configuration]") 