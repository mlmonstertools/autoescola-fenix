from django import forms
from .models import Aluno, DocumentoAluno
from core.utils import validar_cpf


class AlunoForm(forms.ModelForm):
    """Form de cadastro de aluno."""
    
    class Meta:
        model = Aluno
        fields = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento', 'genero', 'estado_civil',
            'naturalidade', 'nacionalidade', 'nome_mae', 'nome_pai', 'foto',
            'email', 'telefone', 'telefone_alternativo',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf',
            'consentimento_lgpd', 'observacoes'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'placeholder': 'Nome completo do aluno'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'placeholder': '000.000.000-00',
                'data-mask': 'cpf'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'naturalidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'nacionalidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'placeholder': '(00) 00000-0000',
                'data-mask': 'telefone'
            }),
            'telefone_alternativo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'placeholder': '00000-000',
                'data-mask': 'cep'
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'uf': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'consentimento_lgpd': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-orange-500 border-gray-300 rounded focus:ring-orange-500'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'rows': 3
            }),
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and not validar_cpf(cpf):
            raise forms.ValidationError('CPF invalido.')
        return cpf


class DocumentoAlunoForm(forms.ModelForm):
    """Form para upload de documentos."""
    
    class Meta:
        model = DocumentoAluno
        fields = ['tipo', 'arquivo', 'descricao']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
        }
