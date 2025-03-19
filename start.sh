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
echo -e "\n🛑 ÉTAPE 1/8 : Arrêt des conteneurs en cours..."
docker-compose down -v

# Récupérer les derniers changements du dépôt Git
echo -e "\n🔄 ÉTAPE 2/8 : Récupération des derniers changements du dépôt Git..."
git pull --rebase origin main

# Reconstruire les images Docker
echo -e "\n🏗️ ÉTAPE 3/8 : Reconstruction des images Docker..."
docker-compose build

# Démarrer les conteneurs
echo -e "\n🚀 ÉTAPE 4/8 : Démarrage des conteneurs..."
docker-compose up -d

# Attendre que la base de données soit prête
echo -e "\n⏳ Attente de la disponibilité de la base de données..."
sleep 10

# Initialiser la base de données avec le fichier SQL
echo -e "\n📊 ÉTAPE 5/8 : Initialisation de la base de données..."
echo "- Exécution du script SQL de création des tables"
docker-compose exec -T db mysql -u root -proot_password < db_creation.sql
echo "- Création des migrations pour correspondre à la structure existante"
docker-compose exec web python manage.py inspectdb > weather/models_auto.py
echo "- Création des migrations"
docker-compose exec web python manage.py makemigrations --empty weather
echo "- Application des migrations avec --fake-initial pour éviter les conflits"
docker-compose exec web python manage.py migrate --fake-initial

# Résoudre les conflits de migrations (intégration de fix_migrations.sh)
echo -e "\n🔄 ÉTAPE 6/8 : Résolution des conflits de migrations Django..."
echo "- Arrêt temporaire du conteneur web"
docker-compose stop web
echo "- Exécution de makemigrations avec l'option --merge pour résoudre les conflits"
docker-compose run --rm web python manage.py makemigrations --merge
echo "- Application des migrations"
docker-compose run --rm web python manage.py migrate
echo "- Redémarrage du service web"
docker-compose up -d web

# Créer un utilisateur admin Django si nécessaire
echo -e "\n👤 ÉTAPE 7/8 : Création de l'utilisateur admin Django..."
# Copier le script create_admin.py dans le conteneur web
docker cp create_admin.py projetbts-web-1:/app/
# Exécuter le script avec les variables d'environnement du fichier .env
docker-compose exec -T web bash -c "export \$(cat .env | grep DJANGO_ADMIN | xargs) && python create_admin.py"

# Vérifier les alertes et finaliser
echo -e "\n🔧 ÉTAPE 8/8 : Finalisation..."
echo "- Vérification des alertes météo"
docker-compose exec web python manage.py check_weather_alerts

# Afficher un message de succès
echo -e "\n✅ TERMINÉ : L'application a été redémarrée avec succès !"
echo "Pour accéder à l'application, ouvrez http://localhost:8000 dans votre navigateur."
echo "Pour accéder à l'interface d'administration, ouvrez http://localhost:8000/admin/"
echo "   - Utilisateur : \$(grep DJANGO_ADMIN_USERNAME .env | cut -d= -f2)"
echo "   - Mot de passe : \$(grep DJANGO_ADMIN_PASSWORD .env | cut -d= -f2)"
echo -e "Pour voir les logs en temps réel, exécutez : docker-compose logs -f"
echo "====================================================="

# Demander à l'utilisateur s'il souhaite voir les logs
read -p "Voulez-vous afficher les logs maintenant ? (o/n) : " afficher_logs
if [[ "$afficher_logs" == "o" || "$afficher_logs" == "O" ]]; then
    echo -e "\n📋 Affichage des logs (Ctrl+C pour quitter)..."
    docker-compose logs -f
fi 