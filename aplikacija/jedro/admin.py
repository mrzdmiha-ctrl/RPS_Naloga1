from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Uporabnik

@admin.register(Uporabnik)
class PrilagojenUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'vloga', 'is_staff', 'is_active')
    list_filter = ('vloga', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Dodatni podatki šolskega sistema', {
            'fields': ('vloga', 'telefon', 'naslov')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dodatni podatki šolskega sistema', {
            'fields': ('first_name', 'last_name', 'email', 'vloga', 'telefon', 'naslov')
        }),
    )

