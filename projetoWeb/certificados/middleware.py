"""
Middleware para geração automática de certificados
Verifica eventos finalizados a cada requisição e gera certificados automaticamente
"""
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from eventos.models import Evento, Inscricao
from certificados.models import Certificado
from auditoria.models import LogAuditoria
from usuarios.email import enviar_email_certificado_disponivel
import logging

logger = logging.getLogger(__name__)


class AutoCertificadoMiddleware(MiddlewareMixin):
    """
    Middleware que verifica periodicamente se há eventos finalizados
    que precisam de certificados gerados
    """

    def process_request(self, request):
        """
        Verifica a cada 1 hora (em cache) se há certificados para gerar
        Isso evita overhead em cada requisição
        """
        # Verifica se já rodou recentemente (cache de 1 hora)
        cache_key = 'auto_certificado_check'
        if cache.get(cache_key):
            return None

        # Define cache por 1 hora
        cache.set(cache_key, True, 3600)

        # Busca eventos finalizados que ainda estão abertos
        eventos_finalizados = Evento.objects.filter(
            data_fim__lt=timezone.now().date(),
            status='ABERTO'
        )

        if not eventos_finalizados.exists():
            return None

        # Gera certificados para cada evento
        for evento in eventos_finalizados:
            self._gerar_certificados_evento(evento)

        return None

    def _gerar_certificados_evento(self, evento):
        """Gera certificados para todas as inscrições confirmadas de um evento"""
        try:
            # Busca inscrições confirmadas COM PRESENÇA sem certificado
            inscricoes = Inscricao.objects.filter(
                evento=evento,
                status='CONFIRMADA',
                presenca_confirmada=True,  # Apenas quem teve presença confirmada
                certificado__isnull=True
            ).select_related('usuario')

            if not inscricoes.exists():
                return

            certificados_gerados = 0

            for inscricao in inscricoes:
                try:
                    # Cria o certificado
                    certificado = Certificado.objects.create(
                        inscricao=inscricao
                    )

                    # Registra log de auditoria
                    LogAuditoria.registrar(
                        usuario=None,  # Sistema
                        acao='GERAR_CERTIFICADO',
                        descricao=f'Certificado gerado automaticamente para {inscricao.usuario.get_full_name()} - {evento.titulo}',
                        dados_adicionais={
                            'evento_id': evento.id,
                            'evento_titulo': evento.titulo,
                            'usuario_id': inscricao.usuario.id,
                            'certificado_id': certificado.id,
                            'codigo_validacao': str(certificado.codigo_validacao),
                            'automatico': True
                        }
                    )

                    # Envia email notificando o usuário
                    enviar_email_certificado_disponivel(certificado)

                    certificados_gerados += 1
                    logger.info(f'Certificado gerado automaticamente para {inscricao.usuario.get_full_name()} - Evento: {evento.titulo}')

                except Exception as e:
                    logger.error(f'Erro ao gerar certificado para {inscricao.usuario.get_full_name()}: {e}')

            # Atualiza o status do evento para FECHADO
            if certificados_gerados > 0:
                evento.status = 'FECHADO'
                evento.save()
                logger.info(f'Evento "{evento.titulo}" fechado automaticamente após geração de {certificados_gerados} certificados')

        except Exception as e:
            logger.error(f'Erro ao processar evento {evento.titulo}: {e}')
