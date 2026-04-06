"""
Comando para configurar dados iniciais do sistema.
Uso: python manage.py setup_initial_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import Usuario
from instrutores.models import Instrutor
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Configura dados iniciais do sistema (grupos e usuário admin)'

    def handle(self, *args, **options):
        self.stdout.write('Configurando dados iniciais...')
        
        # Criar grupos
        grupos = ['DIRETOR', 'INSTRUTOR', 'RECEPCIONISTA']
        for nome in grupos:
            group, created = Group.objects.get_or_create(name=nome)
            if created:
                self.stdout.write(f'  Grupo {nome} criado')
            else:
                self.stdout.write(f'  Grupo {nome} já existe')
        
        # Criar usuário admin se não existir
        admin_email = 'admin@autoescolafenix.com.br'
        if not Usuario.objects.filter(email=admin_email).exists():
            admin = Usuario.objects.create_superuser(
                email=admin_email,
                password='admin123',
                nome_completo='Administrador'
            )
            self.stdout.write(self.style.SUCCESS(f'  Admin criado: {admin_email} / admin123'))
        else:
            self.stdout.write(f'  Admin {admin_email} já existe')
        
        # Criar usuário diretor
        diretor_email = 'diretor@autoescolafenix.com.br'
        if not Usuario.objects.filter(email=diretor_email).exists():
            diretor = Usuario.objects.create_user(
                email=diretor_email,
                password='diretor123',
                nome_completo='João Diretor',
                telefone='11999990001'
            )
            diretor.groups.add(Group.objects.get(name='DIRETOR'))
            self.stdout.write(self.style.SUCCESS(f'  Diretor criado: {diretor_email} / diretor123'))
        else:
            self.stdout.write(f'  Diretor {diretor_email} já existe')
        
        # Criar usuário instrutor
        instrutor_email = 'instrutor@autoescolafenix.com.br'
        if not Usuario.objects.filter(email=instrutor_email).exists():
            usuario_instrutor = Usuario.objects.create_user(
                email=instrutor_email,
                password='instrutor123',
                nome_completo='Carlos Instrutor',
                telefone='11999990002'
            )
            usuario_instrutor.groups.add(Group.objects.get(name='INSTRUTOR'))
            
            # Criar registro de Instrutor
            Instrutor.objects.get_or_create(
                usuario=usuario_instrutor,
                defaults={
                    'numero_credencial': 'CRED001',
                    'data_emissao_credencial': date.today() - timedelta(days=365),
                    'data_vencimento_credencial': date.today() + timedelta(days=365),
                    'numero_cnh': '12345678900',
                    'categoria_cnh': 'AB',
                    'validade_cnh': date.today() + timedelta(days=365*3),
                    'cor_agenda': '#3B82F6',
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  Instrutor criado: {instrutor_email} / instrutor123'))
        else:
            self.stdout.write(f'  Instrutor {instrutor_email} já existe')
        
        # Criar usuário recepcionista
        recep_email = 'recepcao@autoescolafenix.com.br'
        if not Usuario.objects.filter(email=recep_email).exists():
            recepcionista = Usuario.objects.create_user(
                email=recep_email,
                password='recepcao123',
                nome_completo='Maria Recepcionista',
                telefone='11999990003'
            )
            recepcionista.groups.add(Group.objects.get(name='RECEPCIONISTA'))
            self.stdout.write(self.style.SUCCESS(f'  Recepcionista criada: {recep_email} / recepcao123'))
        else:
            self.stdout.write(f'  Recepcionista {recep_email} já existe')
        
        self.stdout.write(self.style.SUCCESS('Dados iniciais configurados com sucesso!'))
        self.stdout.write('')
        self.stdout.write('Usuários disponíveis:')
        self.stdout.write('  ADMIN: admin@autoescolafenix.com.br / admin123')
        self.stdout.write('  DIRETOR: diretor@autoescolafenix.com.br / diretor123')
        self.stdout.write('  INSTRUTOR: instrutor@autoescolafenix.com.br / instrutor123')
        self.stdout.write('  RECEPCIONISTA: recepcao@autoescolafenix.com.br / recepcao123')
