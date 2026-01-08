from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UnidadAcademica, ProgramaAcademico, Usuario


@admin.register(UnidadAcademica)
class UnidadAcademicaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'created_at']
    search_fields = ['nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProgramaAcademico)
class ProgramaAcademicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_academica', 'created_at']
    list_filter = ['unidad_academica']
    search_fields = ['nombre', 'unidad_academica__nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Información del Sistema', {
            'fields': ('rol', 'unidad_academica', 'programa_academico')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Sistema', {
            'fields': ('rol', 'unidad_academica', 'programa_academico')
        }),
    )
