from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    path('logs/', views.listar_logs, name='listar_logs'),
    path('logs/usuario/<int:usuario_id>/', views.logs_usuario, name='logs_usuario'),
    path('logs/data/<str:data>/', views.logs_data, name='logs_data'),
]
