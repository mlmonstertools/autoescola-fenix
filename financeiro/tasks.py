"""
Tasks assincronas do modulo financeiro.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def verificar_parcelas_vencidas():
    """
    Verifica parcelas vencidas e atualiza seu status.
    Envia notificacoes para os responsaveis.
    """
    from financeiro.models import Parcela
    from notificacoes.models import Notificacao
    
    hoje = timezone.now().date()
    
    # Buscar parcelas abertas que venceram
    parcelas_vencidas = Parcela.objects.filter(
        status='aberta',
        data_vencimento__lt=hoje
    )
    
    count = 0
    for parcela in parcelas_vencidas:
        # Atualizar status
        parcela.status = 'vencida'
        parcela.save()
        
        # Criar notificacao para o aluno
        if parcela.contrato.matricula.aluno.usuario:
            Notificacao.objects.create(
                usuario=parcela.contrato.matricula.aluno.usuario,
                tipo='pagamento',
                titulo='Parcela Vencida',
                mensagem=f'A parcela {parcela.numero} do contrato {parcela.contrato.id} venceu em {parcela.data_vencimento.strftime("%d/%m/%Y")}.',
                link=f'/financeiro/parcelas/{parcela.id}/'
            )
        
        count += 1
    
    return f'{count} parcelas marcadas como vencidas'


@shared_task
def enviar_lembrete_pagamento():
    """
    Envia lembretes de parcelas que vencem em 3 dias.
    """
    from financeiro.models import Parcela
    from notificacoes.models import Notificacao
    
    hoje = timezone.now().date()
    data_limite = hoje + timedelta(days=3)
    
    parcelas = Parcela.objects.filter(
        status='aberta',
        data_vencimento__range=[hoje, data_limite]
    )
    
    count = 0
    for parcela in parcelas:
        if parcela.contrato.matricula.aluno.usuario:
            Notificacao.objects.create(
                usuario=parcela.contrato.matricula.aluno.usuario,
                tipo='pagamento',
                titulo='Lembrete de Pagamento',
                mensagem=f'A parcela {parcela.numero} vence em {parcela.data_vencimento.strftime("%d/%m/%Y")}. Valor: R$ {parcela.valor}',
                link=f'/financeiro/parcelas/{parcela.id}/'
            )
        count += 1
    
    return f'{count} lembretes enviados'
