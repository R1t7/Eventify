from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UsuarioRegistroForm, LoginForm
from eventos.models import Evento, Inscricao

def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login')
        else:
            # Mostrar erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    from certificados.models import Certificado

    proximos_eventos = Evento.objects.filter(status='ABERTO').order_by('data_inicio')[:5]

    context = {
        'total_eventos': Evento.objects.count(),
        'eventos_abertos': Evento.objects.filter(status='ABERTO').count(),
        'minhas_inscricoes_count': Inscricao.objects.filter(usuario=request.user, status='CONFIRMADA').count(),
        'meus_certificados_count': Certificado.objects.filter(inscricao__usuario=request.user).count(),
        'proximos_eventos': proximos_eventos,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')