from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_eventos, name='listar_eventos'),
    path('criar/', views.criar_evento, name='criar_evento'),
    path('<int:pk>/', views.detalhes_evento, name='detalhes_evento'),
    path('<int:pk>/editar/', views.editar_evento, name='editar_evento'),
    path('<int:pk>/excluir/', views.excluir_evento, name='excluir_evento'),
    path('<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('minhas-inscricoes/', views.minhas_inscricoes, name='minhas_inscricoes'),
    path('inscricao/<int:inscricao_id>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),
    path('inscricao/<int:inscricao_id>/confirmar-presenca/', views.confirmar_presenca, name='confirmar_presenca'),
    path('inscricao/<int:inscricao_id>/remover-presenca/', views.remover_presenca, name='remover_presenca'),
]