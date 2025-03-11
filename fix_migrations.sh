#!/bin/bash

echo "Script de résolution des conflits de migrations Django"
echo "===================================================="

# Se placer dans le répertoire du projet
cd "$(dirname "$0")"

# Vérifier si le conteneur web est en cours d'exécution
if docker-compose ps | grep -q "web.*Up"; then
    echo "Le conteneur web est en cours d'exécution, arrêt..."
    docker-compose stop web
fi

# Lancer le conteneur web en mode interactif pour résoudre les conflits
echo "Lancement du conteneur web pour résoudre les conflits de migrations..."
docker-compose run --rm web python manage.py makemigrations --merge

# Appliquer les migrations
echo "Application des migrations..."
docker-compose run --rm web python manage.py migrate

# Redémarrer le conteneur web
echo "Redémarrage du service web..."
docker-compose up -d web

echo "===================================================="
echo "Terminé ! Le service web devrait maintenant fonctionner correctement." 