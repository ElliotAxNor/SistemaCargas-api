"""
URL configuration for Sistema de Cargas Académicas.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Apps
    path('api/core/', include('apps.core.urls')),
    path('api/academico/', include('apps.academico.urls')),
    path('api/asignaciones/', include('apps.asignaciones.urls')),
]
