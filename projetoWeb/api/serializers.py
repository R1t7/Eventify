from rest_framework import serializers
from eventos.models import Evento, Inscricao
from usuarios.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para informações básicas do usuário"""
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'perfil', 'instituicao_ensino']
        read_only_fields = fields


class EventoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de eventos"""
    organizador_nome = serializers.CharField(source='organizador.get_full_name', read_only=True)
    professor_responsavel_nome = serializers.CharField(source='professor_responsavel.get_full_name', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vagas_disponiveis = serializers.IntegerField(read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'descricao',
            'data_inicio', 'data_fim', 'horario', 'local',
            'vagas', 'vagas_disponiveis', 'status', 'status_display',
            'organizador_nome', 'professor_responsavel_nome', 'banner'
        ]
        read_only_fields = fields


class EventoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes completos do evento"""
    organizador = UsuarioSerializer(read_only=True)
    professor_responsavel = UsuarioSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vagas_disponiveis = serializers.IntegerField(read_only=True)
    total_inscritos = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'descricao',
            'data_inicio', 'data_fim', 'horario', 'local',
            'vagas', 'vagas_disponiveis', 'total_inscritos',
            'status', 'status_display', 'organizador',
            'professor_responsavel', 'banner', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = fields

    def get_total_inscritos(self, obj):
        return obj.inscricoes.filter(status='CONFIRMADA').count()


class InscricaoSerializer(serializers.ModelSerializer):
    """Serializer para inscrições"""
    evento = EventoListSerializer(read_only=True)
    evento_id = serializers.IntegerField(write_only=True)
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = Inscricao
        fields = ['id', 'evento', 'evento_id', 'usuario_nome', 'data_inscricao', 'status']
        read_only_fields = ['id', 'usuario_nome', 'data_inscricao', 'status']

    def validate_evento_id(self, value):
        """Valida se o evento existe"""
        try:
            Evento.objects.get(id=value)
        except Evento.DoesNotExist:
            raise serializers.ValidationError('Evento não encontrado.')
        return value

    def validate(self, attrs):
        """Validações da inscrição"""
        request = self.context.get('request')
        usuario = request.user
        evento_id = attrs.get('evento_id')

        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            raise serializers.ValidationError({'evento_id': 'Evento não encontrado.'})

        # Verifica se o usuário é organizador
        if usuario.is_organizador():
            raise serializers.ValidationError('Organizadores não podem se inscrever em eventos.')

        # Verifica se já está inscrito
        if Inscricao.objects.filter(usuario=usuario, evento=evento, status='CONFIRMADA').exists():
            raise serializers.ValidationError('Você já está inscrito neste evento.')

        # Verifica se há vagas disponíveis
        if evento.vagas_disponiveis <= 0:
            raise serializers.ValidationError('Não há vagas disponíveis para este evento.')

        # Verifica se o evento está aberto
        if evento.status != 'ABERTO':
            raise serializers.ValidationError('Este evento não está aberto para inscrições.')

        return attrs

    def create(self, validated_data):
        """Cria uma nova inscrição"""
        request = self.context.get('request')
        evento_id = validated_data.pop('evento_id')
        evento = Evento.objects.get(id=evento_id)

        inscricao = Inscricao.objects.create(
            usuario=request.user,
            evento=evento,
            status='CONFIRMADA'
        )

        return inscricao
