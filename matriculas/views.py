from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from core.mixins import BreadcrumbMixin, AuditoriaMixin
from .models import Matricula, HistoricoStatus
from alunos.models import Aluno


class MatriculaListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Matricula
    template_name = 'matriculas/lista.html'
    context_object_name = 'matriculas'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Matriculas', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('aluno')
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        categoria = self.request.GET.get('categoria')
        
        if search:
            queryset = queryset.filter(
                Q(numero_processo__icontains=search) |
                Q(aluno__nome_completo__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        return queryset.order_by('-criado_em')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Matricula.objects.count()
        context['em_andamento'] = Matricula.objects.filter(status='em_andamento').count()
        context['aguardando_exame'] = Matricula.objects.filter(status='aguardando_exame').count()
        context['aprovados'] = Matricula.objects.filter(status='aprovado').count()
        context['mes_atual'] = Matricula.objects.filter(
            criado_em__month=timezone.now().month,
            criado_em__year=timezone.now().year
        ).count()
        return context


class MatriculaDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = Matricula
    template_name = 'matriculas/detalhe.html'
    context_object_name = 'matricula'
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Matriculas', '/matriculas/'),
            (self.object.numero_processo, None)
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matricula = self.object
        
        # Aulas
        context['aulas_teoricas'] = matricula.aulas.filter(tipo__startswith='teorica').order_by('-data')
        context['aulas_praticas'] = matricula.aulas.filter(tipo__startswith='pratica').order_by('-data')
        
        # Proximas aulas
        context['proximas_aulas'] = matricula.aulas.filter(
            data__gte=timezone.now().date(),
            status__in=['agendada', 'confirmada']
        ).order_by('data', 'hora_inicio')[:5]
        
        # Exames
        context['exames'] = matricula.exames.all().order_by('-data_agendamento')
        
        # Historico
        context['historico'] = HistoricoStatus.objects.filter(
            matricula=matricula
        ).order_by('-criado_em')
        
        return context


class MatriculaCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Matricula
    template_name = 'matriculas/form.html'
    fields = ['aluno', 'categoria', 'tipo_processo', 'modalidade', 'observacoes']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Matriculas', '/matriculas/'), ('Nova', None)]
    
    def get_initial(self):
        initial = super().get_initial()
        aluno_pk = self.request.GET.get('aluno')
        if aluno_pk:
            initial['aluno'] = aluno_pk
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alunos'] = Aluno.objects.filter(ativo=True).order_by('nome_completo')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Matricula criada com sucesso! Processo: {form.instance.numero_processo}')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('matriculas:detalhe', kwargs={'pk': self.object.pk})


class MatriculaUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Matricula
    template_name = 'matriculas/form.html'
    fields = ['categoria', 'tipo_processo', 'modalidade', 'status', 'instrutor_teorico', 'instrutor_pratico', 'observacoes']
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Matriculas', '/matriculas/'),
            (self.object.numero_processo, f'/matriculas/{self.object.pk}/'),
            ('Editar', None)
        ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Matricula atualizada com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('matriculas:detalhe', kwargs={'pk': self.object.pk})
