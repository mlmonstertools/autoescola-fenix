from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from core.mixins import BreadcrumbMixin, AuditoriaMixin, InstrutorMixin
from .models import Aula
from matriculas.models import Matricula
from instrutores.models import Instrutor, Veiculo


class AulaListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Aula
    template_name = 'aulas/lista.html'
    context_object_name = 'aulas'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Aulas', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'matricula__aluno', 'instrutor__usuario', 'veiculo'
        )
        
        data = self.request.GET.get('data')
        status = self.request.GET.get('status')
        tipo = self.request.GET.get('tipo')
        instrutor = self.request.GET.get('instrutor')
        
        if data:
            queryset = queryset.filter(data=data)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if instrutor:
            queryset = queryset.filter(instrutor_id=instrutor)
        
        return queryset.order_by('-data', 'hora_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        context['hoje'] = hoje
        context['total_hoje'] = Aula.objects.filter(data=hoje).count()
        context['confirmadas_hoje'] = Aula.objects.filter(data=hoje, status='confirmada').count()
        context['realizadas_hoje'] = Aula.objects.filter(data=hoje, status='realizada').count()
        context['instrutores'] = Instrutor.objects.filter(ativo=True)
        return context


class AulaAgendaView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    """Visão de agenda/calendário."""
    model = Aula
    template_name = 'aulas/agenda.html'
    context_object_name = 'aulas'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Aulas', '/aulas/'), ('Agenda', None)]
    
    def get_queryset(self):
        data = self.request.GET.get('data', timezone.now().date())
        return Aula.objects.filter(data=data).select_related(
            'matricula__aluno', 'instrutor__usuario', 'veiculo'
        ).order_by('hora_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_selecionada'] = self.request.GET.get('data', timezone.now().date())
        context['instrutores'] = Instrutor.objects.filter(ativo=True)
        return context


class AulaCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Aula
    template_name = 'aulas/form.html'
    fields = ['matricula', 'instrutor', 'veiculo', 'data', 'hora_inicio', 'hora_fim', 'tipo', 'observacoes']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Aulas', '/aulas/'), ('Nova', None)]
    
    def get_initial(self):
        initial = super().get_initial()
        matricula_pk = self.request.GET.get('matricula')
        if matricula_pk:
            initial['matricula'] = matricula_pk
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matriculas'] = Matricula.objects.filter(
            status__in=['matriculado', 'em_andamento']
        ).select_related('aluno')
        context['instrutores'] = Instrutor.objects.filter(ativo=True)
        context['veiculos'] = Veiculo.objects.filter(ativo=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Aula agendada com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('aulas:lista')


class AulaUpdateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, UpdateView):
    model = Aula
    template_name = 'aulas/form.html'
    fields = ['instrutor', 'veiculo', 'data', 'hora_inicio', 'hora_fim', 'tipo', 'status', 'observacoes']
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Aulas', '/aulas/'),
            (f'Aula #{self.object.pk}', None)
        ]
    
    def form_valid(self, form):
        messages.success(self.request, 'Aula atualizada com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('aulas:lista')


class AulaRegistrarView(LoginRequiredMixin, View):
    """Registrar aula realizada."""
    
    def post(self, request, pk):
        aula = get_object_or_404(Aula, pk=pk)
        
        status = request.POST.get('status', 'realizada')
        km_inicial = request.POST.get('km_inicial')
        km_final = request.POST.get('km_final')
        avaliacao = request.POST.get('avaliacao')
        observacoes = request.POST.get('observacoes')
        
        aula.status = status
        if km_inicial:
            aula.km_inicial = int(km_inicial)
        if km_final:
            aula.km_final = int(km_final)
        if avaliacao:
            aula.avaliacao = int(avaliacao)
        if observacoes:
            aula.observacoes = observacoes
        
        aula.save()
        
        # Atualizar KM do veiculo
        if aula.veiculo and km_final:
            aula.veiculo.km_atual = int(km_final)
            aula.veiculo.save()
        
        messages.success(request, 'Aula registrada com sucesso!')
        
        # Redirecionar baseado no perfil
        if hasattr(request.user, 'instrutor'):
            return redirect('dashboard:instrutor')
        return redirect('aulas:lista')


class MinhasAulasView(LoginRequiredMixin, InstrutorMixin, ListView):
    """Aulas do instrutor logado."""
    model = Aula
    template_name = 'aulas/minhas_aulas.html'
    context_object_name = 'aulas'
    
    def get_queryset(self):
        instrutor = self.request.user.instrutor
        hoje = timezone.now().date()
        return Aula.objects.filter(
            instrutor=instrutor,
            data__gte=hoje
        ).select_related('matricula__aluno', 'veiculo').order_by('data', 'hora_inicio')
