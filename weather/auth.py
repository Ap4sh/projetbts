from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
import hashlib

class EmailBackend(ModelBackend):
    """
    Authentifie en utilisant l'email au lieu du nom d'utilisateur.
    Gère le cas où les champs Django standard ne sont pas dans la table Users.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # On importe ici pour éviter l'importation circulaire
            from .models import CustomUser
            
            # Vérifie si l'utilisateur existe avec cet email
            user = CustomUser.objects.get(Q(email__iexact=username))
            
            # Vérifie le mot de passe
            if user.check_password(password):
                return user
                
        except CustomUser.DoesNotExist:
            # Renvoie None si l'utilisateur n'existe pas
            print(f"Utilisateur non trouvé: {username}")
            return None
        except Exception as e:
            # Log l'erreur en cas de problème
            print(f"Erreur d'authentification: {e}")
            return None
            
    def get_user(self, user_id):
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(pk=user_id)
            # S'assurer que l'utilisateur a un backend défini
            if not hasattr(user, 'backend'):
                user.backend = 'weather.auth.EmailBackend'
            return user
        except CustomUser.DoesNotExist:
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None 