from django.contrib import admin
from .models import TypeAlert, Alert, CustomUser, Cities, Departments, Regions, TypeSky, Weather


# add les outils pour les admins même si je pense qu'on les utilisera pas (lié à la db)
@admin.register(TypeAlert)
class TypeAlertAdmin(admin.ModelAdmin):
    list_display = ('label',)

@admin.register(TypeSky)
class TypeSkyAdmin(admin.ModelAdmin):
    list_display = ('label',)

@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    list_display = ('label',)

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('label', 'region')
    list_filter = ('region',)

@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    list_display = ('label', 'department')
    list_filter = ('department',)
    search_fields = ('label',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('fk_type', 'department', 'date_alert', 'active')
    list_filter = ('fk_type', 'department', 'active')

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ('city', 'date_weather', 'temperature_min', 'temperature_max')
    list_filter = ('city', 'date_weather')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'city', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('city',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    ) 

