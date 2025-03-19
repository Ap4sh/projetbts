Structure de la base de données
============================

Le projet utilise MySQL comme système de gestion de base de données.

Tables principales
-----------------

.. list-table::
   :header-rows: 1

   * - Nom de la table
     - Description
   * - stations
     - Stocke les informations sur les stations météo
   * - releves
     - Enregistre les relevés météorologiques
   * - alertes
     - Contient les alertes météo actives

Structure détaillée
-----------------

Table `stations`:

.. list-table::
   :header-rows: 1

   * - Champ
     - Type
     - Description
   * - id
     - INT (PK)
     - Identifiant unique de la station
   * - nom
     - VARCHAR(100)
     - Nom de la station météo
   * - latitude
     - DECIMAL
     - Coordonnée de latitude
   * - longitude
     - DECIMAL
     - Coordonnée de longitude
   * - altitude
     - INT
     - Altitude en mètres

Table `releves`:

.. list-table::
   :header-rows: 1

   * - Champ
     - Type
     - Description
   * - id
     - INT (PK)
     - Identifiant unique du relevé
   * - station_id
     - INT (FK)
     - Référence à la station
   * - timestamp
     - DATETIME
     - Date et heure du relevé
   * - temperature
     - DECIMAL
     - Température en degrés Celsius
   * - humidite
     - INT
     - Humidité relative en pourcentage
   * - pression
     - INT
     - Pression atmosphérique en hPa
