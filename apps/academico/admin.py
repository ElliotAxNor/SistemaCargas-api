from django.contrib import admin
from .models import Profesor, Materia


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'unidad_academica', 'created_at']
    list_filter = ['unidad_academica']
    search_fields = ['nombre', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'horas', 'programa_academico', 'created_at']
    list_filter = ['programa_academico', 'horas']
    search_fields = ['clave', 'nombre']
    readonly_fields = ['created_at', 'updated_at']
