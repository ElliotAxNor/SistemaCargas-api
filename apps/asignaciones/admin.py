from django.contrib import admin
from .models import Periodo, Carga, BloqueHorario


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_academica', 'finalizado', 'created_at']
    list_filter = ['finalizado', 'unidad_academica']
    search_fields = ['nombre']
    readonly_fields = ['created_at', 'updated_at']


class BloqueHorarioInline(admin.TabularInline):
    model = BloqueHorario
    extra = 1
    fields = ['dia', 'hora_inicio', 'hora_fin']


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = [
        'materia',
        'profesor',
        'programa_academico',
        'periodo',
        'estado',
        'created_at'
    ]
    list_filter = ['estado', 'periodo', 'programa_academico']
    search_fields = [
        'materia__nombre',
        'materia__clave',
        'profesor__nombre'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BloqueHorarioInline]

    fieldsets = (
        ('Información General', {
            'fields': ('programa_academico', 'materia', 'profesor', 'periodo')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BloqueHorario)
class BloqueHorarioAdmin(admin.ModelAdmin):
    list_display = ['carga', 'dia', 'hora_inicio', 'hora_fin', 'created_at']
    list_filter = ['dia', 'carga__periodo']
    search_fields = ['carga__materia__nombre', 'carga__profesor__nombre']
    readonly_fields = ['created_at', 'updated_at']
