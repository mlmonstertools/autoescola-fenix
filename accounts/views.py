from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import LoginForm, UsuarioUpdateForm


class CustomLoginView(LoginView):
    """View de login customizada."""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_instrutor:
            return reverse_lazy('dashboard:instrutor')
        return reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        messages.success(self.request, f'Bem-vindo, {form.get_user().get_short_name()}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """View de logout."""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Voce saiu do sistema.')
        return super().dispatch(request, *args, **kwargs)


class PerfilView(LoginRequiredMixin, UpdateView):
    """View de perfil do usuario."""
    template_name = 'accounts/perfil.html'
    form_class = UsuarioUpdateForm
    success_url = reverse_lazy('accounts:perfil')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)


class AlterarSenhaView(LoginRequiredMixin, PasswordChangeView):
    """View para alterar senha do usuario."""
    template_name = 'accounts/alterar_senha.html'
    success_url = reverse_lazy('accounts:perfil')
    
    def form_valid(self, form):
        messages.success(self.request, 'Senha alterada com sucesso!')
        return super().form_valid(form)
