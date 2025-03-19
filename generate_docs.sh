#!/bin/bash

# Titre du script
echo "====================================================="
echo "      Générateur de documentation du projet météo"
echo "====================================================="

# Vérifier si Docker est en marche
echo -e "\n🔍 Vérification de Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "⚠️ Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
    exit 1
fi

# Créer un conteneur temporaire dédié à la documentation
echo -e "\n🐳 Création d'un conteneur dédié à la documentation..."
docker run --name doc-generator -d -v "$(pwd):/app" python:3.11-slim tail -f /dev/null

# Créer les répertoires pour la documentation
echo -e "\n📁 Création de la structure de documentation..."
mkdir -p docs/source/_static
mkdir -p docs/build/html

# Installer les dépendances minimales
echo -e "\n📦 Installation des dépendances Python minimales..."
docker exec doc-generator pip install sphinx sphinx-rtd-theme

# Créer le fichier de configuration pour Sphinx
echo -e "\n⚙️ Configuration de Sphinx..."
cat > docs/source/conf.py << EOF
# Configuration file for the Sphinx documentation builder
import os
import sys

# Configuration générale
project = 'Projet Météo BTS'
copyright = '2023, Équipe'
author = 'Équipe'

# Extensions
extensions = [
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# Thème
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'display_version': True,
}
EOF

# Créer page d'index avec sections
echo -e "\n📝 Création de la page d'index..."
cat > docs/source/index.rst << EOF
Documentation du Projet Météo BTS
================================

Cette documentation présente le fonctionnement et l'utilisation du projet météo BTS.

.. toctree::
   :maxdepth: 2
   :caption: Documentation utilisateur:

   installation
   usage
   api
   docker

.. toctree::
   :maxdepth: 2
   :caption: Documentation technique:

   architecture
   database
   developpement
   python_modules

Indices et tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
EOF

# Créer page d'architecture
echo -e "\n📊 Création de la page d'architecture..."
cat > docs/source/architecture.rst << EOF
Architecture du projet
=====================

Structure du projet
------------------

Le projet est organisé comme suit:

.. code-block:: text

   $(find . -type f -not -path "*/\.*" -not -path "*/docs/*" -not -path "*/__pycache__/*" | grep -v "generate_docs.sh" | sort | head -n 20)
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
EOF

# Créer page d'installation
echo -e "\n🔧 Création de la page d'installation..."
cat > docs/source/installation.rst << EOF
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

Les paramètres de configuration sont définis dans le fichier \`.env\` à la racine du projet.
EOF

# Créer page d'utilisation
echo -e "\n📖 Création de la page d'utilisation..."
cat > docs/source/usage.rst << EOF
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

* \`/api/meteo/\` - Données météo actuelles
* \`/api/alertes/\` - Alertes météo actives

Exemples d'utilisation
-------------------

Récupération des données météo actuelles:

.. code-block:: bash

   curl http://localhost:8000/api/meteo/

Récupération des alertes:

.. code-block:: bash

   curl http://localhost:8000/api/alertes/
EOF

# Créer page d'API
echo -e "\n🔌 Génération de la documentation de l'API..."
cat > docs/source/api.rst << EOF
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
EOF

# Créer page de documentation de la base de données
echo -e "\n💾 Création de la documentation de la base de données..."
cat > docs/source/database.rst << EOF
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

Table \`stations\`:

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

Table \`releves\`:

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
EOF

# Créer page Docker
echo -e "\n🐳 Création de la documentation Docker..."
cat > docs/source/docker.rst << EOF
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

* \`start.sh\` - Démarrage complet de l'application
* \`fix_migrations.sh\` - Résolution des conflits de migrations Django
EOF

# Créer page développement
echo -e "\n👨‍💻 Création de la documentation de développement..."
cat > docs/source/developpement.rst << EOF
Guide de développement
====================

Installation pour le développement
-------------------------------

1. Cloner le dépôt:

   .. code-block:: bash

      git clone <URL_DU_DEPOT>
      cd projetbts

2. Lancer l'environnement de développement:

   .. code-block:: bash

      ./start.sh

Workflow de développement
----------------------

1. Créer une branche pour votre fonctionnalité:

   .. code-block:: bash

      git checkout -b feature/nom-de-la-fonctionnalite

2. Implémenter les changements nécessaires

3. Tester localement:

   .. code-block:: bash

      docker-compose exec web python manage.py test

4. Soumettre une pull request vers la branche principale

Guidelines de code
---------------

* Suivre les conventions PEP 8 pour le code Python
* Documenter les fonctions et classes avec des docstrings (format Google ou NumPy)
* Écrire des tests unitaires pour les nouvelles fonctionnalités

Format des docstrings
-----------------

Utilisez le format Google pour les docstrings:

.. code-block:: python

   def ma_fonction(param1, param2):
       """Description de la fonction.
       
       Args:
           param1 (type): Description du paramètre 1.
           param2 (type): Description du paramètre 2.
           
       Returns:
           type: Description de la valeur de retour.
           
       Raises:
           Exception: Description des exceptions possibles.
       """
       # Code de la fonction
EOF

# Créer un script Python pour extraire manuellement les docstrings
echo -e "\n🔍 Création d'un script pour extraire les docstrings..."
cat > extract_manual.py << EOF
#!/usr/bin/env python
import os
import re
from pathlib import Path

def extract_class_docstrings(content):
    """Extrait les docstrings des classes à partir du contenu."""
    class_pattern = r'class\s+(\w+).*?:\s*(\'\'\'|\"\"\")(.+?)(\'\'\'|\"\"\")'
    matches = re.finditer(class_pattern, content, re.DOTALL)
    
    results = {}
    for match in matches:
        class_name = match.group(1)
        docstring = match.group(3).strip()
        results[class_name] = docstring
    
    return results

def extract_function_docstrings(content):
    """Extrait les docstrings des fonctions à partir du contenu."""
    function_pattern = r'def\s+(\w+)\s*\(.*?\).*?:\s*(\'\'\'|\"\"\")(.+?)(\'\'\'|\"\"\")'
    matches = re.finditer(function_pattern, content, re.DOTALL)
    
    results = {}
    for match in matches:
        function_name = match.group(1)
        docstring = match.group(3).strip()
        results[function_name] = docstring
    
    return results

def main():
    # Contenu du fichier weather_api.py
    weather_api_content = """${cat /app/weather/services/weather_api.py 2>/dev/null || echo "Fichier non trouvé"}"""
    
    classes = extract_class_docstrings(weather_api_content)
    functions = extract_function_docstrings(weather_api_content)
    
    output_dir = "/app/docs/source"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/python_modules.rst", "w") as f:
        f.write("Modules Python\n")
        f.write("=============\n\n")
        
        f.write("Services météo\n")
        f.write("-------------\n\n")
        
        # Classes du module weather_api
        for class_name, docstring in classes.items():
            f.write(f"{class_name}\n")
            f.write("~" * len(class_name) + "\n\n")
            f.write(f"{docstring}\n\n")
            
            f.write("Méthodes:\n\n")
            
            # Trouver les méthodes de cette classe
            method_pattern = fr'def\s+(\w+)\s*\(self(?:,\s*.*?)?\).*?:\s*(\'\'\'|\"\"\")(.+?)(\'\'\'|\"\"\")'
            class_content = re.search(fr'class\s+{class_name}.*?:(.*?)(?:class|\Z)', weather_api_content, re.DOTALL)
            
            if class_content:
                methods = re.finditer(method_pattern, class_content.group(1), re.DOTALL)
                for method in methods:
                    method_name = method.group(1)
                    method_doc = method.group(3).strip()
                    
                    f.write(f"**{method_name}**\n\n")
                    f.write(f"{method_doc}\n\n")
        
        # Fonctions du module au niveau supérieur
        f.write("Fonctions utilitaires\n")
        f.write("-------------------\n\n")
        
        for func_name, docstring in functions.items():
            if not func_name.startswith('_'):  # Ignorer les fonctions privées
                f.write(f"**{func_name}**\n\n")
                f.write(f"{docstring}\n\n")

if __name__ == "__main__":
    main()
EOF

# Exécuter le script d'extraction
echo -e "\n🔍 Extraction manuelle des docstrings..."
docker exec -T doc-generator bash -c "cat > /app/extract_manual.py" < extract_manual.py
docker exec doc-generator python /app/extract_manual.py

# Générer la documentation avec Sphinx
echo -e "\n🚀 Génération de la documentation avec Sphinx..."
docker exec -w /app/docs/source doc-generator sphinx-build -b html . ../build/html

# Nettoyer
echo -e "\n🧹 Nettoyage..."
docker stop doc-generator
docker rm doc-generator
rm extract_manual.py

# Finalisation
echo -e "\n✅ Documentation générée avec succès !"
echo "La documentation HTML est disponible dans le répertoire: docs/build/html/"
echo "Ouvrez le fichier index.html dans votre navigateur pour consulter la documentation."
echo "====================================================="

# Proposer d'ouvrir la documentation
read -p "Voulez-vous ouvrir la documentation dans votre navigateur ? (o/n) : " ouvrir_doc
if [[ "$ouvrir_doc" == "o" || "$ouvrir_doc" == "O" ]]; then
    if command -v xdg-open > /dev/null; then
        xdg-open docs/build/html/index.html
    elif command -v open > /dev/null; then
        open docs/build/html/index.html
    else
        echo "Impossible d'ouvrir automatiquement. Veuillez ouvrir manuellement le fichier:"
        echo "docs/build/html/index.html"
    fi
fi 