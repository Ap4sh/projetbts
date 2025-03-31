from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class Cities(models.Model):
    """
    Modèle pour les villes.
    Correspond à la table Cities dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    department = models.ForeignKey('Departments', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Cities'
        
    def __str__(self):
        return self.label

class Departments(models.Model):
    """
    Modèle pour les départements.
    Correspond à la table Departments dans la base de données.
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'Departments'
        
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
    department = models.ForeignKey('Departments', on_delete=models.CASCADE)
    region = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = 'Alerts'
        
    def __str__(self):
        return f"{self.fk_type.label} - {self.region}"

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

class CustomUser(AbstractUser):
    """
    Modèle pour les utilisateurs personnalisés.
    Correspond à la table Users dans la base de données.
    """
    email = models.EmailField(unique=True)
    city = models.ForeignKey('Cities', on_delete=models.CASCADE, null=True, blank=True)
    username = None  # Désactive le champ username car nous utilisons email
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    # Ajout des related_name pour résoudre les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        db_table = 'Users'
        
    def __str__(self):
        return self.email