from django.contrib import admin
from .models import LogAuditoria

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['acao', 'usuario', 'data_hora', 'ip_address']
    list_filter = ['acao', 'data_hora']
    search_fields = ['usuario__username', 'descricao']
    readonly_fields = ['usuario', 'acao', 'descricao', 'ip_address', 'user_agent', 'data_hora', 'dados_adicionais']
    date_hierarchy = 'data_hora'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
