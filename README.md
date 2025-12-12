# 🎓 Eventify - Sistema de Gestão de Eventos Acadêmicos

Sistema web desenvolvido em Django para gerenciamento completo de eventos acadêmicos, incluindo inscrições, controle de vagas, emissão de certificados digitais, API REST e sistema de auditoria.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Instalação Rápida](#-instalação-rápida)
- [Como Usar](#-como-usar)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [API REST](#-api-rest)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Perfis de Usuário](#-perfis-de-usuário)
- [Credenciais de Teste](#-credenciais-de-teste)
- [Comandos Úteis](#-comandos-úteis)

---

## 🎯 Sobre o Projeto

O Eventify é um sistema completo para gestão de eventos acadêmicos que permite:

- **Organizadores**: Criar e gerenciar eventos, controlar inscrições, emitir certificados e consultar logs de auditoria
- **Professores e Alunos**: Se inscrever em eventos, acompanhar inscrições e obter certificados
- **API REST**: Integração externa com autenticação por token e rate limiting

---

## ✨ Funcionalidades

### 🔐 Autenticação e Autorização
- Sistema de login e registro com validação avançada
- Três perfis de usuário (Aluno, Professor, Organizador)
- Controle de permissões por perfil
- Confirmação de email (modo desenvolvimento: console)

### 📅 Gestão de Eventos
- Criar eventos (Seminários, Palestras, Minicursos, Semanas Acadêmicas)
- Upload de banner com validação (JPG, PNG, GIF, máx. 5MB)
- Editar e excluir eventos
- Controle automático de vagas
- Status do evento (Aberto, Fechado, Cancelado)
- Professor responsável obrigatório
- Validação de datas (não permite eventos com data passada)

### 📝 Sistema de Inscrições
- Inscrição em eventos com validação de vagas
- Cancelamento e re-inscrição permitidos
- Notificação por email após inscrição
- Prevenção de duplicatas (status-based)
- Status de inscrição (Confirmada, Cancelada)

### 🎓 Certificados Digitais
- Emissão automática de certificados (comando manage.py)
- Código único de validação (UUID)
- Validação pública de certificados
- Download em PDF com ReportLab
- Notificação por email quando disponível

### 📊 Dashboard
- Estatísticas gerais do sistema
- Próximos eventos
- Contador de inscrições e certificados

### 🔌 API REST
- Autenticação por token
- Endpoints para eventos e inscrições
- Rate limiting (20 req/dia para eventos, 50 para inscrições)
- Documentação completa dos endpoints

### 📜 Sistema de Auditoria
- Registro de todas as ações críticas
- Consulta por usuário, data ou tipo de ação
- Armazenamento de IP e User Agent
- Dados adicionais em JSON
- Acesso restrito a organizadores

### 📧 Notificações por Email
- Confirmação de cadastro
- Confirmação de inscrição em eventos
- Certificado disponível
- Templates HTML estilizados
- Modo desenvolvimento: console (emails no terminal)

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/R1t7/Projeto_Web.git
cd Projeto_Web

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install django djangorestframework pillow reportlab weasyprint

# 4. Entre na pasta do projeto Django
cd projetoWeb

# 5. Execute as migrações
python manage.py migrate

# 6. Popule o banco com dados de teste
python manage.py seed_database

# 7. Inicie o servidor
python manage.py runserver
```

**Acesse:** http://localhost:8000

---

## 💻 Como Usar

### Primeiro Acesso

Use uma das contas de teste ou crie uma nova conta:

**Organizador:**
- Login: `organizador@sgea.com`
- Senha: `Admin@123`

**Professor:**
- Login: `professor@sgea.com`
- Senha: `Professor@123`

**Aluno:**
- Login: `aluno@sgea.com`
- Senha: `Aluno@123`

### Como Organizador

1. Acesse o menu "Eventos"
2. Clique em "Criar Novo Evento"
3. Preencha os dados do evento:
   - Selecione um professor responsável
   - Escolha uma data futura
   - Faça upload de um banner (opcional)
4. Visualize inscrições em "Detalhes do Evento"
5. Emita certificados após o evento
6. Consulte logs em "Auditoria"

### Como Aluno/Professor

1. Navegue pelos eventos disponíveis
2. Inscreva-se nos eventos de interesse
3. Acompanhe em "Minhas Inscrições"
4. Cancele inscrições se necessário (pode se re-inscrever depois)
5. Acesse certificados em "Certificados"
6. Valide certificados usando o código UUID

---

## 🛠 Tecnologias Utilizadas

### Backend
- **Python 3.13** - Linguagem de programação
- **Django 5.2** - Framework web
- **Django REST Framework 3.15** - API REST
- **SQLite** - Banco de dados

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização (design responsivo com gradientes)
- **JavaScript** - Interatividade

### Bibliotecas Python
- `reportlab 4.2.5` - Geração de PDF para certificados
- `Pillow 11.0.0` - Processamento e validação de imagens
- `weasyprint 62.3` - Geração avançada de PDFs

---

## 🔌 API REST

### Autenticação

**Obter Token:**
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "aluno_lucas",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "aluno_lucas",
  "perfil": "ALUNO"
}
```

### Endpoints Disponíveis

| Método | Endpoint | Descrição | Rate Limit |
|--------|----------|-----------|------------|
| GET | `/api/eventos/` | Listar eventos | 20/dia |
| GET | `/api/eventos/{id}/` | Detalhes do evento | 20/dia |
| POST | `/api/inscricoes/` | Inscrever em evento | 50/dia |
| DELETE | `/api/inscricoes/{id}/` | Cancelar inscrição | 50/dia |
| GET | `/api/me/` | Dados do usuário | - |
| GET | `/api/me/inscricoes/` | Minhas inscrições | - |

### Exemplo de Uso

**Listar Eventos:**
```bash
curl -X GET http://localhost:8000/api/eventos/ \
  -H "Authorization: Token SEU_TOKEN_AQUI"
```

**Inscrever-se em Evento:**
```bash
curl -X POST http://localhost:8000/api/inscricoes/ \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"evento_id": 1}'
```

**Script Python de Teste:**
```bash
python3 testar_api.py
```

---

## 📁 Estrutura do Projeto

```
Projeto_Web/
├── projetoWeb/                 # Projeto Django principal
│   ├── manage.py              # Gerenciador Django
│   ├── settings.py            # Configurações do Django
│   ├── urls.py                # URLs principais
│   ├── templates/             # Templates HTML
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── listar_eventos.html
│   │   ├── detalhes_evento.html
│   │   ├── minhas_inscricoes.html
│   │   ├── meus_certificados.html
│   │   ├── validar_certificado.html
│   │   ├── auditoria/
│   │   │   ├── listar_logs.html
│   │   │   ├── logs_usuario.html
│   │   │   └── logs_data.html
│   │   └── emails/
│   │       ├── confirmacao_cadastro.html
│   │       ├── inscricao_confirmada.html
│   │       └── certificado_disponivel.html
│   ├── usuarios/              # App de usuários
│   │   ├── models.py          # Model Usuario
│   │   ├── views.py           # Views de autenticação
│   │   ├── forms.py           # Formulários com validação
│   │   ├── email.py           # Sistema de email
│   │   └── management/commands/
│   │       └── seed_database.py
│   ├── eventos/               # App de eventos
│   │   ├── models.py          # Models Evento e Inscricao
│   │   ├── views.py           # Views de eventos
│   │   └── forms.py           # Formulários
│   ├── certificados/          # App de certificados
│   │   ├── models.py          # Model Certificado
│   │   ├── views.py           # Views de certificados
│   │   └── management/commands/
│   │       └── gerar_certificados.py
│   ├── auditoria/             # Sistema de logs
│   │   ├── models.py          # LogAuditoria
│   │   └── views.py           # Views de consulta
│   └── api/                   # API REST
│       ├── serializers.py     # Serializers DRF
│       ├── views.py           # Views da API
│       ├── urls.py            # URLs da API
│       └── throttling.py      # Rate limiting
├── static/                    # Arquivos estáticos
│   ├── css/styles.css
│   └── js/main.js
├── media/                     # Upload de arquivos
│   └── eventos/banners/
├── venv/                      # Ambiente virtual Python
├── db.sqlite3                 # Banco de dados SQLite
├── testar_api.py              # Script de teste da API
├── popular_db.py              # Script legacy (deprecated)
└── README.md                  # Este arquivo
```

---

## 👥 Perfis de Usuário

### 🎓 Aluno
- ✅ Visualizar eventos
- ✅ Se inscrever em eventos
- ✅ Cancelar e re-inscrever
- ✅ Visualizar certificados
- ✅ Validar certificados
- ❌ Criar eventos

### 📚 Professor
- ✅ Visualizar eventos
- ✅ Se inscrever em eventos
- ✅ Cancelar e re-inscrever
- ✅ Visualizar certificados
- ✅ Validar certificados
- ❌ Criar eventos

### 👔 Organizador
- ✅ Criar, editar e excluir eventos
- ✅ Visualizar lista de inscritos
- ✅ Emitir certificados
- ✅ Consultar logs de auditoria
- ✅ Acessar API REST
- ❌ Se inscrever em eventos
- ❌ Receber certificados

---

## 🔑 Credenciais de Teste

### Organizadores
```
Username: org_admin      | Senha: senha123
Username: org_fernanda   | Senha: senha123
Username: org_ricardo    | Senha: senha123
```

### Professores
```
Username: prof_carlos    | Senha: senha123
Username: prof_maria     | Senha: senha123
Username: prof_joao      | Senha: senha123
```

### Alunos
```
Username: aluno_lucas    | Senha: senha123
Username: aluna_julia    | Senha: senha123
Username: aluno_rafael   | Senha: senha123
```

---

## 🔧 Comandos Úteis

### Gerenciamento do Banco de Dados

```bash
# Popular banco com dados de teste
python manage.py seed_database

# Criar superusuário para admin Django
python manage.py createsuperuser

# Limpar e recriar banco de dados
rm db.sqlite3
python manage.py migrate
python manage.py seed_database
```

### Certificados

```bash
# Gerar certificados automaticamente
python manage.py gerar_certificados

# Gerar certificados de um evento específico
python manage.py gerar_certificados --evento-id=1
```

### Telefones

```bash
# Converter telefones do formato antigo (XX) XXXXX-XXXX para novo formato (apenas dígitos)
python manage.py converter_telefones
```

### Servidor

```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Iniciar em porta diferente
python manage.py runserver 8080

# Acessar admin Django
# http://localhost:8000/admin/
```

### Testes

```bash
# Executar testes do Django
python manage.py test

# Verificar erros no projeto
python manage.py check
```

---

## 📝 Validações Implementadas

### Eventos
- ✅ Data de início não pode ser anterior à data atual
- ✅ Data de fim não pode ser anterior à data de início
- ✅ Número de vagas deve ser maior que zero
- ✅ Professor responsável é obrigatório
- ✅ Banner deve ser imagem válida (JPG, PNG, GIF, máx. 5MB)

### Inscrições
- ✅ Organizadores não podem se inscrever
- ✅ Verifica vagas disponíveis
- ✅ Evento deve estar aberto
- ✅ Permite re-inscrição após cancelamento

### Usuários
- ✅ Telefone: apenas dígitos (10 ou 11 números)
- ✅ Email único no sistema
- ✅ Validação de dados obrigatórios

---

## 🗄️ Modelos de Dados

### Usuario (Herda de AbstractUser)
- username, email, first_name, last_name
- telefone (10-11 dígitos)
- instituicao_ensino
- perfil (ALUNO, PROFESSOR, ORGANIZADOR)
- data_cadastro

### Evento
- tipo (SEMINARIO, PALESTRA, MINICURSO, SEMANA_ACADEMICA)
- titulo, descricao
- data_inicio, data_fim, horario
- local, vagas
- organizador (FK → Usuario)
- professor_responsavel (FK → Usuario)
- banner (ImageField)
- status (ABERTO, FECHADO, CANCELADO)

### Inscricao
- usuario (FK → Usuario)
- evento (FK → Evento)
- data_inscricao
- status (CONFIRMADA, CANCELADA)

### Certificado
- inscricao (OneToOne → Inscricao)
- codigo_validacao (UUID único)
- data_emissao

### LogAuditoria
- usuario (FK → Usuario)
- acao (choices: CRIAR_USUARIO, CRIAR_EVENTO, etc.)
- descricao
- ip_address
- user_agent
- data_hora
- dados_adicionais (JSONField)

---

## 📧 Configuração de Email

### Desenvolvimento (Padrão)
Emails aparecem no console/terminal:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Produção (Gmail/SMTP)
Configure em `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
DEFAULT_FROM_EMAIL = 'Eventify <seu-email@gmail.com>'
```

---

## 🔒 Segurança

- Senhas hashadas com PBKDF2
- Proteção CSRF em todos os formulários
- Validação de dados no backend e frontend
- Autenticação por token na API
- Rate limiting para prevenção de abuso
- Logs de auditoria com IP e User Agent
- Validação de upload de arquivos
- Prevenção de SQL Injection
- XSS Protection

---

## 🚀 Deploy (Produção)

### Configurações necessárias no `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com']

SECRET_KEY = 'gere-uma-chave-secreta-super-segura'

# Configurar banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sgea_db',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Arquivos estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
python manage.py collectstatic
```

---

## 🎨 Design

O Eventify possui um design moderno e responsivo com:

- ✨ Gradientes modernos (roxo/azul)
- 🎴 Cards com animações suaves
- 📱 Layout totalmente responsivo
- 🎯 Interface intuitiva e amigável
- ⚡ Feedback visual em todas as ações
- 🌙 Temas consistentes em templates de email

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Victor Rithelly**

- 🔗 GitHub: [@R1t7](https://github.com/R1t7)
- 📦 Repositório: [Eventify](https://github.com/R1t7/Eventify)

---

## 📊 Status do Projeto

✅ **Fase 2 Completa**

Todas as funcionalidades da Fase 2 foram implementadas e testadas:
- Validação avançada de formulários
- Sistema de seeding de dados
- API REST com rate limiting
- Upload de banners
- Regras de negócio completas
- Notificações por email
- Emissão automática de certificados
- Perfis e permissões
- Logs de auditoria
- Identidade visual consistente
- Documentação completa

---

<div align="center">

**Desenvolvido com ❤️ usando Django**

⭐ Se este projeto foi útil, considere dar uma estrela no [GitHub](https://github.com/R1t7/Projeto_Web)!

[🔗 Repositório](https://github.com/R1t7/Projeto_Web) | [🐛 Issues](https://github.com/R1t7/Projeto_Web/issues)

</div>
