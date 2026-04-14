from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Produto, Venda
import json
import sqlite3 as sql
import pandas as pd
import plotly.express as px

def login(request):
    if request.method =="GET":
        return render(request, "login.html")
    else:
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        
        user=authenticate(username=username, password=senha)

        if user:
            login_django(request, user)
            if user.groups.filter(name='admin').exists():
                return redirect('diretoria')  
            else:
                return redirect('paginaInicial') 
        else:
            messages.error(request, 'Username ou senha invalidos')
            return render(request, 'login.html')
        

def cadastro(request):
    if request.method=='GET':
        return render(request, "cadastro.html")
    else:
        email=request.POST.get('email')
        username=request.POST.get('username')
        senha=request.POST.get('senha')
        confirmar_senha=request.POST.get('confirmar_senha')
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem!")
            return render(request, "cadastro.html")
        
        if User.objects.filter(username=username).first():
            messages.error(request,'Já existe um usuário com esse username')
            return render(request, "cadastro.html")
        user=User.objects.create_user(username=username, email=email, password=senha)
        user.save()

        return redirect('login')

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

@user_passes_test(is_admin, login_url='paginaInicial')
def diretoria(request):
    usuarios = User.objects.filter(is_staff=False).exclude(id=request.user.id)
    usuariosf = User.objects.filter(is_staff=True).exclude(id=request.user.id)
    return render(request, 'diretoria.html', {
        'usuarios': usuarios,
        'usuariosf': usuariosf
        })

@user_passes_test(is_admin, login_url='paginaInicial')
def tornar_admin(request):
     if request.method == "POST":
        user_id= request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        grupo, _ = Group.objects.get_or_create(name='admin')
        acao = request.POST.get('acao')
        if acao=="tornar":
            user.groups.add(grupo)
        else:
            user.groups.remove(grupo)
        return redirect('diretoria')
     
@login_required     
def paginaInicial(request):
    produtos = Produto.objects.all()
    vendas = Venda.objects.filter(vendedor=request.user)
    return render(request, 'vendedor.html', {
        'Produtos': produtos,  # tem que ser exatamente 'Produtos' para bater com o template
        'vendas': vendas
    })

def makegraph(request):
    if request.method == "POST":
        graphtype = request.POST.get('graphtype')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        vendas = Venda.objects.select_related('vendedor', 'produto').all()
        if data_inicio:
            vendas = Venda.filter(date__gte=data_inicio)
        if data_fim:
            vendas = Venda.filter(date__lte=data_fim)
        rows = [(v.vendedor.username, v.produto.nome, v.qtd, v.fat) for v in vendas]
        df = pd.DataFrame(rows, columns=['vendedor', 'produto', 'qtd', 'fat'])
        if graphtype == 'bar':
            eixo_x_col = request.POST.get('eixo_x')
            y = request.POST.get('eixo_y')
            if eixo_x_col == "id_v":
                x = 'vendedor' 
                colors = 'produto' 
            else:
                x = 'produto'
                colors = 'vendedor'
            fig = px.bar(df, x=x, y=y, color=colors)
        elif graphtype == 'pie':
            names = request.POST.get('names')
            values = request.POST.get('values')
            fig = px.pie(df, names=names, values=values)
        return JsonResponse({'fig': fig.to_html(full_html=False)})
        
@login_required
def realizar_venda(request):
    if request.method == "POST":
        produto_id = request.POST.get("selection")
        quantidade = int(request.POST.get("qtd"))
        produto = get_object_or_404(Produto, id=produto_id)
        if produto.estoque >= quantidade:
            Venda.objects.create(
                produto=produto,
                vendedor=request.user,
                qtd=quantidade,
                fat=produto.valor*quantidade
            )
            produto.estoque -= quantidade
            produto.save()
            return JsonResponse({'mensagem': 'Venda realizada com sucesso!'})
        else:
            return JsonResponse({'mensagem': 'Estoque insuficiente.'})
    produtos = Produto.objects.all()
    vendas = Venda.objects.filter(vendedor=request.user)
    return render(request, 'vendedor.html', {'Produtos': produtos, 'vendas': vendas})


@login_required
def listar_vendas(request):
    produtos = Produto.objects.all()
    vendas = Venda.objects.filter(vendedor=request.user)
    return render(request, "vendedor.html", {
        "produtos": produtos,
        "vendas": vendas
        })

def adicionar_produto(request):
    if request.method == "POST":
        dados = json.loads(request.body)
        nome = dados.get('nome')
        valor = float(dados.get('valor'))
        estoque = int(dados.get('estoque'))

        Produto.objects.create(nome=nome, valor=valor, estoque=estoque)
        return JsonResponse({'sucesso': True})
    
@login_required
def editar_venda(request):
    if request.method == "POST":
        venda_id = request.POST.get("venda_id")
        nova_qtd = request.POST.get("qtd")

        if not venda_id or not nova_qtd:
            return JsonResponse({'mensagem': 'Dados inválidos'})

        venda = get_object_or_404(Venda, id=venda_id)

        if venda.vendedor != request.user:
            return JsonResponse({'mensagem': 'Sem permissão'})

        nova_qtd = int(nova_qtd)

        venda.qtd = nova_qtd
        venda.fat = venda.produto.valor * nova_qtd
        venda.save()
        
        return JsonResponse({'mensagem': 'Venda atualizada com sucesso!'})

    return JsonResponse({'mensagem': 'Erro'})

def logout_view(request):
    logout(request)
    return redirect('login')