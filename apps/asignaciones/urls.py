"""
URLs para el módulo Asignaciones.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeriodoViewSet, CargaViewSet, BloqueHorarioViewSet

app_name = 'asignaciones'

router = DefaultRouter()
router.register(r'periodos', PeriodoViewSet, basename='periodo')
router.register(r'cargas', CargaViewSet, basename='carga')
router.register(r'bloques-horarios', BloqueHorarioViewSet, basename='bloquehorario')

urlpatterns = [
    path('', include(router.urls)),
]
