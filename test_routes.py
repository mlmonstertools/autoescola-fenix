"""
Script de testes para identificar bugs no sistema
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoescola.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_routes():
    c = Client()
    
    print('=== Testing Login Page ===')
    r = c.get('/accounts/login/')
    print(f'Login GET: {r.status_code}')
    
    print()
    print('=== Testing Login POST ===')
    r = c.post('/accounts/login/', {'username': 'admin@autoescolafenix.com.br', 'password': 'admin123'}, follow=True)
    print(f'Login POST: {r.status_code}')
    if r.status_code == 200:
        print(f'Final URL: {r.request["PATH_INFO"]}')
    
    print()
    print('=== Testing Dashboard ===')
    try:
        r = c.get('/dashboard/')
        print(f'Dashboard: {r.status_code}')
    except Exception as e:
        print(f'Dashboard ERROR: {e}')
    
    print()
    print('=== Testing Alunos ===')
    try:
        r = c.get('/alunos/')
        print(f'Alunos: {r.status_code}')
    except Exception as e:
        print(f'Alunos ERROR: {e}')
    
    print()
    print('=== Testing Matriculas ===')
    try:
        r = c.get('/matriculas/')
        print(f'Matriculas: {r.status_code}')
    except Exception as e:
        print(f'Matriculas ERROR: {e}')
    
    print()
    print('=== Testing Aulas ===')
    try:
        r = c.get('/aulas/')
        print(f'Aulas: {r.status_code}')
    except Exception as e:
        print(f'Aulas ERROR: {e}')
    
    print()
    print('=== Testing Exames ===')
    try:
        r = c.get('/exames/')
        print(f'Exames: {r.status_code}')
    except Exception as e:
        print(f'Exames ERROR: {e}')
    
    print()
    print('=== Testing Financeiro ===')
    try:
        r = c.get('/financeiro/')
        print(f'Financeiro: {r.status_code}')
    except Exception as e:
        print(f'Financeiro ERROR: {e}')
    
    print()
    print('=== Testing Instrutores ===')
    try:
        r = c.get('/instrutores/')
        print(f'Instrutores: {r.status_code}')
    except Exception as e:
        print(f'Instrutores ERROR: {e}')
    
    print()
    print('=== Testing Relatorios ===')
    try:
        r = c.get('/relatorios/')
        print(f'Relatorios: {r.status_code}')
    except Exception as e:
        print(f'Relatorios ERROR: {e}')
    
    print()
    print('=== Testing Notificacoes ===')
    try:
        r = c.get('/notificacoes/')
        print(f'Notificacoes: {r.status_code}')
    except Exception as e:
        print(f'Notificacoes ERROR: {e}')
    
    # Test create pages
    print()
    print('=== Testing Create Pages ===')
    
    try:
        r = c.get('/alunos/novo/')
        print(f'Aluno Criar: {r.status_code}')
    except Exception as e:
        print(f'Aluno Criar ERROR: {e}')
    
    try:
        r = c.get('/matriculas/nova/')
        print(f'Matricula Criar: {r.status_code}')
    except Exception as e:
        print(f'Matricula Criar ERROR: {e}')
    
    try:
        r = c.get('/aulas/nova/')
        print(f'Aula Criar: {r.status_code}')
    except Exception as e:
        print(f'Aula Criar ERROR: {e}')
    
    print()
    print('=== ALL TESTS COMPLETED ===')

if __name__ == '__main__':
    test_routes()
