from django.db import models
from django.core.exceptions import ValidationError

from core.models import BaseModelComManager


class Exame(BaseModelComManager):
    """
    Exames do processo CNH.
    Psicotecnico, medico e exames DETRAN.
    """
    TIPO_CHOICES = [
        ('psicotecnico', 'Psicotecnico'),
        ('medico', 'Exame Medico'),
        ('teorico_detran', 'Exame Teorico - DETRAN'),
        ('pratico_detran', 'Exame Pratico - DETRAN'),
    ]
    
    RESULTADO_CHOICES = [
        ('agendado', 'Agendado'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('ausente', 'Ausente'),
        ('cancelado', 'Cancelado'),
    ]
    
    matricula = models.ForeignKey(
        'matriculas.Matricula',
        on_delete=models.CASCADE,
        related_name='exames'
    )
    
    tipo = models.CharField('tipo', max_length=20, choices=TIPO_CHOICES)
    resultado = models.CharField('resultado', max_length=15, choices=RESULTADO_CHOICES, default='agendado')
    
    data_agendamento = models.DateField('data de agendamento')
    hora = models.TimeField('hora', null=True, blank=True)
    local = models.CharField('local', max_length=255, blank=True)
    
    data_resultado = models.DateField('data do resultado', null=True, blank=True)
    observacoes = models.TextField('observacoes', blank=True)
    
    # Limite de tentativas
    MAX_REPROVACOES_TEORICO = 3
    MAX_REPROVACOES_PRATICO = 2
    
    class Meta:
        verbose_name = 'exame'
        verbose_name_plural = 'exames'
        ordering = ['-data_agendamento']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.matricula.aluno.nome_completo}'
    
    def clean(self):
        super().clean()
        
        matricula = self.matricula
        
        # Valida pre-requisito para exame teorico
        if self.tipo == 'teorico_detran':
            if not matricula.pode_agendar_exame_teorico:
                raise ValidationError(
                    f'Aluno precisa de {matricula.AULAS_TEORICAS_MINIMAS} aulas teoricas para agendar exame. '
                    f'Atual: {matricula.aulas_teoricas_realizadas}'
                )
            
            # Verifica bloqueio por reprovacoes
            reprovacoes = matricula.exames.filter(
                tipo='teorico_detran',
                resultado='reprovado'
            ).count()
            if reprovacoes >= self.MAX_REPROVACOES_TEORICO and not matricula.bloqueada_revisao:
                raise ValidationError(
                    f'Aluno atingiu limite de {self.MAX_REPROVACOES_TEORICO} reprovacoes no exame teorico. '
                    'Necessario revisao manual.'
                )
        
        # Valida pre-requisito para exame pratico
        if self.tipo == 'pratico_detran':
            if not matricula.pode_agendar_exame_pratico:
                if not matricula.exame_teorico_aprovado:
                    raise ValidationError('Aluno precisa ser aprovado no exame teorico primeiro.')
                raise ValidationError(
                    f'Aluno precisa de {matricula.AULAS_PRATICAS_MINIMAS} aulas praticas para agendar exame. '
                    f'Atual: {matricula.aulas_praticas_realizadas}'
                )
            
            # Verifica bloqueio por reprovacoes
            reprovacoes = matricula.exames.filter(
                tipo='pratico_detran',
                resultado='reprovado'
            ).count()
            if reprovacoes >= self.MAX_REPROVACOES_PRATICO and not matricula.bloqueada_revisao:
                raise ValidationError(
                    f'Aluno atingiu limite de {self.MAX_REPROVACOES_PRATICO} reprovacoes no exame pratico. '
                    'Necessario revisao manual.'
                )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Verifica se deve bloquear matricula por excesso de reprovacoes
        if self.resultado == 'reprovado':
            matricula = self.matricula
            
            if self.tipo == 'teorico_detran':
                reprovacoes = matricula.exames.filter(
                    tipo='teorico_detran',
                    resultado='reprovado'
                ).count()
                if reprovacoes >= self.MAX_REPROVACOES_TEORICO:
                    matricula.bloqueada_revisao = True
                    matricula.motivo_bloqueio = f'Atingiu limite de {self.MAX_REPROVACOES_TEORICO} reprovacoes no exame teorico.'
                    matricula.status = 'bloqueada'
                    matricula.save()
            
            elif self.tipo == 'pratico_detran':
                reprovacoes = matricula.exames.filter(
                    tipo='pratico_detran',
                    resultado='reprovado'
                ).count()
                if reprovacoes >= self.MAX_REPROVACOES_PRATICO:
                    matricula.bloqueada_revisao = True
                    matricula.motivo_bloqueio = f'Atingiu limite de {self.MAX_REPROVACOES_PRATICO} reprovacoes no exame pratico.'
                    matricula.status = 'bloqueada'
                    matricula.save()
