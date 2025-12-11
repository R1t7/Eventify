from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def enviar_email_confirmacao(usuario):
    """
    Envia email de confirmação para novo usuário
    """
    # Gera código de confirmação
    codigo = usuario.gerar_codigo_confirmacao()

    # URL de confirmação
    url_confirmacao = f"{settings.BASE_URL}/confirmar-email/{codigo}/"

    # Contexto para o template
    context = {
        'usuario': usuario,
        'nome_completo': usuario.get_full_name(),
        'codigo_confirmacao': codigo,
        'url_confirmacao': url_confirmacao,
        'base_url': settings.BASE_URL,
    }

    # Renderiza o template HTML
    html_content = render_to_string('emails/confirmacao_cadastro.html', context)
    text_content = strip_tags(html_content)

    # Assunto do email
    subject = 'Bem-vindo ao Eventify - Confirme seu cadastro'

    # Cria o email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email]
    )

    # Anexa a versão HTML
    email.attach_alternative(html_content, "text/html")

    # Envia o email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


def enviar_email_inscricao_confirmada(inscricao):
    """
    Envia email confirmando a inscrição em um evento
    """
    usuario = inscricao.usuario
    evento = inscricao.evento

    context = {
        'usuario': usuario,
        'nome_completo': usuario.get_full_name(),
        'evento': evento,
        'inscricao': inscricao,
        'base_url': settings.BASE_URL,
    }

    html_content = render_to_string('emails/inscricao_confirmada.html', context)
    text_content = strip_tags(html_content)

    subject = f'Inscrição confirmada - {evento.titulo}'

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email]
    )

    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


def enviar_email_certificado_disponivel(certificado):
    """
    Envia email notificando que o certificado está disponível
    """
    usuario = certificado.inscricao.usuario
    evento = certificado.inscricao.evento

    context = {
        'usuario': usuario,
        'nome_completo': usuario.get_full_name(),
        'evento': evento,
        'certificado': certificado,
        'url_certificado': f"{settings.BASE_URL}/certificados/{certificado.id}/",
        'base_url': settings.BASE_URL,
    }

    html_content = render_to_string('emails/certificado_disponivel.html', context)
    text_content = strip_tags(html_content)

    subject = f'Certificado disponível - {evento.titulo}'

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[usuario.email]
    )

    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False
