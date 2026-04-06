from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from core.models import BaseModelComManager
from core.utils import dias_ate


class Instrutor(BaseModelComManager):
    """
    Cadastro de instrutores da autoescola.
    """
    ESPECIALIDADE_CHOICES = [
        ('A', 'Categoria A (Motos)'),
        ('B', 'Categoria B (Carros)'),
        ('AB', 'Categorias A e B'),
        ('C', 'Categoria C'),
        ('D', 'Categoria D'),
        ('E', 'Categoria E'),
    ]
    
    CORES_AGENDA = [
        ('#f97316', 'Laranja'),
        ('#3b82f6', 'Azul'),
        ('#10b981', 'Verde'),
        ('#8b5cf6', 'Roxo'),
        ('#ef4444', 'Vermelho'),
        ('#f59e0b', 'Amarelo'),
        ('#ec4899', 'Rosa'),
        ('#06b6d4', 'Ciano'),
    ]
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instrutor'
    )
    
    # Credencial DETRAN
    numero_credencial = models.CharField('numero da credencial', max_length=50, unique=True)
    data_emissao_credencial = models.DateField('data de emissao')
    data_vencimento_credencial = models.DateField('data de vencimento')
    
    # Especialidades
    especialidades = models.CharField('especialidades', max_length=5, choices=ESPECIALIDADE_CHOICES)
    
    # Visual na agenda
    cor_agenda = models.CharField('cor na agenda', max_length=7, choices=CORES_AGENDA, default='#f97316')
    
    # CNH do instrutor
    numero_cnh = models.CharField('numero da CNH', max_length=20)
    categoria_cnh = models.CharField('categoria da CNH', max_length=5)
    validade_cnh = models.DateField('validade da CNH')
    
    class Meta:
        verbose_name = 'instrutor'
        verbose_name_plural = 'instrutores'
        ordering = ['usuario__nome_completo']
    
    def __str__(self):
        return self.usuario.nome_completo
    
    @property
    def nome(self):
        return self.usuario.nome_completo
    
    @property
    def email(self):
        return self.usuario.email
    
    @property
    def telefone(self):
        return self.usuario.telefone
    
    @property
    def dias_para_vencer_credencial(self):
        return dias_ate(self.data_vencimento_credencial)
    
    @property
    def credencial_vencida(self):
        return self.data_vencimento_credencial < timezone.now().date()
    
    @property
    def alerta_credencial(self):
        """
        Retorna nivel de alerta baseado nos dias para vencer.
        90, 60, 30 dias de antecedencia.
        """
        dias = self.dias_para_vencer_credencial
        if dias <= 0:
            return 'vencido'
        elif dias <= 30:
            return 'urgente'
        elif dias <= 60:
            return 'atencao'
        elif dias <= 90:
            return 'alerta'
        return None
    
    def pode_lecionar_categoria(self, categoria):
        """Verifica se instrutor pode lecionar para determinada categoria."""
        if self.especialidades == 'AB':
            return categoria in ['A', 'B']
        return categoria in self.especialidades


class Veiculo(BaseModelComManager):
    """
    Veiculos da autoescola para aulas praticas.
    """
    TIPO_CHOICES = [
        ('carro', 'Carro'),
        ('moto', 'Moto'),
        ('caminhao', 'Caminhao'),
        ('onibus', 'Onibus'),
    ]
    
    CATEGORIA_CHOICES = [
        ('A', 'Categoria A'),
        ('B', 'Categoria B'),
        ('C', 'Categoria C'),
        ('D', 'Categoria D'),
        ('E', 'Categoria E'),
    ]
    
    placa = models.CharField('placa', max_length=10, unique=True)
    modelo = models.CharField('modelo', max_length=100)
    marca = models.CharField('marca', max_length=100)
    ano = models.PositiveIntegerField('ano')
    tipo = models.CharField('tipo', max_length=20, choices=TIPO_CHOICES)
    categoria = models.CharField('categoria', max_length=2, choices=CATEGORIA_CHOICES)
    cor = models.CharField('cor', max_length=50)
    renavam = models.CharField('RENAVAM', max_length=20, unique=True)
    chassi = models.CharField('chassi', max_length=50, unique=True)
    
    # Documentacao
    data_licenciamento = models.DateField('data do licenciamento')
    
    # Controle
    km_atual = models.PositiveIntegerField('KM atual', default=0)
    em_manutencao = models.BooleanField('em manutencao', default=False)
    
    class Meta:
        verbose_name = 'veiculo'
        verbose_name_plural = 'veiculos'
        ordering = ['placa']
    
    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'
    
    @property
    def disponivel(self):
        return self.ativo and not self.em_manutencao
