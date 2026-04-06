from django.contrib import admin
from django.contrib.admin import AdminSite


class DiretorAdminSite(AdminSite):
    """
    Admin site customizado que restringe acesso apenas a Diretores.
    """
    site_header = 'Autoescola Fênix - Administração'
    site_title = 'Admin Autoescola'
    index_title = 'Painel de Administração'

    def has_permission(self, request):
        """
        Verifica se o usuário tem permissão para acessar o admin.
        Apenas usuários no grupo DIRETOR podem acessar.
        """
        user = request.user
        if not user.is_active:
            return False
        # Superusers sempre podem acessar, ou usuários que são diretores
        return user.is_superuser or getattr(user, 'is_diretor', False)


# Instância do admin customizado
diretor_admin_site = DiretorAdminSite(name='diretor_admin')


# Sobrescrever o admin site padrão
def _check_diretor_permission(self, request):
    """
    Verifica se o usuário pode acessar o admin.
    Apenas superusers ou diretores têm acesso.
    """
    user = request.user
    if not user.is_active:
        return False
    return user.is_superuser or getattr(user, 'is_diretor', False)


# Aplicar a verificação ao admin site padrão
admin.site.has_permission = lambda request: _check_diretor_permission(admin.site, request)
admin.site.site_header = 'Autoescola Fênix - Administração'
admin.site.site_title = 'Admin Autoescola'
admin.site.index_title = 'Painel de Administração'
