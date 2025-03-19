Utilisation
==========

Interface Web
------------

L'application web est accessible à l'adresse http://localhost:8000 après le démarrage.

Fonctionnalités principales
-------------------------

* Visualisation des données météo
* Affichage des alertes météorologiques
* Consultation de l'historique des relevés

API REST
-------

L'API REST est disponible aux endpoints suivants:

* `/api/meteo/` - Données météo actuelles
* `/api/alertes/` - Alertes météo actives

Exemples d'utilisation
-------------------

Récupération des données météo actuelles:

.. code-block:: bash

   curl http://localhost:8000/api/meteo/

Récupération des alertes:

.. code-block:: bash

   curl http://localhost:8000/api/alertes/
