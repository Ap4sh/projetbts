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
        
        # Créer un utilisateur sans hachage de mot de passe
        # pour correspondre à la structure de db_creation.sql
        user = self.model(email=email, **extra_fields)
        
        # Stocker le mot de passe en clair pour correspondre au schéma existant
        # Dans un environnement de production réel, on utiliserait plutôt set_password
        user.password = password
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Dans ce modèle simplifié, nous n'avons pas de superutilisateur
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle pour les utilisateurs personnalisés.
    Correspond à la table Users dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, db_column='city')
    
    # Ces champs sont nécessaires pour Django mais ne sont pas dans la table Users
    # Nous utilisons des propriétés pour les simuler
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'Users'
        managed = False  # Django ne doit pas gérer cette table
        
    def __str__(self):
        return self.email
        
    # Surcharge de la méthode check_password pour comparer directement les mots de passe
    def check_password(self, raw_password):
        # Dans db_creation.sql, les mots de passe sont stockés en clair
        # Cette méthode pourrait être modifiée selon la façon dont les mots de passe sont stockés
        return self.password == raw_password
        
    # Surcharge de la méthode set_password pour stocker le mot de passe en clair
    def set_password(self, raw_password):
        # Dans db_creation.sql, les mots de passe sont stockés en clair
        self.password = raw_password
        self._password = raw_password
        
    # Propriétés virtuelles nécessaires pour Django
    @property
    def is_active(self):
        return True
        
    @property
    def is_staff(self):
        return False
        
    @property
    def is_superuser(self):
        return False
    
    @property
    def last_login(self):
        # Retourner None pour éviter que Django n'essaie d'accéder à ce champ
        return None
    
    @last_login.setter
    def last_login(self, value):
        # Ne rien faire, car le champ n'existe pas dans la base de données
        pass

    def has_perm(self, perm, obj=None):
        return self.is_superuser
        
    def has_module_perms(self, app_label):
        return self.is_superuser

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