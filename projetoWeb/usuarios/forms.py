from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
from .models import Usuario

class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'exemplo@email.com',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name',
                 'telefone', 'instituicao_ensino', 'perfil',
                 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Nome de usuário',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Primeiro nome',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Sobrenome',
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(XX) XXXXX-XXXX',
                'class': 'form-control',
                'maxlength': '15',  # (11) 98765-4321 = 15 caracteres
                'title': 'Digite seu telefone com DDD'
            }),
            'instituicao_ensino': forms.TextInput(attrs={
                'placeholder': 'Nome da Instituição',
                'class': 'form-control'
            }),
            'perfil': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
        self.fields['password1'].help_text = 'Mínimo 8 caracteres, contendo letras, números e caracteres especiais.'

    def clean_telefone(self):
        """Valida o formato do telefone - aceita apenas números"""
        telefone = self.cleaned_data.get('telefone')

        if not telefone:
            raise ValidationError('Telefone é obrigatório.')

        # Remove qualquer caractere que não seja número
        telefone_limpo = re.sub(r'\D', '', telefone)

        # Se após limpar não sobrou nada ou sobrou muito pouco, é porque tinha muitas letras
        if not telefone_limpo:
            raise ValidationError('Telefone deve conter apenas números.')

        # Verifica se tem 10 ou 11 dígitos
        if len(telefone_limpo) < 10:
            raise ValidationError('Telefone deve conter pelo menos 10 dígitos.')

        if len(telefone_limpo) > 11:
            raise ValidationError('Telefone deve conter no máximo 11 dígitos.')

        return telefone_limpo

    def clean_email(self):
        """Valida se o email já está em uso"""
        email = self.cleaned_data.get('email')

        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este email já está cadastrado.')

        return email

    def clean_password1(self):
        """Valida a senha com critérios de segurança"""
        password = self.cleaned_data.get('password1')

        if password:
            # Mínimo 8 caracteres
            if len(password) < 8:
                raise ValidationError('A senha deve ter no mínimo 8 caracteres.')

            # Deve conter letras
            if not re.search(r'[a-zA-Z]', password):
                raise ValidationError('A senha deve conter letras.')

            # Deve conter números
            if not re.search(r'\d', password):
                raise ValidationError('A senha deve conter números.')

            # Deve conter caracteres especiais
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError('A senha deve conter caracteres especiais (!@#$%^&*(),.?":{}|<>).')

        return password

    def clean(self):
        """Valida se as senhas conferem"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('As senhas não conferem.')

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu usuário'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )

