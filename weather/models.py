from django.db import models
from django.contrib.auth.models import User

class TypeAlert(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.nom

class Alert(models.Model):
    type_alert = models.ForeignKey(TypeAlert, on_delete=models.CASCADE)
    region = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.type_alert.nom} - {self.region}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    notifications_actives = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username