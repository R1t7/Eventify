from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from eventos.models import Evento, Inscricao

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais para testes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de dados...'))

        # Criar usuários
        self.criar_usuarios()

        # Criar eventos
        self.criar_eventos()

        self.stdout.write(self.style.SUCCESS('Carga de dados concluída com sucesso!'))

    def criar_usuarios(self):
        self.stdout.write('Criando usuários...')

        # Usuário Organizador
        if not Usuario.objects.filter(username='organizador@sgea.com').exists():
            organizador = Usuario.objects.create_user(
                username='organizador@sgea.com',
                email='organizador@sgea.com',
                password='Admin@123',
                first_name='Admin',
                last_name='Organizador',
                telefone='(11) 98765-4321',
                instituicao_ensino='Eventify - Sistema Central',
                perfil='ORGANIZADOR',
                email_confirmado=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário Organizador criado: {organizador.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'- Usuário Organizador já existe'))

        # Usuário Aluno
        if not Usuario.objects.filter(username='aluno@sgea.com').exists():
            aluno = Usuario.objects.create_user(
                username='aluno@sgea.com',
                email='aluno@sgea.com',
                password='Aluno@123',
                first_name='João',
                last_name='Silva',
                telefone='(11) 91234-5678',
                instituicao_ensino='Universidade Federal',
                perfil='ALUNO',
                email_confirmado=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário Aluno criado: {aluno.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'- Usuário Aluno já existe'))

        # Usuário Professor
        if not Usuario.objects.filter(username='professor@sgea.com').exists():
            professor = Usuario.objects.create_user(
                username='professor@sgea.com',
                email='professor@sgea.com',
                password='Professor@123',
                first_name='Maria',
                last_name='Santos',
                telefone='(11) 97654-3210',
                instituicao_ensino='Universidade Federal',
                perfil='PROFESSOR',
                email_confirmado=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário Professor criado: {professor.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'- Usuário Professor já existe'))

        # Criar alguns usuários adicionais para testes
        usuarios_extras = [
            {
                'username': 'carlos.aluno@sgea.com',
                'email': 'carlos.aluno@sgea.com',
                'password': 'Carlos@123',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'telefone': '(21) 98888-7777',
                'instituicao_ensino': 'Instituto Federal',
                'perfil': 'ALUNO',
            },
            {
                'username': 'ana.professora@sgea.com',
                'email': 'ana.professora@sgea.com',
                'password': 'Ana@123',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'telefone': '(31) 99999-8888',
                'instituicao_ensino': 'Universidade Estadual',
                'perfil': 'PROFESSOR',
            },
        ]

        for user_data in usuarios_extras:
            if not Usuario.objects.filter(username=user_data['username']).exists():
                usuario = Usuario.objects.create_user(**user_data, email_confirmado=True)
                self.stdout.write(self.style.SUCCESS(f'✓ Usuário {usuario.perfil} criado: {usuario.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Usuário {user_data["username"]} já existe'))

    def criar_eventos(self):
        self.stdout.write('Criando eventos...')

        try:
            organizador = Usuario.objects.get(username='organizador@sgea.com')
            professor = Usuario.objects.get(username='professor@sgea.com')
            aluno = Usuario.objects.get(username='aluno@sgea.com')
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR('Erro: Usuários base não encontrados'))
            return

        hoje = timezone.now().date()

        eventos_data = [
            {
                'tipo': 'SEMANA_ACADEMICA',
                'titulo': 'Semana de Tecnologia 2025',
                'descricao': 'A Semana de Tecnologia 2025 é um evento que reúne palestras, workshops e minicursos sobre as últimas tendências em tecnologia, inovação e mercado de trabalho.',
                'data_inicio': hoje + timedelta(days=10),
                'data_fim': hoje + timedelta(days=14),
                'horario': '19:00',
                'local': 'Auditório Principal',
                'vagas': 200,
            },
            {
                'tipo': 'PALESTRA',
                'titulo': 'Inteligência Artificial no Mercado de Trabalho',
                'descricao': 'Palestra sobre as aplicações de IA e seu impacto no mercado de trabalho atual.',
                'data_inicio': hoje + timedelta(days=5),
                'data_fim': hoje + timedelta(days=5),
                'horario': '14:00',
                'local': 'Sala 201',
                'vagas': 50,
            },
            {
                'tipo': 'MINICURSO',
                'titulo': 'Python para Iniciantes',
                'descricao': 'Aprenda os conceitos básicos de programação Python em 3 dias intensivos.',
                'data_inicio': hoje + timedelta(days=20),
                'data_fim': hoje + timedelta(days=22),
                'horario': '14:00',
                'local': 'Laboratório 3',
                'vagas': 20,
            },
            {
                'tipo': 'SEMINARIO',
                'titulo': 'Inovação em Engenharia',
                'descricao': 'Seminário sobre as últimas inovações na área de engenharia civil e mecânica.',
                'data_inicio': hoje + timedelta(days=15),
                'data_fim': hoje + timedelta(days=15),
                'horario': '19:00',
                'local': 'Auditório Central',
                'vagas': 100,
            },
            {
                'tipo': 'MINICURSO',
                'titulo': 'Django Web Development',
                'descricao': 'Curso completo de desenvolvimento web com Django Framework.',
                'data_inicio': hoje + timedelta(days=25),
                'data_fim': hoje + timedelta(days=29),
                'horario': '18:00',
                'local': 'Laboratório 1',
                'vagas': 30,
            },
        ]

        for evento_data in eventos_data:
            if not Evento.objects.filter(titulo=evento_data['titulo']).exists():
                evento = Evento.objects.create(
                    **evento_data,
                    organizador=organizador,
                    professor_responsavel=professor,
                    status='ABERTO'
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Evento criado: {evento.titulo}'))

                # Inscrever o aluno em alguns eventos
                if evento.tipo in ['MINICURSO', 'PALESTRA']:
                    Inscricao.objects.create(
                        usuario=aluno,
                        evento=evento,
                        status='CONFIRMADA'
                    )
                    self.stdout.write(self.style.SUCCESS(f'  → Aluno inscrito em: {evento.titulo}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Evento já existe: {evento_data["titulo"]}'))
