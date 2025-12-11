from django.urls import path
from . import views

urlpatterns = [
    path('emitir/<int:inscricao_id>/', views.emitir_certificado, name='emitir_certificado'),
    path('validar/', views.validar_certificado, name='validar_certificado'),
    path('meus/', views.meus_certificados, name='meus_certificados'),
    path('visualizar/<int:certificado_id>/', views.visualizar_certificado, name='visualizar_certificado'),
]