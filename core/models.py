from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    Model abstrato base para todos os models do sistema.
    Garante soft delete, auditoria e timestamps.
    """
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_criados',
        verbose_name='Criado por'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca o registro como inativo ao inves de deletar."""
        self.ativo = False
        self.save(update_fields=['ativo', 'atualizado_em'])

    def restore(self):
        """Restaura um registro marcado como inativo."""
        self.ativo = True
        self.save(update_fields=['ativo', 'atualizado_em'])


class AtivoManager(models.Manager):
    """Manager que retorna apenas registros ativos por padrao."""
    
    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class BaseModelComManager(BaseModel):
    """
    Model abstrato com manager que filtra apenas ativos por padrao.
    Use objects para ativos e all_objects para todos.
    """
    objects = AtivoManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
