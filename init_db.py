#!/usr/bin/env python
import os
import sys
import MySQLdb
import argparse

def init_database(drop_tables=False):
    """Initialise la base de données en exécutant le script SQL"""
    print("=== Initialisation de la base de données ===")
    
    # Récupérer les informations de connexion depuis les variables d'environnement
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_name = os.environ.get('DB_NAME', 'meteo')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_port = int(os.environ.get('DB_PORT', 3306))
    
    try:
        # Se connecter à MySQL
        print("Connexion à la base de données MySQL...")
        db = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_password,
            db=db_name,
            port=db_port
        )
        
        # Créer un curseur pour exécuter les requêtes
        cursor = db.cursor()
        
        # Supprimer d'abord les tables existantes pour éviter les erreurs de clé primaire
        print("Suppression des tables existantes...")
        tables = [
            "Users", "Weather", "Alerts", "Cities", 
            "Departments", "Regions", "Type_sky", "Type_alert",
            "django_session"
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"Table {table} supprimée")
            except Exception as e:
                print(f"Erreur lors de la suppression de la table {table}: {e}")
                
        # Lire le fichier SQL
        print("Lecture du fichier de création de la base de données...")
        with open('db_creation.sql', 'r') as f:
            sql_script = f.read()
        
        # Diviser le script en commandes individuelles
        sql_commands = sql_script.split(';')
        
        # Exécuter chaque commande
        print("Exécution des commandes SQL...")
        for command in sql_commands:
            command = command.strip()
            if command:  # Ignorer les lignes vides
                try:
                    cursor.execute(command)
                    print(f"Exécuté: {command[:50]}...")
                except Exception as e:
                    print(f"Erreur lors de l'exécution de la commande: {e}")
        
        # Créer la table django_session nécessaire pour les sessions
        print("Création de la table django_session...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_session (
                session_key VARCHAR(40) NOT NULL PRIMARY KEY,
                session_data LONGTEXT NOT NULL,
                expire_date DATETIME NOT NULL,
                INDEX (expire_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Valider les modifications
        db.commit()
        print("Initialisation de la base de données terminée avec succès!")
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False
    finally:
        if 'db' in locals() and db:
            db.close()
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialiser la base de données pour l\'application météo')
    parser.add_argument('--drop', action='store_true', help='Supprimer les tables existantes avant de les recréer')
    args = parser.parse_args()
    
    init_database(drop_tables=args.drop) 