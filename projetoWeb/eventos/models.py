from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os

Usuario = get_user_model()

def evento_banner_path(instance, filename):
    """Define o caminho para salvar os banners dos eventos"""
    ext = filename.split('.')[-1]
    filename = f"evento_{instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('eventos', 'banners', filename)

class Evento(models.Model):
    TIPO_CHOICES = [
        ('SEMINARIO', 'Seminário'),
        ('PALESTRA', 'Palestra'),
        ('MINICURSO', 'Minicurso'),
        ('SEMANA_ACADEMICA', 'Semana Acadêmica'),
    ]

    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('FECHADO', 'Fechado'),
        ('CANCELADO', 'Cancelado'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    horario = models.TimeField()
    local = models.CharField(max_length=200)
    vagas = models.IntegerField()
    professor_responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_responsavel',
        limit_choices_to={'perfil': 'PROFESSOR'}
    )
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos_organizados')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO')
    banner = models.ImageField(
        upload_to=evento_banner_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'evento'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"

    def clean(self):
        """Validações customizadas do modelo"""
        super().clean()

        # Valida se a data de início não é anterior à data atual
        if self.data_inicio and self.data_inicio < timezone.now().date():
            raise ValidationError({'data_inicio': 'A data de início não pode ser anterior à data atual.'})

        # Valida se a data de fim não é anterior à data de início
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({'data_fim': 'A data de término não pode ser anterior à data de início.'})

        # Valida se há um professor responsável
        if not self.professor_responsavel:
            raise ValidationError({'professor_responsavel': 'Todo evento deve ter um professor responsável.'})

        # Valida se o número de vagas é positivo
        if self.vagas and self.vagas <= 0:
            raise ValidationError({'vagas': 'O número de vagas deve ser maior que zero.'})

    @property
    def vagas_disponiveis(self):
        inscritos = self.inscricoes.filter(status='CONFIRMADA').count()
        return self.vagas - inscritos

    def esta_aberto(self):
        return self.status == 'ABERTO' and self.vagas_disponiveis > 0

    def pode_inscrever(self, usuario):
        if usuario.is_organizador():
            return False
        return not self.inscricoes.filter(usuario=usuario, status='CONFIRMADA').exists()

class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='inscricoes')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMADA')
    presenca_confirmada = models.BooleanField(
        default=False,
        help_text='Confirmar presença para liberar certificado'
    )
    
    class Meta:
        db_table = 'inscricao'
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.evento.titulo}"

