from django.urls import path
from . import views

app_name = 'notificacoes'

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='lista'),
    path('templates/', views.TemplateListView.as_view(), name='templates'),
    path('templates/novo/', views.TemplateCreateView.as_view(), name='template_criar'),
    path('logs/', views.LogListView.as_view(), name='logs'),
    path('enviar/<int:aluno_pk>/<str:template_codigo>/', views.EnviarNotificacaoView.as_view(), name='enviar'),
    path('aula/<int:aula_pk>/lembrete/', views.EnviarLembreteAulaView.as_view(), name='lembrete_aula'),
]
