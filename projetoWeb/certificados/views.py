from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from eventos.models import Evento, Inscricao
from .models import Certificado
import datetime

@login_required
def emitir_certificado(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, pk=inscricao_id)
    
    # Verifica se o usuário é o organizador do evento
    if inscricao.evento.organizador != request.user:
        messages.error(request, 'Apenas o organizador pode emitir certificados.')
        return redirect('detalhes_evento', pk=inscricao.evento.pk)
    
    # Cria ou obtém o certificado
    certificado, created = Certificado.objects.get_or_create(inscricao=inscricao)

    # Se foi criado agora, envia email
    if created:
        from usuarios.email import enviar_email_certificado_disponivel
        enviar_email_certificado_disponivel(certificado)

    # Gera o PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Título
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 100, "CERTIFICADO")
    
    # Corpo do certificado
    p.setFont("Helvetica", 14)
    texto = f"Certificamos que {inscricao.usuario.get_full_name()}"
    p.drawCentredString(width/2, height - 200, texto)
    
    texto2 = f"participou do evento '{inscricao.evento.titulo}'"
    p.drawCentredString(width/2, height - 230, texto2)
    
    texto3 = f"realizado de {inscricao.evento.data_inicio.strftime('%d/%m/%Y')} a {inscricao.evento.data_fim.strftime('%d/%m/%Y')}"
    p.drawCentredString(width/2, height - 260, texto3)
    
    texto4 = f"Local: {inscricao.evento.local}"
    p.drawCentredString(width/2, height - 290, texto4)
    
    # Código de validação
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, 100, f"Código de validação: {certificado.codigo_validacao}")
    
    # Data de emissão
    p.drawCentredString(width/2, 80, f"Emitido em: {certificado.data_emissao.strftime('%d/%m/%Y')}")
    
    # Finaliza o PDF
    p.showPage()
    p.save()
    
    # Retorna o PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{inscricao.id}.pdf"'
    
    messages.success(request, 'Certificado emitido com sucesso!')
    return response

def validar_certificado(request):
    """Validação de certificado - não requer login para permitir validação pública"""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        if not codigo:
            context = {
                'valido': False,
                'mensagem': 'Por favor, digite um código de validação.',
            }
            return render(request, 'validacao_resultado.html', context)

        try:
            certificado = Certificado.objects.get(codigo_validacao=codigo)
            context = {
                'valido': True,
                'certificado': certificado,
            }
        except Certificado.DoesNotExist:
            context = {
                'valido': False,
                'mensagem': 'Código de validação inválido.',
            }
        except ValueError as e:
            context = {
                'valido': False,
                'mensagem': 'Formato de código inválido. Verifique se copiou corretamente.',
            }

        return render(request, 'validacao_resultado.html', context)

    return render(request, 'validar_certificado.html')

@login_required
def meus_certificados(request):
    if request.user.is_organizador():
        messages.info(request, 'Organizadores não possuem certificados.')
        return redirect('dashboard')
    
    certificados = Certificado.objects.filter(inscricao__usuario=request.user)
    return render(request, 'meus_certificados.html', {'certificados': certificados})

@login_required
def visualizar_certificado(request, certificado_id):
    certificado = get_object_or_404(Certificado, pk=certificado_id)

    # Verifica se o usuário tem permissão para visualizar
    if certificado.inscricao.usuario != request.user and request.user != certificado.inscricao.evento.organizador:
        messages.error(request, 'Você não tem permissão para visualizar este certificado.')
        return redirect('meus_certificados')

    return render(request, 'visualizar_certificado.html', {'certificado': certificado})
