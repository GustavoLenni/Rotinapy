from django import forms
from .models import TarefaModel

class TarefaForm(forms.ModelForm):
    class Meta:
        model = TarefaModel
        fields = ['nome','descricao','completo','dias_semana']
        # widgets servem para por classes no nosso form do django
        widgets = {
            'nome': forms.TextInput(attrs={
                'class':'input-nome',
                'placeholder':'Digite o Nome da Tarefa'
            }),
            'descricao': forms.Textarea(attrs={
                'class':'input-descricao',
                'placeholder':'Digite a Descrição'
            }),
            'completo': forms.CheckboxInput(attrs={
                'class':'form-check-input',
            }),
            
        }
