from django.urls import path
from . import views

app_name = 'instrutores'

urlpatterns = [
    path('', views.InstrutorListView.as_view(), name='lista'),
    path('novo/', views.InstrutorCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.InstrutorDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.InstrutorUpdateView.as_view(), name='editar'),
    path('veiculos/', views.VeiculoListView.as_view(), name='veiculos_lista'),
    path('veiculos/novo/', views.VeiculoCreateView.as_view(), name='veiculo_criar'),
    path('veiculos/<int:pk>/editar/', views.VeiculoUpdateView.as_view(), name='veiculo_editar'),
]
