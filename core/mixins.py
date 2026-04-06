from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class BaseViewMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Mixin base que combina login obrigatorio e verificacao de permissao.
    Todas as views devem herdar deste mixin.
    """
    login_url = 'accounts:login'
    raise_exception = False
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        messages.error(self.request, 'Voce nao tem permissao para acessar esta pagina.')
        return redirect('dashboard:index')


class InstrutorMixin:
    """
    Mixin para views de instrutor.
    Filtra automaticamente pelo instrutor logado.
    """
    
    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'instrutor'):
            return qs.filter(instrutor=self.request.user.instrutor)
        return qs.none()


class AuditoriaMixin:
    """
    Mixin para salvar usuario que criou/modificou o registro.
    """
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.pk:
            obj.criado_por = self.request.user
        obj.save()
        return super().form_valid(form)


class SoftDeleteMixin:
    """
    Mixin para usar soft delete ao inves de delete real.
    """
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        success_url = self.get_success_url()
        messages.success(request, 'Registro removido com sucesso.')
        return redirect(success_url)


class BreadcrumbMixin:
    """
    Mixin para adicionar breadcrumbs ao contexto.
    Define breadcrumbs como lista de tuplas (nome, url).
    """
    breadcrumbs = []
    
    def get_breadcrumbs(self):
        return self.breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
