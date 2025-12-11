from django.db import models
from eventos.models import Inscricao
import uuid

class Certificado(models.Model):
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE, related_name='certificado')
    codigo_validacao = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_emissao = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='certificados/', null=True, blank=True)
    
    class Meta:
        db_table = 'certificado'
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
    
    def __str__(self):
        return f"Certificado - {self.inscricao}"
