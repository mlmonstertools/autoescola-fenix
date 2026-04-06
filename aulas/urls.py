from django.urls import path
from . import views

app_name = 'aulas'

urlpatterns = [
    path('', views.AulaListView.as_view(), name='lista'),
    path('agenda/', views.AulaAgendaView.as_view(), name='agenda'),
    path('nova/', views.AulaCreateView.as_view(), name='criar'),
    path('<int:pk>/editar/', views.AulaUpdateView.as_view(), name='editar'),
    path('<int:pk>/registrar/', views.AulaRegistrarView.as_view(), name='registrar'),
    path('minhas/', views.MinhasAulasView.as_view(), name='minhas'),
]
