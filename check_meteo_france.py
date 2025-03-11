#!/usr/bin/env python
import os
import sys
import django
import logging
from datetime import datetime

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteo.settings')
django.setup()

from weather.services.weather_api import MeteoFranceVigilanceService

def main():
    """
    Script pour tester l'API Météo France Vigilance
    """
    try:
        # Clé API Météo France
        api_key = "eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzYW15dnZzQGNhcmJvbi5zdXBlciIsImFwcGxpY2F0aW9uIjp7Im93bmVyIjoic2FteXZ2cyIsInRpZXJRdW90YVR5cGUiOm51bGwsInRpZXIiOiJVbmxpbWl0ZWQiLCJuYW1lIjoiRGVmYXVsdEFwcGxpY2F0aW9uIiwiaWQiOjI1Mzc2LCJ1dWlkIjoiMDUyMjEwOGItNzhmMi00NzY4LTk2YTEtZmMyZDJjMTE5NTU4In0sImlzcyI6Imh0dHBzOlwvXC9wb3J0YWlsLWFwaS5tZXRlb2ZyYW5jZS5mcjo0NDNcL29hdXRoMlwvdG9rZW4iLCJ0aWVySW5mbyI6eyI2MFJlcVBhck1pbiI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNWaWdpbGFuY2UiLCJjb250ZXh0IjoiXC9wdWJsaWNcL0RQVmlnaWxhbmNlXC92MSIsInB1Ymxpc2hlciI6ImFkbWluIiwidmVyc2lvbiI6InYxIiwic3Vic2NyaXB0aW9uVGllciI6IjYwUmVxUGFyTWluIn1dLCJleHAiOjE4MzYzNTc4NjMsInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3NDE2ODUwNjMsImp0aSI6IjQ5YTAzMTJmLTUyNjctNDRmNC1iNGYxLWI5YTFlZjY4N2Y4ZiJ9.i5QWxDyyQXgN8JbqYGDpDxdZXVld4mBoFtfVGfKquyboPp02lpT7huL6DJmh0Y4yMr6UmRVBTTB5rd1McC_oxBbk-uEBiLxXggMh23OkhtjjUzxbYkiktWWiVf5WTHPYvRHcXLxyxcd6freSL2XvTCIFyc41dTJK0a5YpZzlGfw6-UIQgxFHgx7vXBZmDkmthw1TrdFZRDWWyIs8Zyy6aEubdmHaJPI4s7G3l0mrQE4KyAsqwSrnCxWwVTWMD-XCbtcUdVYe6Ey3Vkr-3t3lUCH0zsAXOvfBvKP1n53pMzVOU-A5N33dSiCtq-xJ4vd9su1vchGDK1MO40CVWx_E8w=="
        
        # Créer une instance du service
        vigilance_service = MeteoFranceVigilanceService(api_key)
        
        # Récupérer les alertes
        logger.info("Récupération des alertes de vigilance...")
        alerts = vigilance_service.get_vigilance_alerts()
        
        # Afficher les alertes
        if alerts:
            logger.info(f"Nombre d'alertes récupérées: {len(alerts)}")
            for i, alert in enumerate(alerts, 1):
                logger.info(f"Alerte {i}:")
                for key, value in alert.items():
                    if key == 'date_alert' and value:
                        # Vérifier le type de date_alert
                        if isinstance(value, (datetime, str)):
                            logger.info(f"  {key}: {value} (type: {type(value).__name__})")
                        else:
                            logger.info(f"  {key}: {value} (type: {type(value).__name__}) - ATTENTION: type non géré")
                    else:
                        logger.info(f"  {key}: {value}")
                logger.info("-" * 50)
        else:
            logger.warning("Aucune alerte récupérée.")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 