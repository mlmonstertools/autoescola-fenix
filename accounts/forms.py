from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class LoginForm(AuthenticationForm):
    """Form de login customizado."""
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            'placeholder': 'seu@email.com',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            'placeholder': 'Sua senha',
        })
    )
    
    error_messages = {
        'invalid_login': 'Email ou senha incorretos.',
        'inactive': 'Esta conta esta desativada.',
    }


class UsuarioCreationForm(UserCreationForm):
    """Form de criacao de usuario."""
    
    class Meta:
        model = Usuario
        fields = ['email', 'nome_completo', 'telefone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
            'nome_completo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
        }


class UsuarioUpdateForm(forms.ModelForm):
    """Form de atualizacao de perfil."""
    
    class Meta:
        model = Usuario
        fields = ['nome_completo', 'telefone', 'foto']
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
            'foto': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
            }),
        }
