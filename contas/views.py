from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

def cadastro_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('rotina:home')  # redireciona para sua home de tarefas
    else:
        form = UserCreationForm()
    return render(request, 'contas/cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('rotina:home')
    else:
        form = AuthenticationForm()
    return render(request, 'contas/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('contas:login')  # redireciona para login após logout
