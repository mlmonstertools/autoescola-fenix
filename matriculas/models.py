from django.db import models
from django.utils import timezone
from datetime import date

from core.models import BaseModelComManager
from core.utils import gerar_numero_processo


class Matricula(BaseModelComManager):
    """
    Processo CNH do aluno.
    Uma matricula representa o processo completo para obter ou adicionar categoria.
    """
    CATEGORIA_CHOICES = [
        ('A', 'Categoria A'),
        ('B', 'Categoria B'),
        ('AB', 'Categorias A e B'),
        ('C', 'Categoria C'),
        ('D', 'Categoria D'),
        ('E', 'Categoria E'),
        ('ACC', 'ACC'),
    ]
    
    MODALIDADE_CHOICES = [
        ('CFCA', 'CFCA - Motos'),
        ('CFCB', 'CFCB - Carros'),
    ]
    
    TIPO_PROCESSO_CHOICES = [
        ('primeira_habilitacao', 'Primeira Habilitacao'),
        ('adicao_categoria', 'Adicao de Categoria'),
        ('renovacao', 'Renovacao'),
        ('mudanca_categoria', 'Mudanca de Categoria'),
        ('reabilitacao', 'Reabilitacao'),
    ]
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_exame', 'Aguardando Exame'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('concluida', 'Concluida'),
        ('cancelada', 'Cancelada'),
        ('bloqueada', 'Bloqueada'),
    ]
    
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.PROTECT, related_name='matriculas')
    numero_processo = models.CharField('numero do processo', max_length=15, unique=True, blank=True)
    
    categoria = models.CharField('categoria', max_length=5, choices=CATEGORIA_CHOICES)
    modalidade = models.CharField('modalidade', max_length=5, choices=MODALIDADE_CHOICES)
    tipo_processo = models.CharField('tipo de processo', max_length=25, choices=TIPO_PROCESSO_CHOICES)
    
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='aberta')
    data_matricula = models.DateField('data da matricula', default=date.today)
    data_conclusao = models.DateField('data de conclusao', null=True, blank=True)
    
    # Progresso
    aulas_teoricas_realizadas = models.PositiveIntegerField('aulas teoricas realizadas', default=0)
    aulas_praticas_realizadas = models.PositiveIntegerField('aulas praticas realizadas', default=0)
    
    # Requisitos minimos
    AULAS_TEORICAS_MINIMAS = 45
    AULAS_PRATICAS_MINIMAS = 20
    
    # Controle de bloqueio
    bloqueada_revisao = models.BooleanField('bloqueada para revisao', default=False)
    motivo_bloqueio = models.TextField('motivo do bloqueio', blank=True)
    
    observacoes = models.TextField('observacoes', blank=True)
    
    class Meta:
        verbose_name = 'matricula'
        verbose_name_plural = 'matriculas'
        ordering = ['-data_matricula']
    
    def __str__(self):
        return f'{self.numero_processo} - {self.aluno.nome_completo}'
    
    def save(self, *args, **kwargs):
        if not self.numero_processo:
            # Gera numero automatico
            ano = date.today().year
            ultimo = Matricula.all_objects.filter(
                numero_processo__startswith=f'{ano}-'
            ).order_by('-numero_processo').first()
            
            if ultimo:
                try:
                    seq = int(ultimo.numero_processo.split('-')[1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            
            self.numero_processo = gerar_numero_processo(ano, seq)
        super().save(*args, **kwargs)
    
    @property
    def progresso_teorico(self):
        return min(100, int((self.aulas_teoricas_realizadas / self.AULAS_TEORICAS_MINIMAS) * 100))
    
    @property
    def progresso_pratico(self):
        return min(100, int((self.aulas_praticas_realizadas / self.AULAS_PRATICAS_MINIMAS) * 100))
    
    @property
    def pode_agendar_exame_teorico(self):
        return self.aulas_teoricas_realizadas >= self.AULAS_TEORICAS_MINIMAS
    
    @property
    def pode_agendar_exame_pratico(self):
        return (
            self.aulas_praticas_realizadas >= self.AULAS_PRATICAS_MINIMAS and
            self.exame_teorico_aprovado
        )
    
    @property
    def exame_teorico_aprovado(self):
        return self.exames.filter(
            tipo='teorico_detran',
            resultado='aprovado'
        ).exists()


class HistoricoStatus(BaseModelComManager):
    """
    Historico de mudancas de status da matricula.
    """
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='historico_status')
    status_anterior = models.CharField('status anterior', max_length=20)
    status_novo = models.CharField('status novo', max_length=20)
    justificativa = models.TextField('justificativa')
    data_alteracao = models.DateTimeField('data da alteracao', auto_now_add=True)
    
    class Meta:
        verbose_name = 'historico de status'
        verbose_name_plural = 'historicos de status'
        ordering = ['-data_alteracao']
    
    def __str__(self):
        return f'{self.matricula.numero_processo}: {self.status_anterior} -> {self.status_novo}'
