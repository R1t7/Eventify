from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Evento
from usuarios.models import Usuario

class EventoForm(forms.ModelForm):
    professor_responsavel = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(perfil='PROFESSOR'),
        required=True,
        label='Professor Responsável',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Selecione o professor responsável pelo evento'
    )

    banner = forms.ImageField(
        required=False,
        label='Banner do Evento',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png,image/gif'
        }),
        help_text='Formatos aceitos: JPG, JPEG, PNG, GIF (máx. 5MB)'
    )

    class Meta:
        model = Evento
        fields = ['tipo', 'titulo', 'descricao', 'data_inicio', 'data_fim',
                 'horario', 'local', 'vagas', 'professor_responsavel', 'banner', 'status']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do evento'
            }),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control datepicker'
            }),
            'data_fim': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control datepicker'
            }),
            'horario': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control timepicker'
            }),
            'descricao': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Descrição do evento'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local do evento'
            }),
            'vagas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Número de vagas'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_data_inicio(self):
        """Valida se a data de início não é anterior à data atual"""
        data_inicio = self.cleaned_data.get('data_inicio')

        if data_inicio and data_inicio < timezone.now().date():
            raise ValidationError('A data de início não pode ser anterior à data atual.')

        return data_inicio

    def clean_vagas(self):
        """Valida se o número de vagas é positivo"""
        vagas = self.cleaned_data.get('vagas')

        if vagas is not None and vagas <= 0:
            raise ValidationError('O número de vagas deve ser maior que zero.')

        return vagas

    def clean_banner(self):
        """Valida o arquivo de banner"""
        banner = self.cleaned_data.get('banner')

        if banner:
            # Valida o tipo de arquivo
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = banner.name.split('.')[-1].lower()

            if ext not in valid_extensions:
                raise ValidationError(
                    f'Formato de arquivo inválido. Use: {", ".join(valid_extensions)}'
                )

            # Valida o tamanho do arquivo (máximo 5MB)
            if banner.size > 5 * 1024 * 1024:
                raise ValidationError('O arquivo deve ter no máximo 5MB.')

            # Valida se é realmente uma imagem
            try:
                from PIL import Image
                image = Image.open(banner)
                image.verify()
            except Exception:
                raise ValidationError('Arquivo inválido. Por favor, envie uma imagem válida.')

        return banner

    def clean(self):
        """Validações gerais do formulário"""
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise ValidationError({
                    'data_fim': 'A data de término não pode ser anterior à data de início.'
                })

        return cleaned_data