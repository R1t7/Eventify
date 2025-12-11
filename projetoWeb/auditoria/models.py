from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class LogAuditoria(models.Model):
    ACAO_CHOICES = [
        ('CRIAR_USUARIO', 'Criação de Usuário'),
        ('CRIAR_EVENTO', 'Criação de Evento'),
        ('ALTERAR_EVENTO', 'Alteração de Evento'),
        ('EXCLUIR_EVENTO', 'Exclusão de Evento'),
        ('CONSULTA_API_EVENTOS', 'Consulta de Eventos via API'),
        ('INSCRICAO_EVENTO', 'Inscrição em Evento'),
        ('GERAR_CERTIFICADO', 'Geração de Certificado'),
        ('CONSULTAR_CERTIFICADO', 'Consulta de Certificado'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs_auditoria'
    )
    acao = models.CharField(max_length=50, choices=ACAO_CHOICES)
    descricao = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    dados_adicionais = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'log_auditoria'
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']

    def __str__(self):
        usuario_nome = self.usuario.username if self.usuario else 'Sistema'
        return f"{self.get_acao_display()} - {usuario_nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    @staticmethod
    def registrar(usuario, acao, descricao, request=None, dados_adicionais=None):
        """Método auxiliar para registrar logs de auditoria"""
        log = LogAuditoria(
            usuario=usuario,
            acao=acao,
            descricao=descricao,
            dados_adicionais=dados_adicionais
        )

        if request:
            log.ip_address = LogAuditoria.get_client_ip(request)
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')

        log.save()
        return log

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
