from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.
class TarefaModel(models.Model):
    DIAS_SEMANA = (
        ('segunda','Segunda-feira'),
        ('terca','Terça-feira'),
        ('quarta','Quarta-feira'),
        ('quinta','Quinta-feira'),
        ('sexta','Sexta-feira'),
        ('sabado','Sábado'),
        ('domingo','Domingo'),
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    completo = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    # MultiSelectField permite o usuário escolher vários dias ao mesmo tempo.
    # choices define as opções visíveis (segunda, terça, etc.).
    # O valor é salvo como uma string separada (tipo 'segunda,quarta').
    dias_semana = MultiSelectField(choices=DIAS_SEMANA, max_length=100, default=[])

    def __str__ (self):
        return self.nome
    
class ConclusoesModel(models.Model):
    tarefa = models.ForeignKey(TarefaModel,on_delete=models.CASCADE, related_name='conclusoes')
    dia = models.CharField(max_length=10,choices=TarefaModel.DIAS_SEMANA)
    concluido = models.BooleanField(default=False)
    concluida_em = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f'{self.tarefa.nome} - {self.dia} - {"Concluido" if self.concluido else "Pendente"}'
    

class ResetSemana(models.Model):
    data_reset = models.DateField()