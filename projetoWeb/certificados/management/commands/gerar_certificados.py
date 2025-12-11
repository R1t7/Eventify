from django.core.management.base import BaseCommand
from django.utils import timezone
from eventos.models import Evento, Inscricao
from certificados.models import Certificado
from auditoria.models import LogAuditoria
from usuarios.email import enviar_email_certificado_disponivel


class Command(BaseCommand):
    help = 'Gera certificados automaticamente para eventos finalizados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--evento-id',
            type=int,
            help='ID do evento específico para gerar certificados'
        )

    def handle(self, *args, **kwargs):
        evento_id = kwargs.get('evento_id')

        self.stdout.write(self.style.SUCCESS('Iniciando geração de certificados...'))

        if evento_id:
            # Gera certificados para um evento específico
            try:
                evento = Evento.objects.get(id=evento_id)
                self.gerar_certificados_evento(evento)
            except Evento.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Evento com ID {evento_id} não encontrado'))
                return
        else:
            # Gera certificados para todos os eventos finalizados
            eventos_finalizados = Evento.objects.filter(
                data_fim__lt=timezone.now().date(),
                status='ABERTO'
            )

            if not eventos_finalizados.exists():
                self.stdout.write(self.style.WARNING('Nenhum evento finalizado encontrado'))
                return

            for evento in eventos_finalizados:
                self.gerar_certificados_evento(evento)

        self.stdout.write(self.style.SUCCESS('Geração de certificados concluída!'))

    def gerar_certificados_evento(self, evento):
        """Gera certificados para todas as inscrições confirmadas de um evento"""
        self.stdout.write(f'\nProcessando evento: {evento.titulo}')

        # Busca inscrições confirmadas COM PRESENÇA sem certificado
        inscricoes = Inscricao.objects.filter(
            evento=evento,
            status='CONFIRMADA',
            presenca_confirmada=True,  # Apenas quem teve presença confirmada
            certificado__isnull=True
        ).select_related('usuario')

        if not inscricoes.exists():
            self.stdout.write(self.style.WARNING(f'  → Nenhuma inscrição sem certificado encontrada'))
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
                        'codigo_validacao': str(certificado.codigo_validacao)
                    }
                )

                # Envia email notificando o usuário
                enviar_email_certificado_disponivel(certificado)

                certificados_gerados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Certificado gerado para: {inscricao.usuario.get_full_name()}'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Erro ao gerar certificado para {inscricao.usuario.get_full_name()}: {e}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n  Total de certificados gerados: {certificados_gerados}'
            )
        )

        # Atualiza o status do evento para FECHADO
        if certificados_gerados > 0:
            evento.status = 'FECHADO'
            evento.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'  → Status do evento atualizado para FECHADO'
                )
            )
