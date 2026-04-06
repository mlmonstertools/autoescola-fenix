"""
Tasks assincronas do modulo instrutores.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def verificar_credenciais_vencendo():
    """
    Verifica credenciais de instrutores que estao vencendo nos proximos 30 dias.
    Envia notificacoes para recepcionistas e diretores.
    """
    from instrutores.models import Instrutor
    from notificacoes.models import Notificacao
    from core.models import User
    
    hoje = timezone.now().date()
    data_limite = hoje + timedelta(days=30)
    
    # Buscar instrutores com credencial vencendo
    instrutores = Instrutor.objects.filter(
        ativo=True,
        data_vencimento_credencial__isnull=False,
        data_vencimento_credencial__range=[hoje, data_limite]
    )
    
    # Buscar usuarios que devem receber notificacao (diretores e recepcionistas)
    destinatarios = User.objects.filter(
        is_active=True,
        groups__name__in=['DIRETOR', 'RECEPCIONISTA']
    ).distinct()
    
    count = 0
    for instrutor in instrutores:
        dias_restantes = (instrutor.data_vencimento_credencial - hoje).days
        
        for usuario in destinatarios:
            Notificacao.objects.create(
                usuario=usuario,
                tipo='alerta',
                titulo='Credencial Vencendo',
                mensagem=f'A credencial do instrutor {instrutor.usuario.get_full_name() or instrutor.usuario.email} vence em {dias_restantes} dias ({instrutor.data_vencimento_credencial.strftime("%d/%m/%Y")}).',
                link=f'/instrutores/{instrutor.id}/'
            )
            count += 1
    
    return f'{count} notificacoes de credencial enviadas'


@shared_task
def verificar_cnh_vencendo():
    """
    Verifica CNH de instrutores que estao vencendo nos proximos 30 dias.
    """
    from instrutores.models import Instrutor
    from notificacoes.models import Notificacao
    from core.models import User
    
    hoje = timezone.now().date()
    data_limite = hoje + timedelta(days=30)
    
    instrutores = Instrutor.objects.filter(
        ativo=True,
        validade_cnh__isnull=False,
        validade_cnh__range=[hoje, data_limite]
    )
    
    destinatarios = User.objects.filter(
        is_active=True,
        groups__name__in=['DIRETOR', 'RECEPCIONISTA']
    ).distinct()
    
    count = 0
    for instrutor in instrutores:
        dias_restantes = (instrutor.validade_cnh - hoje).days
        
        for usuario in destinatarios:
            Notificacao.objects.create(
                usuario=usuario,
                tipo='alerta',
                titulo='CNH Vencendo',
                mensagem=f'A CNH do instrutor {instrutor.usuario.get_full_name() or instrutor.usuario.email} vence em {dias_restantes} dias.',
                link=f'/instrutores/{instrutor.id}/'
            )
            count += 1
    
    return f'{count} notificacoes de CNH enviadas'
