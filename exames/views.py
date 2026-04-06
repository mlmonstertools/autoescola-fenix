from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from core.mixins import BreadcrumbMixin, AuditoriaMixin
from .models import Exame
from matriculas.models import Matricula


class ExameListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Exame
    template_name = 'exames/lista.html'
    context_object_name = 'exames'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Exames', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('matricula__aluno')
        search = self.request.GET.get('q')
        tipo = self.request.GET.get('tipo')
        resultado = self.request.GET.get('resultado')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        if search:
            queryset = queryset.filter(
                Q(matricula__aluno__nome_completo__icontains=search) |
                Q(matricula__numero_processo__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if resultado:
            queryset = queryset.filter(resultado=resultado)
        
        if data_inicio:
            queryset = queryset.filter(data_agendamento__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_agendamento__lte=data_fim)
        
        return queryset.order_by('-data_agendamento')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        context['agendados_hoje'] = Exame.objects.filter(data_agendamento=hoje).count()
        context['aprovados_mes'] = Exame.objects.filter(
            resultado='aprovado',
            data_agendamento__month=hoje.month,
            data_agendamento__year=hoje.year
        ).count()
        context['reprovados_mes'] = Exame.objects.filter(
            resultado='reprovado',
            data_agendamento__month=hoje.month,
            data_agendamento__year=hoje.year
        ).count()
        return context


class ExameCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Exame
    template_name = 'exames/form.html'
    fields = ['matricula', 'tipo', 'data_agendamento', 'hora', 'local', 'observacoes']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Exames', '/exames/'), ('Agendar', None)]
    
    def get_initial(self):
        initial = super().get_initial()
        matricula_pk = self.request.GET.get('matricula')
        if matricula_pk:
            initial['matricula'] = matricula_pk
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matriculas'] = Matricula.objects.filter(
            status__in=['em_andamento', 'aguardando_exame']
        ).select_related('aluno')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Exame agendado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('exames:lista')


class ExameUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Exame
    template_name = 'exames/form.html'
    fields = ['tipo', 'data', 'hora', 'local', 'resultado', 'observacoes']
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Exames', '/exames/'),
            (f'Exame #{self.object.pk}', None)
        ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Exame atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('exames:lista')


class ExameRegistrarResultadoView(LoginRequiredMixin, UpdateView):
    model = Exame
    template_name = 'exames/registrar_resultado.html'
    fields = ['resultado', 'observacoes']
    
    def form_valid(self, form):
        resultado = form.cleaned_data.get('resultado')
        if resultado == 'aprovado':
            messages.success(self.request, 'Resultado registrado: APROVADO!')
        elif resultado == 'reprovado':
            messages.warning(self.request, 'Resultado registrado: Reprovado')
        else:
            messages.info(self.request, 'Resultado registrado')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('exames:lista')
