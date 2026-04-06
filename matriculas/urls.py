from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    path('', views.MatriculaListView.as_view(), name='lista'),
    path('nova/', views.MatriculaCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.MatriculaDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.MatriculaUpdateView.as_view(), name='editar'),
]
