from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

class Regions(models.Model):
    """
    Modèle pour les régions.
    Correspond à la table Regions dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Regions'
        
    def __str__(self):
        return self.label

class Departments(models.Model):
    """
    Modèle pour les départements.
    Correspond à la table Departments dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    region = models.ForeignKey(Regions, on_delete=models.CASCADE, db_column='region')
    
    class Meta:
        db_table = 'Departments'
        
    def __str__(self):
        return self.label

class Cities(models.Model):
    """
    Modèle pour les villes.
    Correspond à la table Cities dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='department')
    
    class Meta:
        db_table = 'Cities'
        
    def __str__(self):
        return self.label

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

class TypeSky(models.Model):
    """
    Modèle pour les types de ciel.
    Correspond à la table Type_sky dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Type_sky'
        
    def __str__(self):
        return self.label

class Alert(models.Model):
    """
    Modèle pour les alertes météo.
    Correspond à la table Alerts dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    active = models.IntegerField()
    date_alert = models.DateField()
    fk_type = models.ForeignKey(TypeAlert, on_delete=models.CASCADE, db_column='fk_type')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='department')
    region = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        db_table = 'Alerts'
        
    def __str__(self):
        return f"{self.fk_type.label} - {self.department.label}"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle pour les utilisateurs personnalisés.
    Correspond à la table Users dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, db_column='city', null=True, blank=True)
    
    # Champs obligatoires pour AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Remplacer les relations ManyToMany par des champs virtuels gérés à travers la base de données
    # Les tables seront créées par Django mais ne seront pas utilisées
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'Users'
        managed = True  # Django gère cette table
        
    def __str__(self):
        return self.email

class Weather(models.Model):
    """
    Modèle pour les données météo.
    Correspond à la table Weather dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    date_weather = models.DateField()
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    pressure = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    sunrise = models.TimeField()
    sunset = models.TimeField()
    fk_type = models.ForeignKey(TypeSky, on_delete=models.CASCADE, db_column='fk_type')
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, db_column='city')
    
    class Meta:
        db_table = 'Weather'
        
    def __str__(self):
        return f"{self.city.label} - {self.date_weather}"