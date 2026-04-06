"""
Tasks assincronas do modulo aulas.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def enviar_lembretes_aulas():
    """
    Envia lembretes de aulas agendadas para o dia seguinte.
    """
    from aulas.models import Aula
    from notificacoes.models import Notificacao
    
    amanha = timezone.now().date() + timedelta(days=1)
    
    # Buscar aulas agendadas para amanha
    aulas = Aula.objects.filter(
        status='agendada',
        data=amanha
    ).select_related('matricula__aluno__usuario', 'instrutor__usuario')
    
    count = 0
    for aula in aulas:
        # Notificar aluno
        if aula.matricula.aluno.usuario:
            Notificacao.objects.create(
                usuario=aula.matricula.aluno.usuario,
                tipo='aula',
                titulo='Lembrete de Aula',
                mensagem=f'Voce tem aula {aula.get_tipo_display()} amanha as {aula.hora.strftime("%H:%M")} com {aula.instrutor.usuario.get_full_name() or aula.instrutor.usuario.email}.',
                link=f'/agenda/aulas/{aula.id}/'
            )
            count += 1
        
        # Notificar instrutor
        if aula.instrutor.usuario:
            Notificacao.objects.create(
                usuario=aula.instrutor.usuario,
                tipo='aula',
                titulo='Lembrete de Aula',
                mensagem=f'Voce tem aula {aula.get_tipo_display()} amanha as {aula.hora.strftime("%H:%M")} com {aula.matricula.aluno.nome}.',
                link=f'/agenda/aulas/{aula.id}/'
            )
            count += 1
    
    return f'{count} lembretes de aula enviados'


@shared_task
def verificar_aulas_nao_registradas():
    """
    Verifica aulas agendadas que passaram e nao foram registradas.
    Envia alerta para recepcionistas.
    """
    from aulas.models import Aula
    from notificacoes.models import Notificacao
    from core.models import User
    
    ontem = timezone.now().date() - timedelta(days=1)
    
    aulas_pendentes = Aula.objects.filter(
        status='agendada',
        data__lte=ontem
    )
    
    if not aulas_pendentes.exists():
        return '0 aulas pendentes de registro'
    
    destinatarios = User.objects.filter(
        is_active=True,
        groups__name__in=['DIRETOR', 'RECEPCIONISTA']
    ).distinct()
    
    count = 0
    for usuario in destinatarios:
        Notificacao.objects.create(
            usuario=usuario,
            tipo='alerta',
            titulo='Aulas Pendentes de Registro',
            mensagem=f'Existem {aulas_pendentes.count()} aulas que precisam ter presenca registrada.',
            link='/agenda/'
        )
        count += 1
    
    return f'{count} alertas de aulas pendentes enviados'
