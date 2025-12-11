from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventoViewSet, InscricaoViewSet,
    CustomAuthToken, meus_dados, minhas_inscricoes
)

app_name = 'api'

router = DefaultRouter()
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'inscricoes', InscricaoViewSet, basename='inscricao')

urlpatterns = [
    # Autenticação
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),

    # Dados do usuário
    path('me/', meus_dados, name='meus_dados'),
    path('me/inscricoes/', minhas_inscricoes, name='minhas_inscricoes'),

    # Router URLs
    path('', include(router.urls)),
]
