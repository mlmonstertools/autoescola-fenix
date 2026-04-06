from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin customizado para Usuario."""
    
    list_display = ['email', 'nome_completo', 'telefone', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'groups']
    search_fields = ['email', 'nome_completo', 'telefone']
    ordering = ['nome_completo']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informacoes Pessoais'), {'fields': ('nome_completo', 'telefone', 'foto')}),
        (_('Permissoes'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_completo', 'password1', 'password2'),
        }),
    )
