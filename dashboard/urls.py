from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('instrutor/', views.DashboardInstrutorView.as_view(), name='instrutor'),
]
