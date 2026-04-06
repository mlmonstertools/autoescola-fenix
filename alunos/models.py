from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from core.models import BaseModelComManager
from core.utils import validar_cpf


class Aluno(BaseModelComManager):
    """
    Cadastro de alunos da autoescola.
    """
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viuvo(a)'),
        ('outro', 'Outro'),
    ]
    
    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapa'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceara'), ('DF', 'Distrito Federal'),
        ('ES', 'Espirito Santo'), ('GO', 'Goias'), ('MA', 'Maranhao'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Para'), ('PB', 'Paraiba'), ('PR', 'Parana'), ('PE', 'Pernambuco'),
        ('PI', 'Piaui'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondonia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'Sao Paulo'), ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]
    
    # Dados pessoais
    nome_completo = models.CharField('nome completo', max_length=255)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    rg = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('data de nascimento')
    genero = models.CharField('genero', max_length=1, choices=GENERO_CHOICES)
    estado_civil = models.CharField('estado civil', max_length=15, choices=ESTADO_CIVIL_CHOICES, blank=True)
    naturalidade = models.CharField('naturalidade', max_length=100, blank=True)
    nacionalidade = models.CharField('nacionalidade', max_length=100, default='Brasileira')
    nome_mae = models.CharField('nome da mae', max_length=255)
    nome_pai = models.CharField('nome do pai', max_length=255, blank=True)
    
    # Foto
    foto = models.ImageField('foto', upload_to='alunos/fotos/', blank=True, null=True)
    
    # Contato
    email = models.EmailField('email', blank=True)
    telefone = models.CharField('telefone', max_length=20)
    telefone_alternativo = models.CharField('telefone alternativo', max_length=20, blank=True)
    
    # Endereco
    cep = models.CharField('CEP', max_length=10)
    logradouro = models.CharField('logradouro', max_length=255)
    numero = models.CharField('numero', max_length=20)
    complemento = models.CharField('complemento', max_length=100, blank=True)
    bairro = models.CharField('bairro', max_length=100)
    cidade = models.CharField('cidade', max_length=100)
    uf = models.CharField('UF', max_length=2, choices=UF_CHOICES)
    
    # LGPD
    consentimento_lgpd = models.BooleanField('consentimento LGPD', default=False)
    data_consentimento = models.DateTimeField('data do consentimento', null=True, blank=True)
    
    # Observacoes
    observacoes = models.TextField('observacoes', blank=True)
    
    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'
        ordering = ['nome_completo']
    
    def __str__(self):
        return self.nome_completo
    
    def clean(self):
        super().clean()
        if self.cpf and not validar_cpf(self.cpf):
            raise ValidationError({'cpf': 'CPF invalido.'})
    
    def save(self, *args, **kwargs):
        # Redimensiona foto para 300x400px se existir
        if self.foto:
            img = Image.open(self.foto)
            if img.height != 400 or img.width != 300:
                output_size = (300, 400)
                img = img.resize(output_size, Image.Resampling.LANCZOS)
                output = BytesIO()
                img_format = self.foto.name.split('.')[-1].upper()
                if img_format == 'JPG':
                    img_format = 'JPEG'
                img.save(output, format=img_format, quality=90)
                output.seek(0)
                self.foto = InMemoryUploadedFile(
                    output, 'ImageField', self.foto.name,
                    f'image/{img_format.lower()}',
                    sys.getsizeof(output), None
                )
        super().save(*args, **kwargs)


class DocumentoAluno(BaseModelComManager):
    """
    Documentos digitalizados do aluno.
    """
    TIPO_CHOICES = [
        ('rg', 'RG'),
        ('cpf', 'CPF'),
        ('comprovante_residencia', 'Comprovante de Residencia'),
        ('certidao_nascimento', 'Certidao de Nascimento'),
        ('certidao_casamento', 'Certidao de Casamento'),
        ('cnh', 'CNH Anterior'),
        ('foto_3x4', 'Foto 3x4'),
        ('outro', 'Outro'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField('tipo', max_length=30, choices=TIPO_CHOICES)
    arquivo = models.FileField('arquivo', upload_to='alunos/documentos/')
    descricao = models.CharField('descricao', max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        ordering = ['tipo']
    
    def __str__(self):
        return f'{self.aluno.nome_completo} - {self.get_tipo_display()}'
