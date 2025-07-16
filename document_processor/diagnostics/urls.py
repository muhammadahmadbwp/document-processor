from django.urls import path
from . import views

urlpatterns = [
    path('', views.diagnostics_dashboard, name='diagnostics_dashboard'),
    path('connectivity_check/', views.api_connectivity_check, name='api_connectivity_check'),
]