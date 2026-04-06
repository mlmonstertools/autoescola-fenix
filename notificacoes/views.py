from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

from core.mixins import BreadcrumbMixin
from .models import TemplateMensagem, LogNotificacao, enviar_notificacao
from alunos.models import Aluno


class TemplateListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = TemplateMensagem
    template_name = 'notificacoes/lista.html'
    context_object_name = 'templates'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Notificacoes', None)]


class TemplateCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):
    model = TemplateMensagem
    template_name = 'notificacoes/form.html'
    fields = ['tipo', 'titulo', 'conteudo']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Notificacoes', '/notificacoes/'), ('Novo Template', None)]
    success_url = reverse_lazy('notificacoes:templates')
    
    def form_valid(self, form):
        messages.success(self.request, 'Template criado com sucesso!')
        return super().form_valid(form)


class LogListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = LogNotificacao
    template_name = 'notificacoes/logs.html'
    context_object_name = 'logs'
    paginate_by = 50
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Notificacoes', '/notificacoes/'), ('Logs', None)]
    
    def get_queryset(self):
        return super().get_queryset().select_related('aluno').order_by('-criado_em')


class EnviarNotificacaoView(LoginRequiredMixin, View):
    """View para enviar notificação direta."""
    
    def get(self, request, aluno_pk, template_codigo):
        aluno = get_object_or_404(Aluno, pk=aluno_pk)
        template = get_object_or_404(TemplateMensagem, codigo=template_codigo)
        
        # Renderizar preview da mensagem
        return render(request, 'notificacoes/enviar.html', {
            'aluno': aluno,
            'template': template
        })
    
    def post(self, request, aluno_pk, template_codigo):
        aluno = get_object_or_404(Aluno, pk=aluno_pk)
        
        sucesso = enviar_notificacao(
            aluno=aluno,
            template_codigo=template_codigo,
            dados_extras={}
        )
        
        if sucesso:
            messages.success(request, 'Notificacao enviada com sucesso!')
        else:
            messages.error(request, 'Erro ao enviar notificacao')
        
        return redirect('alunos:detalhe', pk=aluno_pk)


class EnviarLembreteAulaView(LoginRequiredMixin, View):
    """Envia lembrete de aula para aluno."""
    
    def post(self, request, aula_pk):
        from aulas.models import Aula
        aula = get_object_or_404(Aula, pk=aula_pk)
        
        sucesso = enviar_notificacao(
            aluno=aula.matricula.aluno,
            template_codigo='lembrete_aula',
            dados_extras={
                'data_aula': aula.data.strftime('%d/%m/%Y'),
                'hora_aula': aula.hora_inicio.strftime('%H:%M'),
                'tipo_aula': aula.get_tipo_display()
            }
        )
        
        if sucesso:
            messages.success(request, 'Lembrete enviado!')
        else:
            messages.error(request, 'Erro ao enviar lembrete')
        
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:index'))
