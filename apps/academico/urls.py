"""
URLs para el módulo Académico.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfesorViewSet, MateriaViewSet

app_name = 'academico'

router = DefaultRouter()
router.register(r'profesores', ProfesorViewSet, basename='profesor')
router.register(r'materias', MateriaViewSet, basename='materia')

urlpatterns = [
    path('', include(router.urls)),
]
