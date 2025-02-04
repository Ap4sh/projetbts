from django.contrib import admin
from .models import TypeAlert, Alert, UserProfile


# add les outils pour les admins même si je pense qu'on les utilisera pas (lié à la db)
@admin.register(TypeAlert)
class TypeAlertAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('type_alert', 'region', 'date_debut', 'date_fin')
    list_filter = ('type_alert', 'region')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'region', 'ville')
    search_fields = ('user__username', 'region', 'ville') 

