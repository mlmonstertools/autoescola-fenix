from django.db import models
from django.conf import settings

from core.models import BaseModelComManager
from core.utils import build_whatsapp_url, get_whatsapp_url_or_mock


class TemplateMensagem(BaseModelComManager):
    """
    Templates de mensagens para notificacoes.
    """
    TIPO_CHOICES = [
        ('cobranca', 'Cobranca de Parcela'),
        ('lembrete_aula', 'Lembrete de Aula'),
        ('lembrete_exame', 'Lembrete de Exame'),
        ('parabens_aprovacao', 'Parabens por Aprovacao'),
        ('aniversario', 'Aniversario'),
        ('boas_vindas', 'Boas Vindas'),
        ('outro', 'Outro'),
    ]
    
    tipo = models.CharField('tipo', max_length=25, choices=TIPO_CHOICES, unique=True)
    titulo = models.CharField('titulo', max_length=100)
    conteudo = models.TextField(
        'conteudo',
        help_text='Variaveis disponiveis: {nome}, {valor}, {data}, {hora}, {instrutor}, {tipo}, {local}'
    )
    
    class Meta:
        verbose_name = 'template de mensagem'
        verbose_name_plural = 'templates de mensagens'
        ordering = ['tipo']
    
    def __str__(self):
        return self.titulo
    
    def renderizar(self, **kwargs):
        """Renderiza o template com as variaveis fornecidas."""
        return self.conteudo.format(**kwargs)


class LogNotificacao(BaseModelComManager):
    """
    Log de notificacoes enviadas.
    """
    STATUS_CHOICES = [
        ('enviado', 'Enviado'),
        ('simulado', 'Simulado'),
        ('erro', 'Erro'),
    ]
    
    aluno = models.ForeignKey(
        'alunos.Aluno',
        on_delete=models.CASCADE,
        related_name='notificacoes'
    )
    template = models.ForeignKey(
        TemplateMensagem,
        on_delete=models.PROTECT,
        related_name='logs'
    )
    mensagem_enviada = models.TextField('mensagem enviada')
    telefone_destino = models.CharField('telefone destino', max_length=20)
    url_whatsapp = models.URLField('URL WhatsApp', max_length=500)
    status = models.CharField('status', max_length=15, choices=STATUS_CHOICES)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='notificacoes_enviadas'
    )
    
    class Meta:
        verbose_name = 'log de notificacao'
        verbose_name_plural = 'logs de notificacoes'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f'{self.aluno.nome_completo} - {self.template.titulo} - {self.status}'


def enviar_notificacao(aluno, template_tipo, usuario, **variaveis):
    """
    Funcao auxiliar para enviar notificacao.
    Gera URL do WhatsApp e registra no log.
    """
    try:
        template = TemplateMensagem.objects.get(tipo=template_tipo)
    except TemplateMensagem.DoesNotExist:
        return None
    
    # Adiciona nome do aluno as variaveis
    variaveis['nome'] = aluno.nome_completo
    
    mensagem = template.renderizar(**variaveis)
    url, is_mock = get_whatsapp_url_or_mock(aluno.telefone, mensagem)
    
    log = LogNotificacao.objects.create(
        aluno=aluno,
        template=template,
        mensagem_enviada=mensagem,
        telefone_destino=aluno.telefone or settings.WHATSAPP_MOCK_NUMBER,
        url_whatsapp=url,
        status='simulado' if is_mock else 'enviado',
        enviado_por=usuario,
        criado_por=usuario
    )
    
    return log
