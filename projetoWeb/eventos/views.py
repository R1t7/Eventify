from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Evento, Inscricao
from .forms import EventoForm

@login_required
def listar_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'listar_eventos.html', {'eventos': eventos})

@login_required
def criar_evento(request):
    if not request.user.is_organizador():
        messages.error(request, 'Apenas organizadores podem criar eventos.')
        return redirect('listar_eventos')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                evento = form.save(commit=False)
                evento.organizador = request.user
                evento.full_clean()  # Executa validações do modelo
                evento.save()

                # Registra log de auditoria
                from auditoria.models import LogAuditoria
                LogAuditoria.registrar(
                    usuario=request.user,
                    acao='CRIAR_EVENTO',
                    descricao=f'Criou o evento "{evento.titulo}"',
                    request=request,
                    dados_adicionais={
                        'evento_id': evento.id,
                        'evento_titulo': evento.titulo,
                        'data_inicio': str(evento.data_inicio)
                    }
                )

                messages.success(request, 'Evento criado com sucesso!')
                return redirect('detalhes_evento', pk=evento.pk)
            except ValidationError as e:
                # Captura erros de validação do modelo
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            except Exception as e:
                messages.error(request, f'Erro ao criar evento: {str(e)}')
        else:
            # Exibe erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = EventoForm()

    return render(request, 'criar_evento.html', {'form': form})

@login_required
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    # Apenas organizadores e o criador do evento podem editar
    if not request.user.is_organizador() and evento.organizador != request.user:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('detalhes_evento', pk=pk)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            try:
                evento = form.save(commit=False)
                evento.full_clean()  # Executa validações do modelo
                evento.save()

                # Registra log de auditoria
                from auditoria.models import LogAuditoria
                LogAuditoria.registrar(
                    usuario=request.user,
                    acao='ALTERAR_EVENTO',
                    descricao=f'Alterou o evento "{evento.titulo}"',
                    request=request,
                    dados_adicionais={
                        'evento_id': evento.id,
                        'evento_titulo': evento.titulo
                    }
                )

                messages.success(request, 'Evento atualizado com sucesso!')
                return redirect('detalhes_evento', pk=evento.pk)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar evento: {str(e)}')
    else:
        form = EventoForm(instance=evento)

    return render(request, 'criar_evento.html', {'form': form, 'evento': evento})

@login_required
def excluir_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    # Apenas organizadores podem excluir
    if not request.user.is_organizador():
        messages.error(request, 'Você não tem permissão para excluir eventos.')
        return redirect('detalhes_evento', pk=pk)

    if request.method == 'POST':
        # Registra log antes de excluir
        from auditoria.models import LogAuditoria
        LogAuditoria.registrar(
            usuario=request.user,
            acao='EXCLUIR_EVENTO',
            descricao=f'Excluiu o evento "{evento.titulo}"',
            request=request,
            dados_adicionais={
                'evento_id': evento.id,
                'evento_titulo': evento.titulo,
                'data_inicio': str(evento.data_inicio)
            }
        )

        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('listar_eventos')

    return render(request, 'confirmar_exclusao.html', {'evento': evento})

@login_required
def detalhes_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscrito = False

    if not request.user.is_organizador():
        inscrito = Inscricao.objects.filter(
            usuario=request.user,
            evento=evento,
            status='CONFIRMADA'
        ).exists()

    inscritos = evento.inscricoes.filter(status='CONFIRMADA') if request.user.is_organizador() else None

    context = {
        'evento': evento,
        'inscrito': inscrito,
        'inscritos': inscritos,
        'pode_inscrever': evento.pode_inscrever(request.user) and evento.esta_aberto(),
    }

    context['inscricoes'] = evento.inscricoes.filter(status='CONFIRMADA') if request.user.perfil == 'ORGANIZADOR' or evento.organizador == request.user else None
    return render(request, 'detalhes_evento.html', context)

@login_required
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    if request.user.is_organizador():
        messages.error(request, 'Organizadores não podem se inscrever em eventos.')
        return redirect('detalhes_evento', pk=pk)

    if not evento.esta_aberto():
        messages.error(request, 'Este evento não está disponível para inscrições.')
        return redirect('detalhes_evento', pk=pk)

    if not evento.pode_inscrever(request.user):
        messages.error(request, 'Você já está inscrito neste evento.')
        return redirect('detalhes_evento', pk=pk)

    # Verifica se há vagas disponíveis
    if evento.vagas_disponiveis <= 0:
        messages.error(request, 'Não há vagas disponíveis para este evento.')
        return redirect('detalhes_evento', pk=pk)

    # Verifica se existe uma inscrição cancelada e reativa
    inscricao_cancelada = Inscricao.objects.filter(
        usuario=request.user,
        evento=evento,
        status='CANCELADA'
    ).first()

    if inscricao_cancelada:
        inscricao_cancelada.status = 'CONFIRMADA'
        inscricao_cancelada.save()
        inscricao = inscricao_cancelada
        mensagem = 'Inscrição reativada com sucesso!'
    else:
        inscricao = Inscricao.objects.create(usuario=request.user, evento=evento)
        mensagem = 'Inscrição realizada com sucesso! Verifique seu email.'

    # Registra log de auditoria
    from auditoria.models import LogAuditoria
    LogAuditoria.registrar(
        usuario=request.user,
        acao='INSCRICAO_EVENTO',
        descricao=f'Inscreveu-se no evento "{evento.titulo}"',
        request=request,
        dados_adicionais={
            'evento_id': evento.id,
            'evento_titulo': evento.titulo,
            'inscricao_id': inscricao.id
        }
    )

    # Envia email de confirmação
    from usuarios.email import enviar_email_inscricao_confirmada
    enviar_email_inscricao_confirmada(inscricao)

    messages.success(request, mensagem)

    return redirect('detalhes_evento', pk=pk)

@login_required
def cancelar_inscricao(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, pk=inscricao_id, usuario=request.user)

    # Verificar se a inscrição pertence ao usuário logado
    if inscricao.usuario != request.user:
        messages.error(request, 'Você não tem permissão para cancelar esta inscrição.')
        return redirect('minhas_inscricoes')

    inscricao.status = 'CANCELADA'
    inscricao.save()

    messages.success(request, 'Inscrição cancelada com sucesso!')
    return redirect('minhas_inscricoes')

@login_required
def minhas_inscricoes(request):
    if request.user.is_organizador():
        messages.info(request, 'Organizadores não possuem inscrições.')
        return redirect('dashboard')

    inscricoes = Inscricao.objects.filter(usuario=request.user).exclude(status='CANCELADA')
    return render(request, 'minhas_inscricoes.html', {'inscricoes': inscricoes})

@login_required
def confirmar_presenca(request, inscricao_id):
    """Confirma a presença de um participante no evento"""
    inscricao = get_object_or_404(Inscricao, pk=inscricao_id)

    # Verifica se o usuário é o organizador do evento
    if inscricao.evento.organizador != request.user and not request.user.is_organizador():
        messages.error(request, 'Apenas o organizador pode confirmar presenças.')
        return redirect('detalhes_evento', pk=inscricao.evento.pk)

    # Confirma a presença
    inscricao.presenca_confirmada = True
    inscricao.save()

    # Registra log de auditoria
    from auditoria.models import LogAuditoria
    LogAuditoria.registrar(
        usuario=request.user,
        acao='INSCRICAO_EVENTO',
        descricao=f'Presença confirmada: {inscricao.usuario.get_full_name()} - {inscricao.evento.titulo}',
        request=request,
        dados_adicionais={
            'inscricao_id': inscricao.id,
            'evento_id': inscricao.evento.id,
            'usuario_id': inscricao.usuario.id,
            'acao': 'confirmar_presenca'
        }
    )

    messages.success(request, f'Presença confirmada para {inscricao.usuario.get_full_name()}!')
    return redirect('detalhes_evento', pk=inscricao.evento.pk)

@login_required
def remover_presenca(request, inscricao_id):
    """Remove a confirmação de presença de um participante"""
    inscricao = get_object_or_404(Inscricao, pk=inscricao_id)

    # Verifica se o usuário é o organizador do evento
    if inscricao.evento.organizador != request.user and not request.user.is_organizador():
        messages.error(request, 'Apenas o organizador pode remover presenças.')
        return redirect('detalhes_evento', pk=inscricao.evento.pk)

    # Remove a presença
    inscricao.presenca_confirmada = False
    inscricao.save()

    # Registra log de auditoria
    from auditoria.models import LogAuditoria
    LogAuditoria.registrar(
        usuario=request.user,
        acao='INSCRICAO_EVENTO',
        descricao=f'Presença removida: {inscricao.usuario.get_full_name()} - {inscricao.evento.titulo}',
        request=request,
        dados_adicionais={
            'inscricao_id': inscricao.id,
            'evento_id': inscricao.evento.id,
            'usuario_id': inscricao.usuario.id,
            'acao': 'remover_presenca'
        }
    )

    messages.warning(request, f'Presença removida para {inscricao.usuario.get_full_name()}.')
    return redirect('detalhes_evento', pk=inscricao.evento.pk)

