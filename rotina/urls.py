from django.urls import path
from . import views

app_name = 'rotina'

urlpatterns = [
    path('', views.rotina_home, name='home'),
    path('adicionar/', views.rotina_adicionar, name='adicionar'),
    path('remover/<int:id>', views.rotina_remover, name='remover'),
    path('editar/<int:id>', views.rotina_editar, name='editar'),
    # Atualize esta linha para incluir o parâmetro dia
    path('concluir/<int:id>/<str:dia>', views.rotina_concluir, name='concluir'),
]