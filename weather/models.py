from django.db import models
from django.contrib.auth.models import User

class TypeAlert(models.Model):
    """
    Modèle pour les types d'alertes météo.
    Correspond à la table Type_alert dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Type_alert'
        
    def __str__(self):
        return self.label

class Alert(models.Model):
    """
    Modèle pour les alertes météo.
    Correspond à la table Alerts dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    fk_type = models.ForeignKey(TypeAlert, on_delete=models.CASCADE, db_column='fk_type')
    region = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    active = models.IntegerField(default=1)
    date_alert = models.DateField()
    
    class Meta:
        db_table = 'Alerts'
        
    def __str__(self):
        return f"{self.fk_type.label} - {self.region}"

class CustomUser(models.Model):
    """
    Modèle pour les utilisateurs personnalisés.
    Correspond à la table Users dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Users'
        
    def __str__(self):
        return self.email