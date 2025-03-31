#!/usr/bin/env python
import os
import django
import sys
from django.db import connection, ProgrammingError
import time

# Configurer l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

print("=== Script de réparation de la base de données ===")

# Attendre que la connexion à la base de données soit établie
max_retries = 5
retry_count = 0
connected = False

while not connected and retry_count < max_retries:
    try:
        connection.ensure_connection()
        connected = True
        print("Connexion à la base de données établie.")
    except Exception as e:
        retry_count += 1
        wait_time = retry_count * 2
        print(f"Tentative {retry_count}/{max_retries} échouée: {e}")
        print(f"Nouvelle tentative dans {wait_time} secondes...")
        time.sleep(wait_time)

if not connected:
    print("Impossible de se connecter à la base de données après plusieurs tentatives.")
    sys.exit(1)

try:
    # Obtenir un curseur pour les opérations SQL directes
    cursor = connection.cursor()
    
    # 1. Vérifier les tables existantes
    print("Vérification des tables existantes...")
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables trouvées: {', '.join(tables) if tables else 'Aucune'}")
    
    # 2. Supprimer les tables de migrations si elles existent
    migration_tables = ['django_migrations', 'django_admin_log', 'django_session']
    for table in migration_tables:
        if table in tables:
            print(f"Suppression de la table {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # 3. Ajouter les colonnes manquantes à la table Users
    print("Vérification de la structure de la table Users...")
    try:
        cursor.execute("DESCRIBE Users")
        columns = {}
        for col in cursor.fetchall():
            columns[col[0]] = {
                'type': col[1],
                'null': col[2] == 'YES',
                'key': col[3],
                'default': col[4],
                'extra': col[5]
            }
        
        required_columns = {
            "is_active": "ALTER TABLE Users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1",
            "is_staff": "ALTER TABLE Users ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0",
            "is_superuser": "ALTER TABLE Users ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0",
            "last_login": "ALTER TABLE Users ADD COLUMN last_login DATETIME NULL",
            "date_joined": "ALTER TABLE Users ADD COLUMN date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
        }
        
        # Vérifier et ajouter les colonnes manquantes
        for col_name, sql in required_columns.items():
            if col_name not in columns:
                print(f"Ajout de la colonne {col_name} à la table Users...")
                cursor.execute(sql)
        
        # Vérifier le type de colonne password
        if 'password' in columns:
            password_type = columns['password']['type']
            if not (password_type.startswith('varchar') or password_type.startswith('char')):
                print(f"Correction du type de la colonne password (actuel: {password_type})...")
                cursor.execute("ALTER TABLE Users MODIFY COLUMN password VARCHAR(255) NOT NULL")
        
        # Vérifier si email est unique
        if 'email' in columns and columns['email']['key'] != 'UNI':
            print("Modification de la colonne email pour la rendre unique...")
            cursor.execute("ALTER TABLE Users ADD UNIQUE (email)")
            
    except ProgrammingError:
        print("La table Users n'a pas été trouvée. Elle sera créée lors des migrations.")
    
    # 4. Ajouter la colonne region à la table Alerts si nécessaire
    print("Vérification de la structure de la table Alerts...")
    try:
        cursor.execute("DESCRIBE Alerts")
        columns = [col[0] for col in cursor.fetchall()]
        
        if "region" not in columns:
            print("Ajout de la colonne 'region' à la table Alerts...")
            cursor.execute("ALTER TABLE Alerts ADD COLUMN region VARCHAR(100) NULL")
    except ProgrammingError:
        print("La table Alerts n'a pas été trouvée. Elle sera créée lors des migrations.")
    
    # 5. Créer les tables manquantes pour Django
    print("Création des tables requises pour l'authentification Django...")
    django_tables = {
        "django_content_type": """
            CREATE TABLE IF NOT EXISTS django_content_type (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            )
        """,
        "auth_permission": """
            CREATE TABLE IF NOT EXISTS auth_permission (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content_type_id INT NOT NULL,
                codename VARCHAR(100) NOT NULL,
                CONSTRAINT fk_content_type FOREIGN KEY (content_type_id) REFERENCES django_content_type (id) ON DELETE CASCADE,
                UNIQUE(content_type_id, codename)
            )
        """,
        "auth_group": """
            CREATE TABLE IF NOT EXISTS auth_group (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL UNIQUE
            )
        """,
        "auth_group_permissions": """
            CREATE TABLE IF NOT EXISTS auth_group_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT NOT NULL,
                permission_id INT NOT NULL,
                CONSTRAINT fk_auth_group FOREIGN KEY (group_id) REFERENCES auth_group (id) ON DELETE CASCADE,
                CONSTRAINT fk_auth_permission FOREIGN KEY (permission_id) REFERENCES auth_permission (id) ON DELETE CASCADE,
                UNIQUE(group_id, permission_id)
            )
        """,
        "Users_groups": """
            CREATE TABLE IF NOT EXISTS Users_groups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customuser_id INT NOT NULL,
                group_id INT NOT NULL,
                CONSTRAINT fk_user_id FOREIGN KEY (customuser_id) REFERENCES Users (id) ON DELETE CASCADE,
                CONSTRAINT fk_group_id FOREIGN KEY (group_id) REFERENCES auth_group (id) ON DELETE CASCADE,
                UNIQUE(customuser_id, group_id)
            )
        """,
        "Users_user_permissions": """
            CREATE TABLE IF NOT EXISTS Users_user_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customuser_id INT NOT NULL,
                permission_id INT NOT NULL,
                CONSTRAINT fk_user_perm_id FOREIGN KEY (customuser_id) REFERENCES Users (id) ON DELETE CASCADE,
                CONSTRAINT fk_perm_id FOREIGN KEY (permission_id) REFERENCES auth_permission (id) ON DELETE CASCADE,
                UNIQUE(customuser_id, permission_id)
            )
        """,
        "django_migrations": """
            CREATE TABLE IF NOT EXISTS django_migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied DATETIME NOT NULL,
                INDEX(applied)
            )
        """,
        "django_session": """
            CREATE TABLE IF NOT EXISTS django_session (
                session_key VARCHAR(40) NOT NULL PRIMARY KEY,
                session_data LONGTEXT NOT NULL,
                expire_date DATETIME NOT NULL,
                INDEX(expire_date)
            )
        """
    }
    
    for table_name, sql in django_tables.items():
        if table_name not in tables:
            print(f"Création de la table {table_name}...")
            cursor.execute(sql)
    
    # 6. Remplir la table django_content_type
    print("Préparation des données pour l'authentification Django...")
    content_types = [
        ("admin", "logentry"),
        ("auth", "permission"),
        ("auth", "group"),
        ("contenttypes", "contenttype"),
        ("sessions", "session"),
        ("weather", "regions"),
        ("weather", "departments"),
        ("weather", "cities"),
        ("weather", "typealert"),
        ("weather", "typesky"),
        ("weather", "alert"),
        ("weather", "customuser"),
        ("weather", "weather")
    ]
    
    # Vérifier si la table django_content_type existe
    if "django_content_type" in tables:
        for app_label, model in content_types:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO django_content_type (app_label, model) VALUES (%s, %s)",
                    [app_label, model]
                )
            except Exception as e:
                print(f"Erreur lors de l'insertion du content type {app_label}.{model}: {e}")
    
    # 7. Créer une migration factice pour indiquer que les migrations sont appliquées
    if "django_migrations" in tables:
        try:
            # Insérer des migrations factices
            migrations = [
                ("contenttypes", "0001_initial"),
                ("auth", "0001_initial"),
                ("weather", "0001_initial"),
                ("admin", "0001_initial"),
                ("sessions", "0001_initial")
            ]
            
            for app, name in migrations:
                cursor.execute(
                    "INSERT IGNORE INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                    [app, name]
                )
        except Exception as e:
            print(f"Erreur lors de l'insertion des migrations factices: {e}")
    
    # 8. Commit des modifications
    connection.commit()
    print("Toutes les modifications ont été appliquées avec succès.")
    
except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
finally:
    # Fermer la connexion à la base de données
    connection.close()

print("=== Script terminé ===") 