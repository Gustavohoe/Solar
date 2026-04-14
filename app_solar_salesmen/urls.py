from django.urls import path 
from . import views



urlpatterns=[
    path('', views.login, name="login"),
    path('cadastro/', views.cadastro, name="cadastro"),
    path('diretoria/', views.diretoria, name="diretoria"),
    path('pagina-Inicial/', views.paginaInicial, name="paginaInicial"),
    path('tornar-admin/', views.tornar_admin, name='tornar_admin'),
    path('realizar-venda/', views.realizar_venda, name='realizar_venda'),
    path('make-graph/', views.makegraph, name='make_graph'),
    path('adicionar-produto/', views.adicionar_produto, name='adicionar_produto'),
    path('editar-venda/', views.editar_venda, name='editar_venda'),
    path('logout/', views.logout_view, name='logout'),

]