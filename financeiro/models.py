from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from core.models import BaseModelComManager
from core.utils import calcular_multa, calcular_juros_pro_rata, calcular_valor_corrigido


class Contrato(BaseModelComManager):
    """
    Contrato financeiro da matricula.
    Define valor total, desconto e forma de pagamento.
    """
    matricula = models.OneToOneField(
        'matriculas.Matricula',
        on_delete=models.PROTECT,
        related_name='contrato'
    )
    
    valor_total = models.DecimalField(
        'valor total',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    desconto = models.DecimalField(
        'desconto',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    valor_entrada = models.DecimalField(
        'valor de entrada',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    numero_parcelas = models.PositiveSmallIntegerField(
        'numero de parcelas',
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    dia_vencimento = models.PositiveSmallIntegerField(
        'dia de vencimento',
        validators=[MinValueValidator(1), MaxValueValidator(28)]
    )
    
    data_contrato = models.DateField('data do contrato', default=date.today)
    observacoes = models.TextField('observacoes', blank=True)
    
    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
        ordering = ['-data_contrato']
    
    def __str__(self):
        return f'Contrato {self.matricula.numero_processo}'
    
    @property
    def valor_liquido(self):
        return self.valor_total - self.desconto
    
    @property
    def valor_a_parcelar(self):
        return self.valor_liquido - self.valor_entrada
    
    @property
    def valor_parcela(self):
        if self.numero_parcelas == 0:
            return Decimal('0.00')
        return (self.valor_a_parcelar / self.numero_parcelas).quantize(Decimal('0.01'))
    
    @property
    def valor_pago(self):
        return sum(p.valor_pago or Decimal('0') for p in self.parcelas.filter(status='paga'))
    
    @property
    def valor_pendente(self):
        return self.valor_liquido - self.valor_pago
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Gera parcelas automaticamente ao criar contrato
        if is_new and self.numero_parcelas > 0:
            self._gerar_parcelas()
    
    def _gerar_parcelas(self):
        """Gera as parcelas do contrato."""
        valor_parcela = self.valor_parcela
        data_vencimento = self._calcular_primeiro_vencimento()
        
        for i in range(1, self.numero_parcelas + 1):
            Parcela.objects.create(
                contrato=self,
                numero=i,
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                criado_por=self.criado_por
            )
            # Proximo mes
            if data_vencimento.month == 12:
                data_vencimento = date(data_vencimento.year + 1, 1, self.dia_vencimento)
            else:
                try:
                    data_vencimento = date(data_vencimento.year, data_vencimento.month + 1, self.dia_vencimento)
                except ValueError:
                    # Dia nao existe no mes (ex: 31 em fevereiro)
                    data_vencimento = date(data_vencimento.year, data_vencimento.month + 2, 1) - timedelta(days=1)
    
    def _calcular_primeiro_vencimento(self):
        """Calcula a data do primeiro vencimento."""
        hoje = date.today()
        if hoje.day <= self.dia_vencimento:
            return date(hoje.year, hoje.month, self.dia_vencimento)
        else:
            if hoje.month == 12:
                return date(hoje.year + 1, 1, self.dia_vencimento)
            return date(hoje.year, hoje.month + 1, self.dia_vencimento)


class Parcela(BaseModelComManager):
    """
    Parcela de pagamento do contrato.
    """
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('paga', 'Paga'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.PROTECT,
        related_name='parcelas'
    )
    numero = models.PositiveSmallIntegerField('numero')
    valor = models.DecimalField(
        'valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    data_vencimento = models.DateField('data de vencimento')
    
    status = models.CharField('status', max_length=15, choices=STATUS_CHOICES, default='aberta')
    
    # Pagamento
    valor_pago = models.DecimalField(
        'valor pago',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    data_pagamento = models.DateField('data do pagamento', null=True, blank=True)
    forma_pagamento = models.CharField('forma de pagamento', max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'parcela'
        verbose_name_plural = 'parcelas'
        ordering = ['contrato', 'numero']
        unique_together = ['contrato', 'numero']
    
    def __str__(self):
        return f'{self.contrato} - Parcela {self.numero}/{self.contrato.numero_parcelas}'
    
    @property
    def vencida(self):
        return self.status == 'aberta' and self.data_vencimento < date.today()
    
    @property
    def dias_atraso(self):
        if self.data_vencimento < date.today() and self.status == 'aberta':
            return (date.today() - self.data_vencimento).days
        return 0
    
    @property
    def multa(self):
        if self.dias_atraso > 0:
            return calcular_multa(self.valor)
        return Decimal('0.00')
    
    @property
    def juros(self):
        if self.dias_atraso > 0:
            return calcular_juros_pro_rata(self.valor, self.dias_atraso)
        return Decimal('0.00')
    
    @property
    def valor_corrigido(self):
        if self.dias_atraso > 0:
            return calcular_valor_corrigido(self.valor, self.dias_atraso)['total']
        return self.valor
    
    def registrar_pagamento(self, valor_pago, data_pagamento=None, forma_pagamento=''):
        """Registra o pagamento da parcela."""
        self.valor_pago = valor_pago
        self.data_pagamento = data_pagamento or date.today()
        self.forma_pagamento = forma_pagamento
        self.status = 'paga'
        self.save()


class CaixaDiario(BaseModelComManager):
    """
    Controle de caixa diario.
    """
    data = models.DateField('data', unique=True)
    saldo_inicial = models.DecimalField(
        'saldo inicial',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fechado = models.BooleanField('fechado', default=False)
    data_fechamento = models.DateTimeField('data de fechamento', null=True, blank=True)
    fechado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='caixas_fechados'
    )
    
    class Meta:
        verbose_name = 'caixa diario'
        verbose_name_plural = 'caixas diarios'
        ordering = ['-data']
    
    def __str__(self):
        status = 'Fechado' if self.fechado else 'Aberto'
        return f'Caixa {self.data.strftime("%d/%m/%Y")} - {status}'
    
    @property
    def total_entradas(self):
        return sum(m.valor for m in self.movimentos.filter(tipo='entrada'))
    
    @property
    def total_saidas(self):
        return sum(m.valor for m in self.movimentos.filter(tipo='saida'))
    
    @property
    def saldo_final(self):
        return self.saldo_inicial + self.total_entradas - self.total_saidas
    
    def fechar(self, usuario):
        """Fecha o caixa do dia."""
        self.fechado = True
        self.data_fechamento = timezone.now()
        self.fechado_por = usuario
        self.save()


class MovimentoCaixa(BaseModelComManager):
    """
    Movimentos de entrada e saida do caixa.
    """
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saida'),
    ]
    
    CATEGORIA_CHOICES = [
        ('mensalidade', 'Mensalidade'),
        ('parcela', 'Parcela de Contrato'),
        ('taxa_exame', 'Taxa de Exame'),
        ('material', 'Material Didatico'),
        ('despesa_operacional', 'Despesa Operacional'),
        ('salario', 'Salario'),
        ('combustivel', 'Combustivel'),
        ('manutencao', 'Manutencao'),
        ('outros', 'Outros'),
    ]
    
    caixa = models.ForeignKey(
        CaixaDiario,
        on_delete=models.PROTECT,
        related_name='movimentos'
    )
    tipo = models.CharField('tipo', max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField('categoria', max_length=25, choices=CATEGORIA_CHOICES)
    valor = models.DecimalField(
        'valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    descricao = models.CharField('descricao', max_length=255)
    
    # Vinculo com parcela (se for pagamento de parcela)
    parcela = models.ForeignKey(
        Parcela,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimentos'
    )
    
    class Meta:
        verbose_name = 'movimento de caixa'
        verbose_name_plural = 'movimentos de caixa'
        ordering = ['-caixa__data', '-criado_em']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - R$ {self.valor} - {self.descricao}'
    
    def save(self, *args, **kwargs):
        # Impede alteracao em caixa fechado
        if self.caixa.fechado and not self._state.adding:
            raise ValueError('Nao e possivel alterar movimento em caixa fechado.')
        super().save(*args, **kwargs)


class LogFinanceiro(models.Model):
    """
    Log de auditoria para alteracoes financeiras.
    """
    MODELO_CHOICES = [
        ('contrato', 'Contrato'),
        ('parcela', 'Parcela'),
        ('caixa', 'Caixa Diario'),
        ('movimento', 'Movimento de Caixa'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='logs_financeiros'
    )
    modelo = models.CharField('modelo', max_length=20, choices=MODELO_CHOICES)
    objeto_id = models.PositiveIntegerField('ID do objeto')
    campo = models.CharField('campo alterado', max_length=100)
    valor_anterior = models.TextField('valor anterior', blank=True)
    valor_novo = models.TextField('valor novo', blank=True)
    data_alteracao = models.DateTimeField('data da alteracao', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    
    class Meta:
        verbose_name = 'log financeiro'
        verbose_name_plural = 'logs financeiros'
        ordering = ['-data_alteracao']
    
    def __str__(self):
        return f'{self.modelo} #{self.objeto_id} - {self.campo} - {self.data_alteracao}'
