from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta

from alunos.models import Aluno
from matriculas.models import Matricula
from aulas.models import Aula
from instrutores.models import Instrutor
from financeiro.models import Parcela


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard administrativo."""
    template_name = 'dashboard/index.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_instrutor:
            return redirect('dashboard:instrutor')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()
        
        # KPIs
        context['total_alunos'] = Aluno.objects.count()
        context['matriculas_ativas'] = Matricula.objects.filter(
            status__in=['aberta', 'em_andamento', 'aguardando_exame']
        ).count()
        context['aulas_hoje'] = Aula.objects.filter(data=hoje).count()
        
        # Parcelas vencidas
        context['parcelas_vencidas'] = Parcela.objects.filter(
            status='aberta',
            data_vencimento__lt=hoje
        ).count()
        
        # Alertas de credenciais
        context['credenciais_vencer'] = Instrutor.objects.filter(
            data_vencimento_credencial__lte=hoje + timedelta(days=90),
            ativo=True
        ).order_by('data_vencimento_credencial')[:5]
        
        # Matriculas por status
        context['matriculas_por_status'] = Matricula.objects.values('status').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Ultimas matriculas
        context['ultimas_matriculas'] = Matricula.objects.select_related('aluno').order_by(
            '-data_matricula'
        )[:5]
        
        # Aulas de hoje
        context['aulas_do_dia'] = Aula.objects.filter(data=hoje).select_related(
            'matricula__aluno', 'instrutor__usuario'
        ).order_by('hora_inicio')[:10]
        
        return context


class DashboardInstrutorView(LoginRequiredMixin, TemplateView):
    """Dashboard mobile-first para instrutores."""
    template_name = 'dashboard/instrutor.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_instrutor:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()
        instrutor = self.request.user.instrutor
        
        # Aulas de hoje
        context['aulas_hoje'] = Aula.objects.filter(
            instrutor=instrutor,
            data=hoje
        ).select_related('matricula__aluno').order_by('hora_inicio')
        
        context['total_aulas_hoje'] = context['aulas_hoje'].count()
        
        # Proximos 3 dias
        context['proximas_aulas'] = Aula.objects.filter(
            instrutor=instrutor,
            data__gt=hoje,
            data__lte=hoje + timedelta(days=3)
        ).select_related('matricula__aluno').order_by('data', 'hora_inicio')[:10]
        
        # Alunos do instrutor
        matriculas_ids = Aula.objects.filter(
            instrutor=instrutor
        ).values_list('matricula_id', flat=True).distinct()
        
        context['meus_alunos'] = Matricula.objects.filter(
            id__in=matriculas_ids,
            status__in=['aberta', 'em_andamento', 'aguardando_exame']
        ).select_related('aluno')[:10]
        
        return context


class InstrutorMixin:
    """Mixin para views de instrutor - verifica permissão e fornece instrutor."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_instrutor:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get_instrutor(self):
        return self.request.user.instrutor


class InstrutorAlunosView(InstrutorMixin, TemplateView):
    """Lista de alunos do instrutor (mobile-first)."""
    template_name = 'dashboard/instrutor_alunos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrutor = self.get_instrutor()
        
        # Alunos com aulas agendadas com este instrutor
        matriculas_ids = Aula.objects.filter(
            instrutor=instrutor
        ).values_list('matricula_id', flat=True).distinct()
        
        context['alunos'] = Matricula.objects.filter(
            id__in=matriculas_ids
        ).select_related('aluno').order_by('aluno__nome_completo')
        
        return context


class InstrutorAgendaView(InstrutorMixin, TemplateView):
    """Agenda do instrutor (mobile-first)."""
    template_name = 'dashboard/instrutor_agenda.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrutor = self.get_instrutor()
        hoje = date.today()
        amanha = hoje + timedelta(days=1)
        
        context['hoje'] = hoje
        context['amanha'] = amanha
        
        # Aulas dos próximos 7 dias
        context['aulas'] = Aula.objects.filter(
            instrutor=instrutor,
            data__gte=hoje,
            data__lte=hoje + timedelta(days=7)
        ).select_related('matricula__aluno').order_by('data', 'hora_inicio')
        
        # Agrupar por data
        aulas_por_dia = {}
        for aula in context['aulas']:
            if aula.data not in aulas_por_dia:
                aulas_por_dia[aula.data] = []
            aulas_por_dia[aula.data].append(aula)
        context['aulas_por_dia'] = aulas_por_dia
        
        return context


class InstrutorPerfilView(InstrutorMixin, TemplateView):
    """Perfil do instrutor (mobile-first)."""
    template_name = 'dashboard/instrutor_perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instrutor = self.get_instrutor()
        context['instrutor'] = instrutor
        
        # Estatísticas
        hoje = date.today()
        context['total_aulas_mes'] = Aula.objects.filter(
            instrutor=instrutor,
            data__year=hoje.year,
            data__month=hoje.month,
            status='realizada'
        ).count()
        
        context['total_alunos'] = Aula.objects.filter(
            instrutor=instrutor
        ).values('matricula').distinct().count()
        
        return context
