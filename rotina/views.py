from django.shortcuts import render, redirect, get_object_or_404
from .forms import TarefaForm
from .models import TarefaModel, ConclusoesModel
from django.http import HttpRequest
from django.utils.timezone import now
from django.template.defaulttags import register

# Custom template filter para acessar itens em um dicionário por chave
# get_item serve para Acessar a itens em um dicionário
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

# Custom template filter para split
# split dividir uma string e tranforma-la em lista para conseguir iterar 
@register.filter
def split(value, arg):
    return value.split(arg)

def rotina_home(request):
    # Obter o dia da semana atual em inglês
    dia_semana_ingles = now().strftime("%A").lower()

    # Tradução dos dias da semana
    dias_traduzidos = {
        "monday": "segunda",
        "tuesday": "terca",
        "wednesday": "quarta",
        "thursday": "quinta",
        "friday": "sexta",
        "saturday": "sabado",
        "sunday": "domingo",
    }
    
    # Lista de todos os dias da semana em português
    todos_dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    
    # Verificar se há um parâmetro 'dia' na URL
    dia_solicitado = request.GET.get('dia')
    
    # Se houver um dia solicitado na URL e for válido, use-o
    if dia_solicitado and dia_solicitado in todos_dias:
        dia_atual = dia_solicitado
    else:
        # Caso contrário, use o dia atual
        dia_atual = dias_traduzidos.get(dia_semana_ingles, "segunda")
    
    # Dia de hoje para destacar no seletor
    hoje = dias_traduzidos.get(dia_semana_ingles, "segunda")
    
    # Contagem de tarefas por dia da semana
    contagem_tarefas = {}
    for dia in todos_dias:
        # Aqui assumimos que dias_semana é um campo de texto que contém o dia
        # Se for uma lista ou outro formato, precisará adaptar esta condição
        contagem_tarefas[dia] = TarefaModel.objects.filter(dias_semana__contains=dia).count()
    
    # Filtrar tarefas do dia específico
    tarefas_do_dia = TarefaModel.objects.filter(dias_semana__contains=dia_atual)

    # Mapeia conclusões existentes
    conclusoes = ConclusoesModel.objects.filter(dia=dia_atual)
    status_conclusao = { conclusao.tarefa_id: conclusao.concluido for conclusao in conclusoes }

    contexto = {
        "nome": "Gustavo Lenni",
        "rotina": tarefas_do_dia,
        "dia_semana": dia_atual,
        "dia_atual": dia_atual,
        "hoje": hoje,
        "contagem_tarefas": contagem_tarefas,
        "status_conclusao": status_conclusao
    }
    
    return render(request, 'rotina/home.html', contexto)

def rotina_adicionar(request: HttpRequest):
    if request.method == "POST":
        # pegar os dados do formulario
        formulario = TarefaForm(request.POST)
        # se o formulario for valido ele salva ele no nosso banco de dados
        # e retorna para a pagina home
        
        if formulario.is_valid():
            formulario.save()
            return redirect("rotina:home")
    
    contexto = {
        "form": TarefaForm()
    }
    return render(request, 'rotina/adicionar.html', contexto)

def rotina_remover(request: HttpRequest, id):
    tarefa = get_object_or_404(TarefaModel, id=id)
    tarefa.delete()
    return redirect("rotina:home")

def rotina_editar(request: HttpRequest, id):
    tarefa = get_object_or_404(TarefaModel, id=id)
    
    if request.method == 'POST':
        formulario = TarefaForm(request.POST, instance=tarefa)
        if formulario.is_valid():
            formulario.save()
            return redirect("rotina:home")
    
    formulario = TarefaForm(instance=tarefa)
    contexto = {
        "form": formulario
    }
    return render(request, 'rotina/editar.html', contexto)

def rotina_concluir(request: HttpRequest, id, dia):
    tarefa = get_object_or_404(TarefaModel, id=id)

    conclusao, created = ConclusoesModel.objects.get_or_create(
        tarefa=tarefa,
        dia=dia,
        defaults={'concluido': True}
    )
    if not created:
        # Se já existe, apenas inverte o status
        conclusao.concluido = not conclusao.concluido
        conclusao.save()
    
    # Redirecionar para o mesmo dia que o usuário estava vendo
    return redirect(f'/rotina/?dia={dia}')
