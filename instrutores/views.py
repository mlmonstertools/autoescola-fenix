from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from core.mixins import BreadcrumbMixin, AuditoriaMixin
from .models import Instrutor, Veiculo


class InstrutorListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Instrutor
    template_name = 'instrutores/lista.html'
    context_object_name = 'instrutores'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Instrutores', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('usuario')
        search = self.request.GET.get('q')
        
        if search:
            queryset = queryset.filter(
                Q(usuario__nome_completo__icontains=search) |
                Q(numero_credencial__icontains=search)
            )
        
        return queryset.order_by('usuario__nome_completo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = Instrutor.objects.count()
        context['ativos'] = Instrutor.objects.filter(ativo=True).count()
        context['credenciais_vencendo'] = Instrutor.objects.filter(
            data_vencimento_credencial__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count()
        return context


class InstrutorDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = Instrutor
    template_name = 'instrutores/detalhe.html'
    context_object_name = 'instrutor'
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Instrutores', '/instrutores/'),
            (self.object.usuario.nome_completo, None)
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrutor = self.object
        hoje = timezone.now().date()
        
        # Aulas de hoje
        context['aulas_hoje'] = instrutor.aulas.filter(data=hoje).order_by('hora_inicio')
        
        # Proximas aulas
        context['proximas_aulas'] = instrutor.aulas.filter(
            data__gte=hoje,
            status__in=['agendada', 'confirmada']
        ).order_by('data', 'hora_inicio')[:10]
        
        # Alunos ativos
        context['alunos_ativos'] = instrutor.matriculas_pratico.filter(
            status__in=['matriculado', 'em_andamento']
        ).count()
        
        return context


class InstrutorCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Instrutor
    template_name = 'instrutores/form.html'
    fields = ['usuario', 'numero_credencial', 'data_emissao_credencial', 'data_vencimento_credencial', 'especialidades', 'numero_cnh', 'categoria_cnh', 'validade_cnh', 'cor_agenda']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Instrutores', '/instrutores/'), ('Novo', None)]
    success_url = reverse_lazy('instrutores:lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Instrutor cadastrado com sucesso!')
        return super().form_valid(form)


class InstrutorUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Instrutor
    template_name = 'instrutores/form.html'
    fields = ['numero_credencial', 'data_emissao_credencial', 'data_vencimento_credencial', 'especialidades', 'numero_cnh', 'categoria_cnh', 'validade_cnh', 'cor_agenda', 'ativo']
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Instrutores', '/instrutores/'),
            (self.object.usuario.nome_completo, f'/instrutores/{self.object.pk}/'),
            ('Editar', None)
        ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Instrutor atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('instrutores:detalhe', kwargs={'pk': self.object.pk})


# Veiculos
class VeiculoListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Veiculo
    template_name = 'instrutores/veiculos/lista.html'
    context_object_name = 'veiculos'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Veiculos', None)]
    
    def get_queryset(self):
        return super().get_queryset().order_by('placa')


class VeiculoCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Veiculo
    template_name = 'instrutores/veiculos/form.html'
    fields = ['placa', 'modelo', 'ano', 'categoria', 'km_atual']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Veiculos', '/instrutores/veiculos/'), ('Novo', None)]
    success_url = reverse_lazy('instrutores:veiculos_lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Veiculo cadastrado com sucesso!')
        return super().form_valid(form)


class VeiculoUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Veiculo
    template_name = 'instrutores/veiculos/form.html'
    fields = ['placa', 'modelo', 'ano', 'categoria', 'km_atual', 'ativo']
    success_url = reverse_lazy('instrutores:veiculos_lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Veiculo atualizado com sucesso!')
        return super().form_valid(form)
