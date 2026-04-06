from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.utils import timezone
from decimal import Decimal

from core.mixins import BreadcrumbMixin
from alunos.models import Aluno
from matriculas.models import Matricula
from aulas.models import Aula
from exames.models import Exame
from financeiro.models import Parcela, Contrato
from .pdf_utils import render_pdf_template


class RelatoriosIndexView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/index.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', None)]


class RelatorioAlunosView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/alunos.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', '/relatorios/'), ('Alunos', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = int(self.request.GET.get('ano', timezone.now().year))
        
        # Cadastros por mes
        context['cadastros_mes'] = []
        for mes in range(1, 13):
            total = Aluno.objects.filter(
                criado_em__year=ano,
                criado_em__month=mes
            ).count()
            context['cadastros_mes'].append({'mes': mes, 'total': total})
        
        context['total_alunos'] = Aluno.objects.count()
        context['alunos_ativos'] = Aluno.objects.filter(ativo=True).count()
        context['ano'] = ano
        context['titulo'] = f'Relatorio de Alunos - {ano}'
        context['data_geracao'] = timezone.now()
        
        return context
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data()
            return render_pdf_template(
                request,
                'relatorios/pdf/alunos.html',
                context,
                f'relatorio_alunos_{context["ano"]}.pdf'
            )
        return super().get(request, *args, **kwargs)


class RelatorioMatriculasView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/matriculas.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', '/relatorios/'), ('Matriculas', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Por status
        context['por_status'] = Matricula.objects.values('status').annotate(
            total=Count('id')
        ).order_by('status')
        
        # Por categoria
        context['por_categoria'] = Matricula.objects.values('categoria').annotate(
            total=Count('id')
        ).order_by('categoria')
        
        context['titulo'] = 'Relatorio de Matriculas'
        context['data_geracao'] = timezone.now()
        
        return context
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data()
            return render_pdf_template(
                request,
                'relatorios/pdf/matriculas.html',
                context,
                'relatorio_matriculas.pdf'
            )
        return super().get(request, *args, **kwargs)


class RelatorioFinanceiroView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/financeiro.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', '/relatorios/'), ('Financeiro', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # Recebido no mes
        context['recebido_mes'] = Parcela.objects.filter(
            status='paga',
            data_pagamento__month=hoje.month,
            data_pagamento__year=hoje.year
        ).aggregate(total=Sum('valor_pago'))['total'] or Decimal('0')
        
        # A receber no mes
        context['a_receber_mes'] = Parcela.objects.filter(
            status='aberta',
            data_vencimento__month=hoje.month,
            data_vencimento__year=hoje.year
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        # Inadimplencia
        context['total_vencido'] = Parcela.objects.filter(
            status__in=['aberta', 'vencida'],
            data_vencimento__lt=hoje
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        # Contratos ativos
        context['contratos_ativos'] = Contrato.objects.filter(ativo=True).count()
        
        context['titulo'] = 'Relatorio Financeiro'
        context['data_geracao'] = timezone.now()
        
        return context
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data()
            return render_pdf_template(
                request,
                'relatorios/pdf/financeiro.html',
                context,
                'relatorio_financeiro.pdf'
            )
        return super().get(request, *args, **kwargs)


class RelatorioExamesView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/exames.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', '/relatorios/'), ('Exames', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aprovacoes
        context['total_teorico_aprovado'] = Exame.objects.filter(
            tipo='teorico_detran', resultado='aprovado'
        ).count()
        context['total_teorico_reprovado'] = Exame.objects.filter(
            tipo='teorico_detran', resultado='reprovado'
        ).count()
        context['total_pratico_aprovado'] = Exame.objects.filter(
            tipo='pratico_detran', resultado='aprovado'
        ).count()
        context['total_pratico_reprovado'] = Exame.objects.filter(
            tipo='pratico_detran', resultado='reprovado'
        ).count()
        
        context['titulo'] = 'Relatorio de Exames'
        context['data_geracao'] = timezone.now()
        
        return context
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data()
            return render_pdf_template(
                request,
                'relatorios/pdf/exames.html',
                context,
                'relatorio_exames.pdf'
            )
        return super().get(request, *args, **kwargs)


class RelatorioInstrutoresView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'relatorios/instrutores.html'
    breadcrumbs = [('Dashboard', '/dashboard/'), ('Relatorios', '/relatorios/'), ('Instrutores', None)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        # Aulas por instrutor no mes
        from instrutores.models import Instrutor
        context['aulas_instrutor'] = []
        for instrutor in Instrutor.objects.filter(ativo=True):
            total = instrutor.aulas.filter(
                data__month=hoje.month,
                data__year=hoje.year,
                status='realizada'
            ).count()
            context['aulas_instrutor'].append({
                'instrutor': instrutor,
                'total': total
            })
        
        context['titulo'] = 'Relatorio de Instrutores'
        context['data_geracao'] = timezone.now()
        
        return context
    
    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'pdf':
            context = self.get_context_data()
            return render_pdf_template(
                request,
                'relatorios/pdf/instrutores.html',
                context,
                'relatorio_instrutores.pdf'
            )
        return super().get(request, *args, **kwargs)
