Architecture du projet
=====================

Structure du projet
------------------

Le projet est organisé comme suit:

.. code-block:: text

   ./check_meteo_france.py
./db_creation.sql
./db_projetbts.loo
./docker-compose.yml
./Dockerfile
./manage.py
./meteo/asgi.py
./meteo/__init__.py
./meteo/settings.py
./meteo/urls.py
./meteo/wsgi.py
./model_diagram.py
./README.md
./requirements.txt
./start.sh
./static/images/default-avatar.png
./static/images/france_map.svg
./static/images/login-bg.jpg
./static/images/logo.png
./weather/admin.py
   [...]

Structure technique
-----------------

L'application est construite sur les technologies suivantes:

* **Backend**: Django (Python)
* **Base de données**: MySQL
* **Conteneurisation**: Docker et Docker Compose
* **Interface web**: HTML, CSS, JavaScript

Composants principaux
-------------------

* **Modèles Django**: Définition des structures de données
* **Vues Django**: Logique de traitement des requêtes
* **Templates**: Interface utilisateur
* **Scripts d'automatisation**: Gestion du déploiement et maintenance
* **Services externes**: Intégration avec les API météo
