from django.contrib import admin
from .models import TypeAlert, Alert, CustomUser


# add les outils pour les admins même si je pense qu'on les utilisera pas (lié à la db)
@admin.register(TypeAlert)
class TypeAlertAdmin(admin.ModelAdmin):
    list_display = ('label',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('fk_type', 'region', 'date_alert', 'active')
    list_filter = ('fk_type', 'region', 'active')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'region', 'city')
    search_fields = ('email', 'region', 'city') 

