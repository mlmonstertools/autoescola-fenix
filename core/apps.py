from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        # Importa o admin customizado para aplicar as restrições de acesso
        from core import admin  # noqa
