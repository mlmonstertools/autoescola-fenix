from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.RelatoriosIndexView.as_view(), name='index'),
    path('alunos/', views.RelatorioAlunosView.as_view(), name='alunos'),
    path('matriculas/', views.RelatorioMatriculasView.as_view(), name='matriculas'),
    path('financeiro/', views.RelatorioFinanceiroView.as_view(), name='financeiro'),
    path('exames/', views.RelatorioExamesView.as_view(), name='exames'),
    path('instrutores/', views.RelatorioInstrutoresView.as_view(), name='instrutores'),
]
