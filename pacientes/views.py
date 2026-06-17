from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Paciente
from .forms import PacienteForm
from django.http import JsonResponse
from consultas.models import Consulta


@login_required
def home(request):

    return render(
        request,
        'home.html'
    )


@login_required
def cadastrar_paciente(request):

    if request.method == 'POST':
        form = PacienteForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = PacienteForm()

    return render(
        request,
        'pacientes/form_paciente.html',
        {
            'form': form
        }
    )


@login_required
def buscar_paciente(request):

    return render(
        request,
        "pacientes/buscar.html"
    )
    
@login_required
def autocomplete_pacientes(request):

    termo = request.GET.get("q", "")

    pacientes = (
        Paciente.objects
        .filter(nome__icontains=termo)
        .order_by("nome")[:10]
    )

    dados = []

    for paciente in pacientes:

        data_nascimento = ""

        if paciente.data_nascimento:
            data_nascimento = paciente.data_nascimento.strftime("%d/%m/%Y")

        dados.append({
            "id": paciente.id,
            "nome": paciente.nome,
            "data_nascimento": data_nascimento,
            "url": f"/paciente/{paciente.id}/arquivo/"
        })

    return JsonResponse(dados, safe=False)

@login_required
def arquivo_paciente(request, id):

    paciente = get_object_or_404(
        Paciente,
        id=id
    )

    consultas = (
        Consulta.objects
        .filter(paciente=paciente)
        .order_by("-criada_em")
    )

    tem_consultas = consultas.exists()

    return render(
        request,
        "pacientes/arquivo.html",
        {
            "paciente": paciente,
            "consultas": consultas,
            "tem_consultas": tem_consultas,
        }
    )


@login_required
def historico_consultas(request, id):

    paciente = get_object_or_404(
        Paciente,
        id=id
    )

    consultas = (
        Consulta.objects
        .filter(paciente=paciente)
        .order_by("-criada_em")
    )

    return render(
        request,
        "consultas/historico.html",
        {
            "paciente": paciente,
            "consultas": consultas,
        }
    )
