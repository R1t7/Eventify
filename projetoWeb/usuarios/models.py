from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import secrets

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('ORGANIZADOR', 'Organizador'),
    ]

    phone_validator = RegexValidator(
        regex=r'^\d{10,11}$',
        message='Telefone deve conter 10 ou 11 dígitos (apenas números)'
    )

    telefone = models.CharField(max_length=11, validators=[phone_validator], help_text='Digite apenas números (10 ou 11 dígitos)')
    instituicao_ensino = models.CharField(max_length=200)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    email_confirmado = models.BooleanField(default=False)
    codigo_confirmacao = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name()} - {self.perfil}"

    def is_organizador(self):
        return self.perfil == 'ORGANIZADOR'

    def is_aluno(self):
        return self.perfil == 'ALUNO'

    def is_professor(self):
        return self.perfil == 'PROFESSOR'

    def gerar_codigo_confirmacao(self):
        """Gera um código único de confirmação para o usuário"""
        self.codigo_confirmacao = secrets.token_urlsafe(32)
        self.save()
        return self.codigo_confirmacao