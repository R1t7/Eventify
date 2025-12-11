from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.db.models import Q

from eventos.models import Evento, Inscricao
from auditoria.models import LogAuditoria
from .serializers import (
    EventoListSerializer, EventoDetailSerializer,
    InscricaoSerializer, UsuarioSerializer
)
from .throttling import EventosConsultaThrottle, EventosInscricaoThrottle


class CustomAuthToken(ObtainAuthToken):
    """View customizada para autenticação e obtenção de token"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'erro': 'Username e password são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'erro': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verifica se o email foi confirmado
        if not user.email_confirmado:
            return Response(
                {'erro': 'Email não confirmado. Verifique seu email para ativar sua conta.'},
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(user=user)

        # Registra log de auditoria
        LogAuditoria.registrar(
            usuario=user,
            acao='CONSULTA_API_EVENTOS',
            descricao=f'Usuário autenticou na API',
            request=request
        )

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'perfil': user.perfil,
            'nome_completo': user.get_full_name()
        })


class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de eventos via API

    list: Lista todos os eventos disponíveis (20 requisições/dia)
    retrieve: Obtém detalhes de um evento específico
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [EventosConsultaThrottle]

    def get_queryset(self):
        """Retorna eventos filtrados"""
        queryset = Evento.objects.all()

        # Filtros opcionais
        tipo = self.request.query_params.get('tipo', None)
        status_evento = self.request.query_params.get('status', None)
        data_inicio = self.request.query_params.get('data_inicio', None)
        search = self.request.query_params.get('search', None)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if status_evento:
            queryset = queryset.filter(status=status_evento)

        if data_inicio:
            queryset = queryset.filter(data_inicio__gte=data_inicio)

        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descricao__icontains=search) |
                Q(local__icontains=search)
            )

        return queryset.order_by('data_inicio')

    def get_serializer_class(self):
        """Retorna o serializer apropriado"""
        if self.action == 'retrieve':
            return EventoDetailSerializer
        return EventoListSerializer

    def list(self, request, *args, **kwargs):
        """Lista eventos e registra auditoria"""
        response = super().list(request, *args, **kwargs)

        # Registra log de auditoria
        LogAuditoria.registrar(
            usuario=request.user,
            acao='CONSULTA_API_EVENTOS',
            descricao=f'Consultou lista de eventos via API',
            request=request,
            dados_adicionais={
                'total_eventos': len(response.data.get('results', [])),
                'filtros': dict(request.query_params)
            }
        )

        return response

    def retrieve(self, request, *args, **kwargs):
        """Obtém detalhes de um evento e registra auditoria"""
        response = super().retrieve(request, *args, **kwargs)

        # Registra log de auditoria
        LogAuditoria.registrar(
            usuario=request.user,
            acao='CONSULTA_API_EVENTOS',
            descricao=f'Consultou detalhes do evento ID {kwargs.get("pk")} via API',
            request=request,
            dados_adicionais={
                'evento_id': kwargs.get('pk'),
                'evento_titulo': response.data.get('titulo')
            }
        )

        return response


class InscricaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para inscrições em eventos via API

    list: Lista inscrições do usuário autenticado
    create: Cria uma nova inscrição (50 requisições/dia)
    destroy: Cancela uma inscrição
    """
    permission_classes = [IsAuthenticated]
    serializer_class = InscricaoSerializer

    def get_queryset(self):
        """Retorna apenas inscrições do usuário autenticado"""
        return Inscricao.objects.filter(
            usuario=self.request.user
        ).select_related('evento', 'usuario')

    def get_throttles(self):
        """Define throttling apenas para criação de inscrições"""
        if self.action == 'create':
            return [EventosInscricaoThrottle()]
        return []

    def create(self, request, *args, **kwargs):
        """Cria uma nova inscrição e registra auditoria"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Registra log de auditoria
        evento_id = request.data.get('evento_id')
        evento = Evento.objects.get(id=evento_id)

        LogAuditoria.registrar(
            usuario=request.user,
            acao='INSCRICAO_EVENTO',
            descricao=f'Inscreveu-se no evento "{evento.titulo}" via API',
            request=request,
            dados_adicionais={
                'evento_id': evento.id,
                'evento_titulo': evento.titulo,
                'inscricao_id': serializer.data.get('id')
            }
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'mensagem': 'Inscrição realizada com sucesso!',
                'inscricao': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """Cancela uma inscrição"""
        inscricao = self.get_object()

        # Verifica se a inscrição pertence ao usuário
        if inscricao.usuario != request.user:
            return Response(
                {'erro': 'Você não tem permissão para cancelar esta inscrição'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Atualiza o status ao invés de deletar
        inscricao.status = 'CANCELADA'
        inscricao.save()

        # Registra log de auditoria
        LogAuditoria.registrar(
            usuario=request.user,
            acao='INSCRICAO_EVENTO',
            descricao=f'Cancelou inscrição no evento "{inscricao.evento.titulo}" via API',
            request=request,
            dados_adicionais={
                'evento_id': inscricao.evento.id,
                'evento_titulo': inscricao.evento.titulo,
                'inscricao_id': inscricao.id
            }
        )

        return Response(
            {'mensagem': 'Inscrição cancelada com sucesso'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meus_dados(request):
    """Retorna dados do usuário autenticado"""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_inscricoes(request):
    """Lista todas as inscrições do usuário autenticado"""
    inscricoes = Inscricao.objects.filter(
        usuario=request.user
    ).select_related('evento')

    serializer = InscricaoSerializer(inscricoes, many=True)
    return Response(serializer.data)
