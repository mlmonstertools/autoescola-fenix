from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UsuarioManager(BaseUserManager):
    """Manager customizado para Usuario."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email e obrigatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Usuario customizado do sistema.
    Usa email como identificador principal.
    """
    username = None
    email = models.EmailField(_('email'), unique=True)
    nome_completo = models.CharField(_('nome completo'), max_length=255)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True)
    foto = models.ImageField(
        _('foto'),
        upload_to='usuarios/fotos/',
        blank=True,
        null=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo']
    
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['nome_completo']
    
    def __str__(self):
        return self.nome_completo or self.email
    
    def get_full_name(self):
        return self.nome_completo
    
    def get_short_name(self):
        if self.nome_completo:
            return self.nome_completo.split()[0]
        return self.email.split('@')[0]
    
    @property
    def is_instrutor(self):
        return self.groups.filter(name='INSTRUTOR').exists()
    
    @property
    def is_recepcionista(self):
        return self.groups.filter(name='RECEPCIONISTA').exists()
    
    @property
    def is_diretor(self):
        return self.groups.filter(name='DIRETOR').exists()
    
    @property
    def is_admin_sistema(self):
        return self.is_superuser or self.is_diretor
