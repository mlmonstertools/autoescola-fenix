from django.urls import path
from . import views

app_name = 'exames'

urlpatterns = [
    path('', views.ExameListView.as_view(), name='lista'),
    path('novo/', views.ExameCreateView.as_view(), name='criar'),
    path('<int:pk>/editar/', views.ExameUpdateView.as_view(), name='editar'),
    path('<int:pk>/resultado/', views.ExameRegistrarResultadoView.as_view(), name='resultado'),
]
