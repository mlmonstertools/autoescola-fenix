from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('instrutor/', views.DashboardInstrutorView.as_view(), name='instrutor'),
    path('instrutor/alunos/', views.InstrutorAlunosView.as_view(), name='instrutor_alunos'),
    path('instrutor/agenda/', views.InstrutorAgendaView.as_view(), name='instrutor_agenda'),
    path('instrutor/perfil/', views.InstrutorPerfilView.as_view(), name='instrutor_perfil'),
]
