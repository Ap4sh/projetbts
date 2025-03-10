#!/bin/bash

# Afficher un message de bienvenue
echo "====================================================="
echo "      Script de gestion du projet météo BTS"
echo "====================================================="

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Erreur: Docker et/ou Docker Compose ne sont pas installés."
    echo "Veuillez installer Docker et Docker Compose avant d'exécuter ce script."
    exit 1
fi

# Arrêter tous les conteneurs en cours d'exécution
echo -e "\n🛑 ÉTAPE 1/5 : Arrêt des conteneurs en cours..."
docker-compose down -v

# Récupérer les derniers changements du dépôt Git
echo -e "\n🔄 ÉTAPE 2/5 : Récupération des derniers changements du dépôt Git..."
git pull origin main

# Reconstruire les images Docker
echo -e "\n🏗️ ÉTAPE 3/5 : Reconstruction des images Docker..."
docker-compose build

# Démarrer les conteneurs
echo -e "\n🚀 ÉTAPE 4/5 : Démarrage des conteneurs..."
docker-compose up -d

# Attendre que la base de données soit prête
echo -e "\n⏳ Attente de la disponibilité de la base de données..."
sleep 10

# Appliquer les migrations et vérifier les alertes
echo -e "\n📊 ÉTAPE 5/5 : Configuration finale..."
echo "- Application des migrations de la base de données"
docker-compose exec web python manage.py migrate
echo "- Vérification des alertes météo"
docker-compose exec web python manage.py check_weather_alerts

# Afficher un message de succès
echo -e "\n✅ TERMINÉ : L'application a été redémarrée avec succès !"
echo "Pour accéder à l'application, ouvrez http://localhost:8000 dans votre navigateur."
echo -e "Pour voir les logs en temps réel, exécutez : docker-compose logs -f"
echo "====================================================="

# Demander à l'utilisateur s'il souhaite voir les logs
read -p "Voulez-vous afficher les logs maintenant ? (o/n) : " afficher_logs
if [[ "$afficher_logs" == "o" || "$afficher_logs" == "O" ]]; then
    echo -e "\n📋 Affichage des logs (Ctrl+C pour quitter)..."
    docker-compose logs -f
fi 