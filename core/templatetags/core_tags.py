from django import template
from django.utils.safestring import mark_safe
from core.utils import formatar_moeda, formatar_cpf, formatar_telefone, status_dias_restantes

register = template.Library()


@register.filter
def moeda(valor):
    """Formata valor como moeda brasileira."""
    return formatar_moeda(valor)


@register.filter
def cpf(valor):
    """Formata CPF."""
    return formatar_cpf(valor)


@register.filter
def telefone(valor):
    """Formata telefone."""
    return formatar_telefone(valor)


@register.filter
def status_badge(status):
    """Retorna classe de badge baseada no status."""
    status_classes = {
        'aprovado': 'bg-green-500',
        'pago': 'bg-green-500',
        'ativo': 'bg-green-500',
        'concluido': 'bg-green-500',
        'pendente': 'bg-yellow-500',
        'agendado': 'bg-yellow-500',
        'em_andamento': 'bg-orange-500',
        'reprovado': 'bg-red-500',
        'vencido': 'bg-red-500',
        'cancelado': 'bg-red-500',
        'inativo': 'bg-gray-500',
    }
    return status_classes.get(status.lower(), 'bg-gray-500')


@register.filter
def dias_status_class(dias):
    """Retorna classe CSS baseada nos dias restantes."""
    status = status_dias_restantes(dias)
    classes = {
        'vencido': 'text-red-600 bg-red-100',
        'urgente': 'text-red-600 bg-red-100',
        'atencao': 'text-yellow-600 bg-yellow-100',
        'alerta': 'text-orange-600 bg-orange-100',
        'ok': 'text-green-600 bg-green-100',
    }
    return classes.get(status, '')


@register.simple_tag
def progress_bar(atual, total, cor='orange'):
    """Renderiza barra de progresso."""
    if total == 0:
        percentual = 0
    else:
        percentual = min(100, int((atual / total) * 100))
    
    html = f'''
    <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div class="bg-{cor}-500 h-2.5 rounded-full transition-all duration-300" style="width: {percentual}%"></div>
    </div>
    <span class="text-xs text-gray-600">{atual}/{total} ({percentual}%)</span>
    '''
    return mark_safe(html)


@register.inclusion_tag('core/partials/breadcrumbs.html')
def breadcrumbs(items):
    """Renderiza breadcrumbs."""
    return {'items': items}


@register.inclusion_tag('core/partials/status_badge.html')
def render_status(status, texto=None):
    """Renderiza badge de status."""
    return {'status': status, 'texto': texto or status}


@register.simple_tag(takes_context=True)
def is_instrutor(context):
    """Verifica se usuario logado e instrutor."""
    request = context.get('request')
    if request and request.user.is_authenticated:
        return request.user.groups.filter(name='INSTRUTOR').exists()
    return False
