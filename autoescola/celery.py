"""
Configuracao do Celery para o projeto Autoescola Fenix.

Para rodar o worker:
    celery -A autoescola worker -l info

Para rodar o beat (agendador):
    celery -A autoescola beat -l info

Para Windows (desenvolvimento):
    celery -A autoescola worker -l info --pool=solo
"""
import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoescola.settings')

app = Celery('autoescola')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Tarefas agendadas
app.conf.beat_schedule = {
    # Verificar parcelas vencidas diariamente as 8h
    'verificar-parcelas-vencidas': {
        'task': 'financeiro.tasks.verificar_parcelas_vencidas',
        'schedule': crontab(hour=8, minute=0),
    },
    # Verificar credenciais de instrutores vencendo diariamente as 9h
    'verificar-credenciais-instrutores': {
        'task': 'instrutores.tasks.verificar_credenciais_vencendo',
        'schedule': crontab(hour=9, minute=0),
    },
    # Enviar lembretes de aulas (1 dia antes) diariamente as 18h
    'enviar-lembretes-aulas': {
        'task': 'aulas.tasks.enviar_lembretes_aulas',
        'schedule': crontab(hour=18, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
