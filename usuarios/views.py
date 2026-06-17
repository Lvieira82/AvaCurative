from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def login_view(request):

    erro = None

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('home')

        erro = 'Usuário ou senha inválidos.'

    return render(
        request,
        'usuarios/login.html',
        {
            'erro': erro
        }
    )


def logout_view(request):

    logout(request)

    return redirect('login')


def cadastro_usuario(request):

    erro = None

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            erro = 'Usuário já existe.'

        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return redirect('login')

    return render(
        request,
        'usuarios/cadastro.html',
        {
            'erro': erro
        }
    )