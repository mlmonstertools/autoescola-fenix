from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from core.mixins import BreadcrumbMixin, AuditoriaMixin
from .models import Contrato, Parcela, CaixaDiario, MovimentoCaixa, LogFinanceiro
from matriculas.models import Matricula


class FinanceiroDashboardView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'financeiro/dashboard.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Financeiro', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # Parcelas vencidas
        context['parcelas_vencidas'] = Parcela.objects.filter(
            status='pendente',
            data_vencimento__lt=hoje
        ).count()
        
        # Total a receber
        context['total_a_receber'] = Parcela.objects.filter(
            status='pendente'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        # Recebido no mes
        context['recebido_mes'] = Parcela.objects.filter(
            status='pago',
            data_pagamento__month=hoje.month,
            data_pagamento__year=hoje.year
        ).aggregate(total=Sum('valor_pago'))['total'] or Decimal('0')
        
        # Parcelas do dia
        context['parcelas_hoje'] = Parcela.objects.filter(
            data_vencimento=hoje,
            status='pendente'
        ).select_related('contrato__matricula__aluno')[:10]
        
        # Parcelas vencidas lista
        context['lista_vencidas'] = Parcela.objects.filter(
            status='pendente',
            data_vencimento__lt=hoje
        ).select_related('contrato__matricula__aluno').order_by('data_vencimento')[:10]
        
        return context


class ContratoListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Contrato
    template_name = 'financeiro/contratos.html'
    context_object_name = 'contratos'
    paginate_by = 20
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Financeiro', '/financeiro/'), ('Contratos', None)]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('matricula__aluno')
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(matricula__aluno__nome_completo__icontains=search) |
                Q(matricula__numero_processo__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-criado_em')


class ContratoDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = Contrato
    template_name = 'financeiro/contrato_detalhe.html'
    context_object_name = 'contrato'
    
    def get_breadcrumbs(self):
        return [
            ('Dashboard', '/dashboard/'),
            ('Financeiro', '/financeiro/'),
            ('Contratos', '/financeiro/contratos/'),
            (f'Contrato #{self.object.pk}', None)
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parcelas'] = self.object.parcelas.all().order_by('numero')
        context['logs'] = LogFinanceiro.objects.filter(
            contrato=self.object
        ).order_by('-criado_em')[:20]
        return context


class ContratoCreateView(LoginRequiredMixin, AuditoriaMixin, BreadcrumbMixin, CreateView):
    model = Contrato
    template_name = 'financeiro/contrato_form.html'
    fields = ['matricula', 'valor_total', 'desconto', 'valor_entrada', 'numero_parcelas', 'dia_vencimento', 'data_contrato', 'observacoes']
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Financeiro', '/financeiro/'), ('Novo Contrato', None)]
    
    def get_initial(self):
        initial = super().get_initial()
        matricula_pk = self.request.GET.get('matricula')
        if matricula_pk:
            initial['matricula'] = matricula_pk
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matriculas'] = Matricula.objects.filter(
            contrato__isnull=True
        ).select_related('aluno')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Contrato criado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('financeiro:contrato_detalhe', kwargs={'pk': self.object.pk})


class ParcelaRegistrarPagamentoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        parcela = get_object_or_404(Parcela, pk=pk)
        
        valor_pago = request.POST.get('valor_pago')
        forma_pagamento = request.POST.get('forma_pagamento', 'dinheiro')
        
        if valor_pago:
            parcela.registrar_pagamento(
                valor=Decimal(valor_pago),
                usuario=request.user,
                forma_pagamento=forma_pagamento
            )
            messages.success(request, f'Pagamento de R$ {valor_pago} registrado com sucesso!')
        else:
            messages.error(request, 'Informe o valor do pagamento')
        
        return redirect('financeiro:contrato_detalhe', pk=parcela.contrato.pk)


class CaixaDiarioView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'financeiro/caixa.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Financeiro', '/financeiro/'), ('Caixa', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # Caixa de hoje
        caixa, created = CaixaDiario.objects.get_or_create(data=hoje)
        context['caixa'] = caixa
        
        # Movimentos de hoje
        context['movimentos'] = MovimentoCaixa.objects.filter(
            caixa=caixa
        ).order_by('-criado_em')
        
        return context


class CaixaMovimentoCreateView(LoginRequiredMixin, CreateView):
    model = MovimentoCaixa
    template_name = 'financeiro/caixa_movimento_form.html'
    fields = ['tipo', 'valor', 'descricao', 'categoria']
    
    def form_valid(self, form):
        hoje = timezone.now().date()
        caixa, _ = CaixaDiario.objects.get_or_create(data=hoje)
        form.instance.caixa = caixa
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Movimento registrado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('financeiro:caixa')
