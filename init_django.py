#!/usr/bin/env python
import os
import django
import sys
import MySQLdb

# Configurer l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

print("Initialisation de l'environnement Django...")

# Obtenir les informations de connexion à la base de données depuis settings
from django.conf import settings
db_settings = settings.DATABASES['default']

try:
    # Se connecter à MySQL
    print("Connexion à la base de données MySQL...")
    db = MySQLdb.connect(
        host=db_settings.get('HOST', 'localhost'),
        user=db_settings.get('USER', 'root'),
        passwd=db_settings.get('PASSWORD', ''),
        db=db_settings.get('NAME', 'meteo')
    )
    cursor = db.cursor()
    print("Connexion réussie.")
    
    print("Vérification de la structure de la table Users...")
    
    # Vérifier si la table Users a les colonnes nécessaires pour AuthBaseUser
    cursor.execute("SHOW TABLES LIKE 'Users'")
    if cursor.fetchone():
        cursor.execute("DESCRIBE Users")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # Ajouter les colonnes requises si elles n'existent pas
        missing_columns = []
        required_columns = [
            "is_active", "is_staff", "is_superuser", "last_login", "date_joined"
        ]
        
        for column in required_columns:
            if column not in column_names:
                missing_columns.append(column)
        
        if missing_columns:
            print(f"Ajout des colonnes manquantes à la table Users: {', '.join(missing_columns)}")
            for column in missing_columns:
                if column == 'is_active':
                    cursor.execute("ALTER TABLE Users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1")
                elif column == 'is_staff':
                    cursor.execute("ALTER TABLE Users ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0")
                elif column == 'is_superuser':
                    cursor.execute("ALTER TABLE Users ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0")
                elif column == 'last_login':
                    cursor.execute("ALTER TABLE Users ADD COLUMN last_login DATETIME NULL")
                elif column == 'date_joined':
                    cursor.execute("ALTER TABLE Users ADD COLUMN date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
        else:
            print("La table Users possède déjà toutes les colonnes requises.")
    else:
        print("La table Users n'existe pas encore, elle sera créée par Django.")
    
    # Création des tables ManyToMany pour les permissions
    print("Vérification des tables de liaison ManyToMany...")
    
    # Tables nécessaires pour PermissionsMixin
    required_tables = [
        "Users_groups", 
        "Users_user_permissions", 
        "auth_group", 
        "auth_group_permissions", 
        "auth_permission", 
        "django_content_type"
    ]
    
    for table in required_tables:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        if not cursor.fetchone():
            print(f"La table {table} n'existe pas, elle sera créée par Django.")
    
    print("Vérification de la table Alerts...")
    cursor.execute("SHOW TABLES LIKE 'Alerts'")
    if cursor.fetchone():
        cursor.execute("DESCRIBE Alerts")
        alert_columns = cursor.fetchall()
        alert_column_names = [col[0] for col in alert_columns]
        
        if 'region' not in alert_column_names:
            print("Ajout de la colonne 'region' à la table Alerts")
            cursor.execute("ALTER TABLE Alerts ADD COLUMN region VARCHAR(100) NULL")
        else:
            print("La table Alerts possède déjà la colonne 'region'.")
    
    # Committer les changements
    db.commit()
    print("Toutes les modifications ont été appliquées avec succès.")
    
except MySQLdb.Error as e:
    print(f"Erreur MySQL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
finally:
    if 'db' in locals() and db.open:
        db.close()
        print("Connexion à la base de données fermée.")

print("Initialisation terminée.") 