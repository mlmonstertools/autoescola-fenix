from django.contrib import admin
from django.utils.html import format_html
from .models import Aluno, DocumentoAluno


class DocumentoAlunoInline(admin.TabularInline):
    model = DocumentoAluno
    extra = 0


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'telefone', 'cidade', 'ativo', 'foto_preview']
    list_filter = ['ativo', 'uf', 'genero', 'consentimento_lgpd']
    search_fields = ['nome_completo', 'cpf', 'email', 'telefone']
    ordering = ['nome_completo']
    inlines = [DocumentoAlunoInline]
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'rg', 'data_nascimento', 'genero', 'estado_civil', 'foto')
        }),
        ('Filiacao', {
            'fields': ('nome_mae', 'nome_pai', 'naturalidade', 'nacionalidade')
        }),
        ('Contato', {
            'fields': ('email', 'telefone', 'telefone_alternativo')
        }),
        ('Endereco', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf')
        }),
        ('LGPD', {
            'fields': ('consentimento_lgpd', 'data_consentimento')
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('ativo', 'criado_em', 'atualizado_em', 'criado_por')
        }),
    )
    
    readonly_fields = ['criado_em', 'atualizado_em', 'criado_por']
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="50" height="67" />', obj.foto.url)
        return '-'
    foto_preview.short_description = 'Foto'


@admin.register(DocumentoAluno)
class DocumentoAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'tipo', 'criado_em', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['aluno__nome_completo']
