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
echo -e "\n🛑 ÉTAPE 1/6 : Arrêt des conteneurs en cours..."
docker-compose down -v

# Récupérer les derniers changements du dépôt Git
echo -e "\n🔄 ÉTAPE 2/6 : Récupération des derniers changements du dépôt Git..."
#git pull --rebase origin main

# Reconstruire les images Docker
echo -e "\n🏗️ ÉTAPE 3/6 : Reconstruction des images Docker..."
docker-compose build

# Supprimer les migrations existantes pour éviter les conflits
echo -e "\n🧹 ÉTAPE 4/6 : Préparation des migrations Django..."
find ./weather/migrations -name "*.py" ! -name "__init__.py" -delete

# Démarrer la base de données d'abord
echo -e "\n🚀 ÉTAPE 5/6 : Démarrage de la base de données..."
docker-compose up -d db

# Attendre que la base de données soit prête
echo -e "\n⏳ Attente de la disponibilité de la base de données..."
sleep 15

# Initialiser la base de données avec le fichier SQL
echo -e "\n📊 Initialisation des tables de base de données..."
docker-compose exec -T db mysql -u root -proot_password < db_creation.sql

# Exécuter le script de réparation
echo -e "\n🔧 Application des correctifs à la base de données..."
docker-compose run --rm web python fix_database.py

# Démarrer le service web
echo -e "\n🚀 ÉTAPE 6/6 : Démarrage du service web..."
docker-compose up -d web

# Attendre que le service web soit prêt
sleep 5

# Créer le dossier static s'il n'existe pas
echo -e "\n📁 Création du dossier static..."
docker-compose exec web mkdir -p /app/static

# Exécuter init_django.py pour configurer les modèles
echo -e "\n🔧 Configuration des modèles Django..."
docker-compose exec web python init_django.py

# Créer un utilisateur admin Django si nécessaire
echo -e "\n👤 Création de l'utilisateur admin Django..."
docker-compose exec -T web bash -c "export \$(cat .env | grep DJANGO_ADMIN | xargs) && python create_admin.py"

# Vérifier les alertes et finaliser
echo -e "\n✅ Finalisation..."
docker-compose exec web python manage.py check_weather_alerts

# Afficher un message de succès
echo -e "\n✅ TERMINÉ : L'application a été redémarrée avec succès !"
echo "Pour accéder à l'application, ouvrez http://localhost:8000 dans votre navigateur."
echo "Pour accéder à l'interface d'administration, ouvrez http://localhost:8000/admin/"
echo "   - Utilisateur : $(grep DJANGO_ADMIN_USERNAME .env | cut -d= -f2)"
echo "   - Mot de passe : $(grep DJANGO_ADMIN_PASSWORD .env | cut -d= -f2)"
echo -e "Pour voir les logs en temps réel, exécutez : docker-compose logs -f"
echo "====================================================="

# Demander à l'utilisateur s'il souhaite voir les logs
read -p "Voulez-vous afficher les logs maintenant ? (o/n) : " afficher_logs
if [[ "$afficher_logs" == "o" || "$afficher_logs" == "O" ]]; then
    echo -e "\n📋 Affichage des logs (Ctrl+C pour quitter)..."
    docker-compose logs -f
fi 