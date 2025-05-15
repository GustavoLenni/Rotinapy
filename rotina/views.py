from django.shortcuts import render, redirect, get_object_or_404
from .forms import TarefaForm
from .models import TarefaModel, ConclusoesModel, ResetSemana
from django.http import HttpRequest
from django.utils.timezone import localtime, localdate
from datetime import timedelta
from django.template.defaulttags import register
from django.utils import timezone
from django.db.models import Q
from django.utils.timezone import make_aware, datetime
from django.contrib.auth.decorators import login_required

@login_required
def rotina_home(request):

    # ------Dia da semana------
    # Obter o dia da semana atual em inglês
    dia_semana_ingles = localtime().strftime("%A").lower()

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
    dia_hoje = dias_traduzidos.get(dia_semana_ingles, "segunda")
    


    # ----Status de Conclusão e de contagem de tarefas-----
    # Contagem de tarefas por dia da semana
    # ele guarda a variavel todos_dias que contem todos os dias da semana de segunda a domingo
    # e com isso ele seleciona por exemplo segunda é igual a tantas tarefas
    contagem_tarefas = {}
    for dia in todos_dias:
        contagem_tarefas[dia] = TarefaModel.objects.filter(
            usuario=request.user,
            dias_semana__contains=dia
        ).count()
    
    # Filtrar tarefas do dia específico
    # busca todas as tarefas do dia atual
    tarefas_do_dia = TarefaModel.objects.filter(
        usuario=request.user,
        dias_semana__contains=dia_atual
    )

    # Mapeia conclusões existentes para o dia atual
    # busca as conclusões do dia atual do usuario
    conclusoes = ConclusoesModel.objects.filter(
        dia=dia_atual,
        tarefa__usuario=request.user
    )

    # dicionário onde a chave é o ID da tarefa e o valor diz se ela foi concluída hoje ou não
    status_conclusao = {conclusao.tarefa_id: conclusao.concluido for conclusao in conclusoes}
    
    print(f"Status de conclusão para o dia {dia_atual}: {status_conclusao}")
    
    # Preparar a lista de dias para o template
    dias_semana_lista = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

    # -----Reset------
    data_atual = localdate()
    dia_semana = data_atual.strftime("%A").lower()

    # Se for segunda-feira, reseta todas as confirmações 
    # verifica se o reset ja foi feito 
    if dia_semana == 'monday':
        reset_realizado = ResetSemana.objects.filter(data_reset=data_atual).exists()
        # se não foi reseta as conclusões e registra que o reset foi feito no banco
        # de dados
        if not reset_realizado:
            ConclusoesModel.objects.all().update(concluido=False)
            ResetSemana.objects.create(data_reset=data_atual)


    # -----Total de Tarefas do Dia Atual--------
    # Total de tarefas do dia específico
    total_tarefas = tarefas_do_dia.count()
    
    # Tarefas concluídas do dia específico
    total_concluidas = ConclusoesModel.objects.filter(
        tarefa__usuario=request.user,
        dia=dia_atual,
        concluido=True
    ).count()
    
    print(f"Tarefas do dia {dia_atual}: {total_tarefas}")
    print(f"Tarefas concluídas do dia {dia_atual}: {total_concluidas}")
    
    # Calcular a porcentagem de conclusão para o dia específico
    if total_tarefas > 0:
        porcentagem_conclusao = (total_concluidas / total_tarefas) * 100
    else:
        porcentagem_conclusao = 0
    
    print(f"Porcentagem de conclusão do dia {dia_atual}: {porcentagem_conclusao}%")
    
    
    # Criar uma lista de dicionários com as informações de cada tarefa do dia atual
    tarefas_com_status = []
    for tarefa in tarefas_do_dia:
        concluido = status_conclusao.get(tarefa.id, False)
        tarefas_com_status.append({
            'tarefa': tarefa,
            'concluido': concluido
        })

    # -----Informações da semana atual (mantidas para referência)--------
    data_hoje = localtime().date()
    
    # Calcular início da semana (segunda-feira)
    inicio_semana = data_hoje - timedelta(days=data_hoje.weekday())
    
    inicio_semana = make_aware(datetime.combine(inicio_semana, datetime.min.time()))
    
    # Calcular fim da semana (domingo)
    fim_semana = inicio_semana + timedelta(days=6, hours=23, minutes=59, seconds=59)
    fim_semana = make_aware(datetime.combine(fim_semana, datetime.max.time()))

    contexto = {
        "nome": request.user.username,
        "rotina": tarefas_com_status,
        "dias_semana_lista": dias_semana_lista,
        "dia_semana": dia_atual,
        "dia_atual": dia_atual,
        "dia_hoje": dia_hoje,
        "contagem_tarefas": contagem_tarefas,
        "total_tarefas": total_tarefas,
        "total_concluidas_semana": total_concluidas,  # Renomeado mas mantido para compatibilidade
        "porcentagem_conclusao": porcentagem_conclusao,
        "inicio_semana": inicio_semana,
        "fim_semana": fim_semana
    }
    
    return render(request, 'rotina/home.html', contexto)

@login_required
def rotina_adicionar(request: HttpRequest):
    if request.method == "POST":
        # pegar os dados do formulario
        formulario = TarefaForm(request.POST)
        # se o formulario for valido ele salva ele no nosso banco de dados
        # e retorna para a pagina home
        
        if formulario.is_valid():
            nova_tarefa = formulario.save(commit=False)
            nova_tarefa.usuario = request.user
            nova_tarefa.save()
            return redirect("rotina:home")
    
    contexto = {
        "form": TarefaForm()
    }
    return render(request, 'rotina/adicionar.html', contexto)

def rotina_remover(request: HttpRequest, id):
    tarefa = get_object_or_404(TarefaModel, id=id, usuario=request.user)
    tarefa.delete()
    return redirect("rotina:home")

def rotina_editar(request: HttpRequest, id):
    tarefa = get_object_or_404(TarefaModel, id=id, usuario=request.user)
    
    if request.method == 'POST':
        formulario = TarefaForm(request.POST, instance=tarefa)
        if formulario.is_valid():
            nova_tarefa = formulario.save(commit=False)
            nova_tarefa.usuario = request.user
            nova_tarefa.save()
            return redirect("rotina:home")
    
    formulario = TarefaForm(instance=tarefa)
    contexto = {
        "form": formulario
    }
    return render(request, 'rotina/editar.html', contexto)

def rotina_concluir(request: HttpRequest, id, dia):
    tarefa = get_object_or_404(TarefaModel, id=id, usuario=request.user)

    # Adicione log para depuração
    print(f"Tentando alternar conclusão da tarefa {id} para o dia {dia}")
    
    conclusao, created = ConclusoesModel.objects.get_or_create(
        tarefa=tarefa,
        dia=dia,
        defaults={'concluido': True, 'concluida_em': timezone.now()}
    )
    
    if not created:
        # Se já existe, apenas inverte o status
        conclusao.concluido = not conclusao.concluido
        
        # Atualiza ou limpa o timestamp conforme o estado de conclusão
        if conclusao.concluido:
            conclusao.concluida_em = timezone.now()
        else:
            conclusao.concluida_em = None
            
        conclusao.save()
        print(f"Data de conclusão salva: {conclusao.concluida_em}")
    
    print(f"Status atual da conclusão: {conclusao.concluido}")
    
    # Redirecionar para o mesmo dia que o usuário estava vendo
    return redirect(f'/rotina/?dia={dia}')