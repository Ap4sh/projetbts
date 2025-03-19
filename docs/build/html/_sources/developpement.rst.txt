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
