from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from core.models import BaseModelComManager


class Aula(BaseModelComManager):
    """
    Aulas teoricas e praticas da autoescola.
    """
    TIPO_CHOICES = [
        ('teorica', 'Teorica'),
        ('pratica_simulador', 'Pratica - Simulador'),
        ('pratica_via_publica', 'Pratica - Via Publica'),
        ('direcao_defensiva', 'Direcao Defensiva'),
        ('primeiros_socorros', 'Primeiros Socorros'),
    ]
    
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('falta_aluno', 'Falta do Aluno'),
        ('falta_instrutor', 'Falta do Instrutor'),
        ('cancelada', 'Cancelada'),
        ('remarcada', 'Remarcada'),
    ]
    
    matricula = models.ForeignKey(
        'matriculas.Matricula',
        on_delete=models.CASCADE,
        related_name='aulas'
    )
    instrutor = models.ForeignKey(
        'instrutores.Instrutor',
        on_delete=models.PROTECT,
        related_name='aulas'
    )
    veiculo = models.ForeignKey(
        'instrutores.Veiculo',
        on_delete=models.PROTECT,
        related_name='aulas',
        null=True,
        blank=True
    )
    
    tipo = models.CharField('tipo', max_length=25, choices=TIPO_CHOICES)
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='agendada')
    
    data = models.DateField('data')
    hora_inicio = models.TimeField('hora de inicio')
    hora_fim = models.TimeField('hora de fim')
    
    # Registro da aula (preenchido apos realizacao)
    km_inicial = models.PositiveIntegerField('KM inicial', null=True, blank=True)
    km_final = models.PositiveIntegerField('KM final', null=True, blank=True)
    avaliacao = models.PositiveSmallIntegerField(
        'avaliacao',
        null=True,
        blank=True,
        help_text='Nota de 1 a 10'
    )
    observacoes = models.TextField('observacoes', blank=True)
    
    class Meta:
        verbose_name = 'aula'
        verbose_name_plural = 'aulas'
        ordering = ['data', 'hora_inicio']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.matricula.aluno.nome_completo} - {self.data}'
    
    def clean(self):
        super().clean()
        
        # Valida duracao da aula pratica
        if self.tipo.startswith('pratica'):
            duracao = self.duracao_minutos
            if duracao < 50:
                raise ValidationError('Aula pratica deve ter no minimo 50 minutos.')
            if duracao > 90:
                raise ValidationError('Aula pratica deve ter no maximo 90 minutos.')
        
        # Valida avaliacao
        if self.avaliacao is not None and (self.avaliacao < 1 or self.avaliacao > 10):
            raise ValidationError({'avaliacao': 'Avaliacao deve ser entre 1 e 10.'})
        
        # Valida conflito de horario do instrutor
        if self.pk is None:
            conflitos = Aula.objects.filter(
                instrutor=self.instrutor,
                data=self.data,
                status__in=['agendada', 'confirmada']
            ).exclude(pk=self.pk)
            
            for aula in conflitos:
                if self._horarios_sobrepostos(aula):
                    raise ValidationError(
                        f'Instrutor ja tem aula agendada neste horario ({aula.hora_inicio} - {aula.hora_fim}).'
                    )
        
        # Valida conflito de veiculo
        if self.veiculo and self.pk is None:
            conflitos_veiculo = Aula.objects.filter(
                veiculo=self.veiculo,
                data=self.data,
                status__in=['agendada', 'confirmada']
            ).exclude(pk=self.pk)
            
            for aula in conflitos_veiculo:
                if self._horarios_sobrepostos(aula):
                    raise ValidationError(
                        f'Veiculo ja esta em uso neste horario ({aula.hora_inicio} - {aula.hora_fim}).'
                    )
    
    def _horarios_sobrepostos(self, outra_aula):
        """Verifica se dois horarios se sobrepoem."""
        return (
            (self.hora_inicio < outra_aula.hora_fim and self.hora_fim > outra_aula.hora_inicio)
        )
    
    @property
    def duracao_minutos(self):
        """Retorna duracao da aula em minutos."""
        inicio = timedelta(hours=self.hora_inicio.hour, minutes=self.hora_inicio.minute)
        fim = timedelta(hours=self.hora_fim.hour, minutes=self.hora_fim.minute)
        return int((fim - inicio).total_seconds() / 60)
    
    @property
    def km_rodado(self):
        if self.km_inicial and self.km_final:
            return self.km_final - self.km_inicial
        return 0
    
    @property
    def is_pratica(self):
        return self.tipo.startswith('pratica')
    
    def registrar_aula(self, status, km_inicial=None, km_final=None, avaliacao=None, observacoes=''):
        """Registra a aula como realizada ou falta."""
        self.status = status
        if self.is_pratica:
            self.km_inicial = km_inicial
            self.km_final = km_final
        self.avaliacao = avaliacao
        self.observacoes = observacoes
        self.save()
        
        # Atualiza contagem na matricula
        if status == 'realizada':
            matricula = self.matricula
            if self.tipo == 'teorica':
                matricula.aulas_teoricas_realizadas += 1
            elif self.is_pratica:
                matricula.aulas_praticas_realizadas += 1
            matricula.save()
            
            # Atualiza km do veiculo
            if self.veiculo and self.km_final:
                self.veiculo.km_atual = self.km_final
                self.veiculo.save()
