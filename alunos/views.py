from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

from core.mixins import BreadcrumbMixin, AuditoriaMixin, SoftDeleteMixin
from .models import Aluno, DocumentoAluno
from .forms import AlunoForm


class AlunoListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Aluno
    template_name = 'alunos/lista.html'
    context_object_name = 'alunos'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Alunos', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(nome_completo__icontains=search) |
                Q(cpf__icontains=search) |
                Q(email__icontains=search) |
                Q(telefone__icontains=search)
            )
        
        if status == 'ativo':
            queryset = queryset.filter(ativo=True)
        elif status == 'inativo':
            queryset = queryset.filter(ativo=False)
        
        return queryset.order_by('-criado_em')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_alunos'] = Aluno.objects.count()
        context['total_ativos'] = Aluno.objects.filter(ativo=True).count()
        context['total_matriculados'] = Aluno.objects.filter(matriculas__isnull=False).distinct().count()
        context['cadastrados_mes'] = Aluno.objects.filter(
            criado_em__month=timezone.now().month,
            criado_em__year=timezone.now().year
        ).count()
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['alunos/partials/tabela.html']
        return ['alunos/lista.html']


class AlunoDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = Aluno
    template_name = 'alunos/detalhe.html'
    context_object_name = 'aluno'
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Alunos', '/alunos/'),
            (self.object.nome_completo, None)
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = self.object
        
        # Matricula ativa
        matricula_ativa = aluno.matriculas.filter(
            status__in=['em_andamento', 'matriculado']
        ).first()
        context['matricula_ativa'] = matricula_ativa
        
        # Proximas aulas
        if matricula_ativa:
            from aulas.models import Aula
            context['proximas_aulas'] = Aula.objects.filter(
                matricula=matricula_ativa,
                data__gte=timezone.now().date(),
                status__in=['agendada', 'confirmada']
            ).order_by('data', 'hora_inicio')[:5]
        
        return context


class AlunoCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/form.html'
    success_url = reverse_lazy('alunos:lista')
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Alunos', '/alunos/'), ('Novo Aluno', None)]
    
    def form_valid(self, form):
        form.instance.data_consentimento = timezone.now() if form.instance.consentimento_lgpd else None
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return super().form_valid(form)


class AlunoUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/form.html'
    
    def get_success_url(self):
        return reverse_lazy('alunos:detalhe', kwargs={'pk': self.object.pk})
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Alunos', '/alunos/'),
            (self.object.nome_completo, f'/alunos/{self.object.pk}/'),
            ('Editar', None)
        ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Aluno atualizado com sucesso!')
        return super().form_valid(form)


class AlunoDeleteView(LoginRequiredMixin, SoftDeleteMixin, BreadcrumbMixin, DeleteView):
    model = Aluno
    template_name = 'alunos/confirmar_exclusao.html'
    success_url = reverse_lazy('alunos:lista')


class AlunoBuscaView(LoginRequiredMixin, ListView):
    """View para busca HTMX."""
    model = Aluno
    template_name = 'alunos/partials/lista_items.html'
    context_object_name = 'alunos'
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if len(query) >= 2:
            return Aluno.objects.filter(
                Q(nome_completo__icontains=query) |
                Q(cpf__icontains=query)
            )[:10]
        return Aluno.objects.none()
