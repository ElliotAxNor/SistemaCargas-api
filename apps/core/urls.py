"""
URLs para el módulo Core.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnidadAcademicaViewSet, ProgramaAcademicoViewSet, UsuarioViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'unidades-academicas', UnidadAcademicaViewSet, basename='unidadacademica')
router.register(r'programas-academicos', ProgramaAcademicoViewSet, basename='programaacademico')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]
