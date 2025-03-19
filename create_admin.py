#!/usr/bin/env python
import os
import django
import sys

# Configurer l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

# Importer le modèle User après avoir configuré Django
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Récupérer les informations d'environnement (valeurs par défaut si non définies)
admin_username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
admin_password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin')
admin_email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@exemple.com')

# Vérifier si un utilisateur admin existe déjà
if User.objects.filter(username=admin_username).exists():
    print(f"L'utilisateur admin '{admin_username}' existe déjà.")
    # Mettre à jour le mot de passe si demandé
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        admin_user = User.objects.get(username=admin_username)
        admin_user.set_password(admin_password)
        admin_user.save()
        print(f"Mot de passe mis à jour pour l'utilisateur '{admin_username}'.")
else:
    # Créer un nouvel utilisateur admin
    admin_user = User.objects.create_superuser(
        username=admin_username,
        email=admin_email,
        password=admin_password
    )
    print(f"Utilisateur admin '{admin_username}' créé avec succès.")
    print(f"Email: {admin_email}")
    print("Mot de passe: [défini selon la configuration]") 