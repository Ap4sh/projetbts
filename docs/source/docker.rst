Docker et déploiement
====================

Configuration Docker
-----------------

Le projet utilise Docker et Docker Compose pour faciliter le déploiement.

Conteneurs:

.. list-table::
   :header-rows: 1

   * - Service
     - Image
     - Description
   * - web
     - Python 3.11
     - Application Django
   * - db
     - MySQL
     - Base de données

Fichier docker-compose.yml
------------------------

.. code-block:: yaml

   version: '3'
   
   services:
     web:
       build: .
       volumes:
         - .:/app
       ports:
         - "8000:8000"
       depends_on:
         - db
       environment:
         - DATABASE_URL=mysql://root:root_password@db:3306/weather_db
     
     db:
       image: mysql:8
       environment:
         - MYSQL_ROOT_PASSWORD=root_password
         - MYSQL_DATABASE=weather_db
       volumes:
         - db_data:/var/lib/mysql
   
   volumes:
     db_data:

Scripts de gestion
---------------

Le projet inclut plusieurs scripts pour faciliter la gestion:

* `start.sh` - Démarrage complet de l'application
* `fix_migrations.sh` - Résolution des conflits de migrations Django
