import re
from urllib.parse import quote
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import date, datetime
from django.conf import settings


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo mod11.
    Retorna True se valido, False caso contrario.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf) != 11:
        return False
    
    if cpf == cpf[0] * 11:
        return False
    
    # Primeiro digito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Segundo digito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2


def formatar_cpf(cpf: str) -> str:
    """Formata CPF no padrao XXX.XXX.XXX-XX."""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


def limpar_telefone(telefone: str) -> str:
    """Remove caracteres nao numericos do telefone."""
    return ''.join(filter(str.isdigit, telefone))


def formatar_telefone(telefone: str) -> str:
    """Formata telefone no padrao (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    telefone = limpar_telefone(telefone)
    if len(telefone) == 11:
        return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'
    elif len(telefone) == 10:
        return f'({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}'
    return telefone


def build_whatsapp_url(numero: str, mensagem: str) -> str:
    """
    Gera URL do WhatsApp Web/App para enviar mensagem.
    Adiciona codigo do Brasil (55) se nao estiver presente.
    """
    numero_limpo = ''.join(filter(str.isdigit, numero))
    if not numero_limpo.startswith('55'):
        numero_limpo = f'55{numero_limpo}'
    return f'https://wa.me/{numero_limpo}?text={quote(mensagem)}'


def get_whatsapp_url_or_mock(telefone: str, mensagem: str) -> tuple[str, bool]:
    """
    Retorna URL do WhatsApp e flag indicando se e mock.
    Se telefone nao existir, usa numero mock das settings.
    """
    if not telefone or not telefone.strip():
        mock_number = getattr(settings, 'WHATSAPP_MOCK_NUMBER', '13981388978')
        return build_whatsapp_url(mock_number, mensagem), True
    return build_whatsapp_url(telefone, mensagem), False


def formatar_moeda(valor) -> str:
    """Formata valor decimal em reais brasileiros."""
    if valor is None or valor == '':
        return 'R$ 0,00'
    try:
        valor = Decimal(str(valor))
        return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError, InvalidOperation):
        return 'R$ 0,00'


def calcular_multa(valor: Decimal, percentual: Decimal = Decimal('2')) -> Decimal:
    """Calcula multa sobre valor (padrao 2%)."""
    return (valor * percentual / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_juros_pro_rata(valor: Decimal, dias_atraso: int, taxa_mensal: Decimal = Decimal('1')) -> Decimal:
    """
    Calcula juros proporcional aos dias de atraso.
    Taxa mensal padrao: 1%
    """
    if dias_atraso <= 0:
        return Decimal('0')
    taxa_diaria = taxa_mensal / Decimal('30')
    juros = valor * taxa_diaria * Decimal(str(dias_atraso)) / Decimal('100')
    return juros.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_valor_corrigido(valor: Decimal, dias_atraso: int) -> dict:
    """
    Calcula valor corrigido com multa e juros.
    Retorna dicionario com detalhamento.
    """
    multa = calcular_multa(valor)
    juros = calcular_juros_pro_rata(valor, dias_atraso)
    total = valor + multa + juros
    return {
        'valor_original': valor,
        'multa': multa,
        'juros': juros,
        'dias_atraso': dias_atraso,
        'total': total
    }


def gerar_numero_processo(ano: int = None, sequencial: int = None) -> str:
    """
    Gera numero de processo no formato AAAA-NNNNNN.
    Se sequencial nao for fornecido, deve ser obtido do banco.
    """
    if ano is None:
        ano = date.today().year
    if sequencial is None:
        sequencial = 1
    return f'{ano}-{sequencial:06d}'


def dias_ate(data_futura: date) -> int:
    """Retorna numero de dias ate uma data futura."""
    if isinstance(data_futura, datetime):
        data_futura = data_futura.date()
    return (data_futura - date.today()).days


def status_dias_restantes(dias: int) -> str:
    """Retorna classe CSS baseada nos dias restantes."""
    if dias <= 0:
        return 'vencido'
    elif dias <= 30:
        return 'urgente'
    elif dias <= 60:
        return 'atencao'
    elif dias <= 90:
        return 'alerta'
    return 'ok'
