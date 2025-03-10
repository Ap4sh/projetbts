import requests
import json

def check_meteo_france_alerts():
    """
    Vérifie s'il y a des alertes météo en cours sur le site de Météo France
    """
    print("Vérification des alertes météo sur Météo France...")
    
    # URL de l'API de vigilance Météo-France (format JSON)
    vigilance_url = "https://vigilance.meteofrance.fr/fr/carte-de-vigilance.json"
    
    try:
        # Récupérer les données de vigilance
        response = requests.get(vigilance_url, timeout=10)
        response.raise_for_status()
        
        # Analyser le JSON
        data = response.json()
        
        # Vérifier si les données contiennent les informations de vigilance
        if 'meta' not in data or 'update_time' not in data['meta']:
            print("Format de données inattendu dans la réponse de Météo-France")
            return
        
        # Date de mise à jour des données
        update_time = data['meta']['update_time']
        print(f"Données de vigilance mises à jour le : {update_time}")
        
        # Dictionnaire pour mapper les niveaux de vigilance aux types d'alertes
        vigilance_levels = {
            "1": "Vert - Pas de vigilance particulière",
            "2": "Jaune - Soyez attentif",
            "3": "Orange - Soyez très vigilant",
            "4": "Rouge - Vigilance absolue"
        }
        
        # Dictionnaire pour mapper les phénomènes aux types d'alertes
        phenomena_types = {
            "1": "Vent violent",
            "2": "Pluie-inondation",
            "3": "Orages",
            "4": "Crues",
            "5": "Neige-verglas",
            "6": "Canicule",
            "7": "Grand froid",
            "8": "Avalanches",
            "9": "Vagues-submersion"
        }
        
        # Parcourir les données de vigilance des départements
        alerts_count = 0
        
        if 'data' in data and 'departments' in data['data']:
            for dept in data['data']['departments']:
                dept_id = dept.get('department_code')
                dept_name = dept.get('department_name')
                vigilance_level = dept.get('vigilance_level')
                
                # Ne traiter que les alertes orange (3) ou rouge (4)
                if vigilance_level in ["3", "4"]:
                    vigilance_type = vigilance_levels.get(vigilance_level, "Alerte météo")
                    
                    # Parcourir les phénomènes pour ce département
                    phenomena = dept.get('phenomenons_items', [])
                    for phenomenon in phenomena:
                        phenomenon_id = phenomenon.get('phenomenon_id')
                        phenomenon_level = phenomenon.get('phenomenon_max_level')
                        
                        # Ne traiter que les phénomènes en alerte orange ou rouge
                        if phenomenon_level in ["3", "4"] and phenomenon_id in phenomena_types:
                            phenomenon_type = phenomena_types[phenomenon_id]
                            
                            # Afficher l'alerte
                            print(f"ALERTE: {vigilance_type} - {phenomenon_type} dans le département {dept_name} ({dept_id})")
                            alerts_count += 1
        
        if alerts_count == 0:
            print("Aucune alerte météo trouvée. Tous les départements sont en vigilance verte ou jaune.")
        else:
            print(f"{alerts_count} alertes météo trouvées.")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données de vigilance: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"Erreur lors de l'analyse du JSON: {str(e)}")
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    check_meteo_france_alerts() 