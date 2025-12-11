from django.core.management.base import BaseCommand
from usuarios.models import Usuario
import re


class Command(BaseCommand):
    help = 'Converte telefones do formato (XX) XXXXX-XXXX para apenas números'

    def handle(self, *args, **options):
        usuarios = Usuario.objects.all()
        convertidos = 0

        for usuario in usuarios:
            telefone_original = usuario.telefone
            # Remove tudo que não for número
            telefone_limpo = re.sub(r'\D', '', telefone_original)

            if telefone_limpo != telefone_original:
                usuario.telefone = telefone_limpo
                try:
                    usuario.save()
                    convertidos += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Convertido: {telefone_original} → {telefone_limpo}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Erro ao converter {usuario.username}: {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal de telefones convertidos: {convertidos}'
            )
        )
