Installation
===========

Prérequis
---------

* Docker et Docker Compose
* Git

Instructions d'installation
--------------------------

1. Cloner le dépôt:

   .. code-block:: bash

      git clone <URL_DU_DEPOT>
      cd projetbts

2. Lancer l'application avec Docker:

   .. code-block:: bash

      ./start.sh

Le script start.sh effectue automatiquement les opérations suivantes:

- Arrêt des conteneurs en cours d'exécution
- Récupération des changements Git
- Construction des images Docker
- Démarrage des conteneurs
- Initialisation de la base de données
- Résolution des conflits de migrations Django
- Vérification des alertes météo

Configuration
------------

Les paramètres de configuration sont définis dans le fichier `.env` à la racine du projet.
