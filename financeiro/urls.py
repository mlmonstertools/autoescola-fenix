from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.FinanceiroDashboardView.as_view(), name='index'),
    path('contratos/', views.ContratoListView.as_view(), name='contratos'),
    path('contratos/novo/', views.ContratoCreateView.as_view(), name='contrato_criar'),
    path('contratos/<int:pk>/', views.ContratoDetailView.as_view(), name='contrato_detalhe'),
    path('parcelas/<int:pk>/pagar/', views.ParcelaRegistrarPagamentoView.as_view(), name='parcela_pagar'),
    path('caixa/', views.CaixaDiarioView.as_view(), name='caixa'),
    path('caixa/movimento/', views.CaixaMovimentoCreateView.as_view(), name='movimento_criar'),
]
