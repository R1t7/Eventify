from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime
from .models import LogAuditoria

@login_required
def listar_logs(request):
    """Lista todos os logs de auditoria (apenas para organizadores)"""
    if not request.user.is_organizador():
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    logs = LogAuditoria.objects.all()

    # Filtros
    acao = request.GET.get('acao')
    if acao:
        logs = logs.filter(acao=acao)

    usuario_id = request.GET.get('usuario')
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)

    data = request.GET.get('data')
    if data:
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            logs = logs.filter(data_hora__date=data_obj)
        except ValueError:
            pass

    # Paginação
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'acoes': LogAuditoria.ACAO_CHOICES,
    }

    return render(request, 'auditoria/listar_logs.html', context)

@login_required
def logs_usuario(request, usuario_id):
    """Lista logs de um usuário específico"""
    if not request.user.is_organizador():
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    logs = LogAuditoria.objects.filter(usuario_id=usuario_id)

    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'auditoria/logs_usuario.html', context)

@login_required
def logs_data(request, data):
    """Lista logs de uma data específica"""
    if not request.user.is_organizador():
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        logs = LogAuditoria.objects.filter(data_hora__date=data_obj)

        paginator = Paginator(logs, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'data': data,
        }

        return render(request, 'auditoria/logs_data.html', context)
    except ValueError:
        return JsonResponse({'erro': 'Data inválida'}, status=400)
