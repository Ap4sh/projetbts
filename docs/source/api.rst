API Reference
============

Cette section contient la documentation détaillée de l'API.

Endpoints
--------

.. list-table::
   :header-rows: 1

   * - Endpoint
     - Méthode
     - Description
   * - /api/meteo/
     - GET
     - Récupère les données météo actuelles
   * - /api/alertes/
     - GET
     - Récupère les alertes météo actives

Format des données
----------------

Les données sont retournées au format JSON.

Exemple de réponse pour /api/meteo/:

.. code-block:: json

   {
     "station": "Paris",
     "temperature": 23.5,
     "humidity": 65,
     "pressure": 1013,
     "wind_speed": 15,
     "wind_direction": "NE",
     "timestamp": "2023-06-15T14:30:00Z"
   }
