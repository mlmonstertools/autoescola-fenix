# PROMPT PARA CLAUDE OPUS 4.5 — SISTEMA DE GESTÃO PARA AUTOESCOLA/CFC (DJANGO)

---

## QUEM VOCÊ É

Você é um engenheiro Django sênior. Seu trabalho é construir um sistema web completo de gestão
para Autoescolas e CFCs (Centros de Formação de Condutores), substituindo um sistema legado
chamado Abel Genial — software dos anos 90, interface que trava com o mouse, visual de BIOS de
PC, operado apenas por teclado.

O objetivo é um protótipo funcional e visualmente moderno para a Autoescola Fênix avaliar
a substituição. Você tem autonomia total para decidir arquitetura, organização de arquivos,
ordem de implementação e modelagem — use esse espaço para entregar o melhor Django possível.

---

## REGRA FUNDAMENTAL: USE O DJANGO, NÃO LUTE CONTRA ELE

Antes de escrever qualquer linha de código:

- Analise rigorosamente a documentação do Django: "https://docs.djangoproject.com/en/6.0/" para utilizar suas funcionalidades mais atuais, utilize o mcp do context7 para analisar as documentações mais atualizadas caso necessário.
- Inicie com `django-admin startproject autoescola .`
- Crie cada app com `python manage.py startapp <nome>` — NUNCA crie pastas de app manualmente
- Registre cada app em `INSTALLED_APPS` imediatamente após criar
- Use `makemigrations` e `migrate` para todo model novo
- Extraia o máximo do que o Django já entrega antes de instalar qualquer lib:
  - `django.contrib.auth` para autenticação, grupos e permissões
  - `django.contrib.admin` customizado — é o painel interno de dados do sistema
  - `django.contrib.messages` para feedback ao usuário
  - CBVs nativas com mixins de permissão
  - `ModelForm` com `clean()` para validações — não valide só na view
  - Signals para efeitos colaterais automáticos
  - `django.contrib.humanize` para formatação nos templates
- NUNCA reinvente o que o Django já entrega

---

## STACK

- Python 3.14.3 + Django 6.0
- Banco: SQLite no desenvolvimento, PostgreSQL em produção
- Frontend: Django Templates + HTMX + Alpine.js + Tailwind CSS (todos via CDN, sem build step)
- Agenda visual: FullCalendar.js (CDN)
- PDFs: WeasyPrint
- Tarefas assíncronas: Celery + Redis
- Permissões por objeto: django-guardian
- Testes: pytest-django + factory-boy
- Deploy alvo: VPS Linux com Gunicorn + Nginx

---

## APPS DO SISTEMA

Crie com `startapp`. A organização interna e a modelagem são decisões suas:

- `core` — BaseModel abstrato, mixins, utils, template tags
- `accounts` — usuário customizado (AbstractUser), perfis, login, permissões por grupo
- `alunos` — cadastro de alunos, documentos, foto
- `matriculas` — processo CNH, status, histórico
- `instrutores` — cadastro, credenciais DETRAN, alertas de vencimento
- `aulas` — agenda de aulas práticas, veículos, registro de frequência
- `exames` — psicotécnico, médico, exames DETRAN (teórico e prático)
- `financeiro` — contratos, parcelas, caixa diário, auditoria
- `relatorios` — PDFs para DETRAN/CIRETRAN, relatórios gerenciais
- `notificacoes` — templates de mensagem, log de envios, links WhatsApp
- `dashboard` — KPIs, gráficos Chart.js, alertas centralizados

---

## O QUE O SISTEMA PRECISA FAZER

Descrevo os domínios e fluxos. A modelagem é sua.

### Alunos e documentos
Cadastro completo de alunos com foto (redimensionar para 300x400px com Pillow no save),
documentos digitalizados, dados pessoais, endereço e contato. CPF deve ser validado pelo
algoritmo mod11 antes de salvar — criar utilitário em `core/utils.py`. Incluir flag de
consentimento LGPD com data de aceite. Soft delete obrigatório: nunca `.delete()`, sempre
`ativo = False`.

### Processo CNH (Matrículas)
Cada aluno pode ter uma ou mais matrículas. Uma matrícula representa o processo completo para
obter ou adicionar uma categoria de CNH (A, B, AB, C, D, E, ACC). O sistema precisa controlar:
modalidade (CFCA para motos, CFCB para carros), tipo do processo (primeira habilitação, adição
de categoria, renovação), status atual e histórico de cada mudança de status com justificativa.
O progresso é medido por aulas teóricas (mínimo 45) e práticas (mínimo 20) realizadas. Um
número de processo único deve ser gerado automaticamente no formato AAAA-NNNNNN.

### Instrutores e credenciais
Instrutores têm credencial emitida pelo DETRAN com data de vencimento. O sistema deve alertar
com 90, 60 e 30 dias de antecedência. Cada instrutor tem uma cor para identificação visual na
agenda. Apenas instrutores com a especialidade correspondente podem ser alocados para uma
categoria de matrícula.

### Agenda de aulas
As aulas podem ser teóricas ou práticas (simulador, via pública, direção defensiva, primeiros
socorros). Aulas práticas usam veículo. O sistema deve impedir: mesmo instrutor em dois
horários sobrepostos, mesmo veículo em duas aulas simultâneas. Duração de aula prática:
mínimo 50 minutos, máximo 90 minutos. Ao registrar a aula como realizada, o instrutor informa
status, km rodado (se prática), avaliação de 1 a 10 e observações.

### Exames
Três tipos: psicotécnico, médico e exames no DETRAN (teórico e prático). Pré-requisitos
obrigatórios validados no sistema: o exame teórico DETRAN só pode ser agendado após 45 aulas
teóricas realizadas; o exame prático só pode ser agendado após aprovação no teórico e 20 aulas
práticas realizadas. Após 3 reprovações no teórico ou 2 no prático, bloquear o agendamento e
exigir revisão manual com flag no sistema.

### Financeiro
Cada matrícula gera um contrato. O contrato define valor total, desconto, valor de entrada,
número de parcelas (1-24) e dia de vencimento. As parcelas são geradas automaticamente quando
o contrato é salvo. Multa por atraso: 2% do valor. Juros: 1% ao mês proporcional aos dias.
NUNCA usar `float` para dinheiro — sempre `Decimal`. O caixa diário registra entradas e saídas;
após o fechamento do dia, nenhum movimento pode ser alterado. Toda alteração em valores
financeiros deve ser logada com usuário responsável, timestamp, valor anterior e novo.
FKs em modelos financeiros: usar `PROTECT` — nunca cascade.

### Relatórios e PDFs
Documentos para DETRAN/CIRETRAN via WeasyPrint: ficha de matrícula com foto, boletim de
frequência teórica, boletim de frequência prática, declaração de conclusão, declaração de
matrícula. Relatórios gerenciais com Chart.js: alunos por status, taxa de aprovação em exames,
receita vs inadimplência por mês, produtividade de instrutores.

### Notificações via WhatsApp
NÃO usar Evolution API, Z-API ou qualquer API externa. Implementar em `core/utils.py`:

```python
from urllib.parse import quote

def build_whatsapp_url(numero: str, mensagem: str) -> str:
    numero_limpo = ''.join(filter(str.isdigit, numero))
    if not numero_limpo.startswith('55'):
        numero_limpo = f'55{numero_limpo}'
    return f'https://wa.me/{numero_limpo}?text={quote(mensagem)}'
```

Todo botão "Enviar WhatsApp" usa `target="_blank"` com link gerado por essa função.
Se o aluno não tiver telefone, usar `settings.WHATSAPP_MOCK_NUMBER` (default: `13981388978`).
Registrar cada acionamento no `LogNotificacao` com status `SIMULADO`.

Mensagens pré-formatadas para: cobrança de parcela vencida, lembrete de aula, lembrete de
exame e parabéns por aprovação — com variáveis `{nome}`, `{valor}`, `{data}`, `{hora}`,
`{instrutor}`, `{tipo}`, `{local}`.

---

## IDENTIDADE VISUAL

O objetivo visual é ser o oposto do Abel Genial: moderno, intuitivo, funciona com mouse e toque.

- **Cor primária:** laranja `#f97316` — CTAs, destaques, elementos ativos, badges de ação
- **Cor secundária:** preto `#191919` — sidebar, navbar, textos principais, headers
- **Fundo:** branco `#ffffff` e cinza claríssimo `#f8fafc` para separar áreas
- **Status badges:** verde para aprovado/pago, amarelo para pendente/agendado,
  vermelho para reprovado/vencido, laranja para em andamento
- Breadcrumbs em todas as páginas internas
- Mensagens de sucesso/erro com auto-dismiss em 5 segundos via Alpine.js
- Modais de confirmação para ações destrutivas
- Ícones: Heroicons via CDN
- Use: #claude-cookbooks-main para te dar mais poder e fazer um design ainda mais bonito, moderno, completo e com cara de dashboard executivo premium.

---

## DESIGN ROLE-FIRST: EXPERIÊNCIA DO INSTRUTOR

O sistema tem dois públicos com necessidades radicalmente diferentes:

**Recepcionista/Admin/Diretor:** usa desktop ou tablet, precisa de acesso completo,
navegação por sidebar lateral, tabelas e formulários completos.

**Instrutor:** usa o celular entre uma aula e outra, no estacionamento ou dentro do
veículo. Precisa de uma experiência completamente diferente.

### Detecção de perfil no template base

```django
{% if request.user.groups.filter(name="INSTRUTOR").exists %}
  {% include "layouts/base_instrutor.html" %}
{% else %}
  {% include "layouts/base_admin.html" %}
{% endif %}
```

### `base_instrutor.html` — mobile-first obrigatório

- Sem sidebar lateral — **bottom navigation bar** fixada no rodapé (padrão mobile nativo)
- Itens da bottom nav: Hoje, Agenda, Alunos, Perfil — nada mais
- Fonte base mínima 16px, botões com altura mínima 48px para toque confortável
- Cards empilhados verticalmente — zero tabelas
- Layout testável em viewport 390px (iPhone 14)

### Dashboard do instrutor

Quando logado como INSTRUTOR, renderizar view completamente diferente do dashboard admin:

**Hoje** (bloco principal, topo da tela):
- Número grande de aulas do dia em destaque
- Lista cronológica: horário + nome do aluno + tipo + status badge
- Botão "Registrar" em cada aula — modal com: status, km (se prática), avaliação 1-10,
  observação — salva em um toque e volta para a lista

**Próximos dias:**
- Mini agenda dos próximos 3 dias (nome + horário)
- Botão "Ver semana" que abre FullCalendar filtrado só para o instrutor logado

**Meus alunos:**
- Cards compactos dos alunos ativos sob responsabilidade do instrutor
- Cada card: nome, barra de progresso (teóricas % e práticas %), próxima aula
- Toque no card: telefone com botão direto para WhatsApp + status da matrícula

**O instrutor NÃO vê:** financeiro, cadastro de alunos, relatórios DETRAN, configurações,
KPIs administrativos (receita, inadimplência), dados de outros instrutores.

### Fluxo principal do instrutor em 3 toques

1. Abre o app → vê aulas de hoje
2. Toca na aula → modal de registro
3. Preenche e salva → volta para a lista

### Segurança no backend — não apenas no template

O perfil INSTRUTOR só acessa seus próprios dados. Filtrar obrigatoriamente no
`get_queryset()` de todas as views com `instrutor=request.user.instrutor` — não
depender de esconder elementos no HTML.

---

## REGRAS TÉCNICAS NÃO-NEGOCIÁVEIS RECOMENDADAS - CASO ENCONTRE REGRAS MELHORES, APLIQUE-AS

- Todo model herda de `BaseModel` abstrato (seus campos: `criado_em`, `atualizado_em`,
  `criado_por`, `ativo`)
- NUNCA `.delete()` — sempre `ativo = False`
- NUNCA `float` para dinheiro — sempre `Decimal`
- NUNCA lógica de negócio na view — `services.py` ou `clean()`
- NUNCA view sem `LoginRequiredMixin` + `PermissionRequiredMixin`
- NUNCA placeholder `# TODO` ou `# implementar depois` — código real ou não escreve
- NUNCA travessão (—) em comentários, docstrings ou texto ao usuário
- HTMX em `hx-post`: sempre `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'`
- Busca ao vivo via HTMX: `hx-trigger="keyup changed delay:300ms"`
- Valores monetários: `list_display` no admin sempre formatados em BRL
- Testes obrigatórios para cálculo de multa/juros e permissões por perfil
- Cobertura mínima de 80% nos apps `financeiro` e `matriculas`

---

**Comece pelo setup do projeto e implemente na ordem que fizer mais sentido
para as dependências. Para cada arquivo, entregue código completo e funcional.**
