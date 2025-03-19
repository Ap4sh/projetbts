#!/usr/bin/env python
import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteo.settings')
django.setup()

# Exécuter la commande graph_models
from django.core.management import call_command
call_command('graph_models', 'weather', output='docs/source/_static/models.png')
print("Diagramme des modèles généré avec succès.")
