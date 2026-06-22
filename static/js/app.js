document.addEventListener("DOMContentLoaded", function () {

    const inputBusca = document.getElementById("buscaPaciente");
    const resultado = document.getElementById("resultadoAutocomplete");

    if (inputBusca && resultado) {

        inputBusca.addEventListener("input", function () {

            const termo = inputBusca.value.trim();

            if (termo.length < 2) {
                resultado.innerHTML = "";
                return;
            }

            fetch(`/pacientes/autocomplete/?q=${encodeURIComponent(termo)}`)
                .then(response => response.json())
                .then(data => {

                    resultado.innerHTML = "";

                    if (data.length === 0) {
                        resultado.innerHTML = `
                            <div class="autocomplete-vazio">
                                Nenhum paciente encontrado.
                            </div>
                        `;
                        return;
                    }

                    data.forEach(function (paciente) {

                        const item = document.createElement("a");

                        item.href = paciente.url;
                        item.classList.add("autocomplete-item");

                        item.innerHTML = `
                            <strong>${paciente.nome}</strong>
                            <span>Nascimento: ${paciente.data_nascimento || ""}</span>
                        `;

                        resultado.appendChild(item);
                    });
                })
                .catch(error => {
                    console.error("Erro no autocomplete:", error);
                });
        });
    }

});
document.addEventListener("DOMContentLoaded", function () {

    const tipoBloqueio = document.getElementById("tipoBloqueio");
    const campoDataFim = document.getElementById("campoDataFim");
    const campoHoras = document.getElementById("campoHoras");

    if (tipoBloqueio) {

        tipoBloqueio.addEventListener("change", function () {

            campoDataFim.style.display = "none";
            campoHoras.style.display = "none";

            if (tipoBloqueio.value === "PERIODO") {
                campoDataFim.style.display = "block";
            }

            if (tipoBloqueio.value === "HORARIO") {
                campoHoras.style.display = "block";
            }

        });
    }

});
document.addEventListener("DOMContentLoaded", function () {

    const inputFotos = document.getElementById("inputFotosConsulta");
    const previewFotos = document.getElementById("previewFotosConsulta");

    if (inputFotos && previewFotos) {

        let arquivosSelecionados = [];

        inputFotos.addEventListener("change", function () {

            arquivosSelecionados = Array.from(inputFotos.files);

            if (arquivosSelecionados.length > 6) {
                alert("Você pode anexar no máximo 6 fotos.");
                inputFotos.value = "";
                previewFotos.innerHTML = "";
                arquivosSelecionados = [];
                return;
            }

            atualizarPreview();
        });

        function atualizarPreview() {

            previewFotos.innerHTML = "";

            const dataTransfer = new DataTransfer();

            arquivosSelecionados.forEach(function (arquivo, index) {

                dataTransfer.items.add(arquivo);

                const leitor = new FileReader();

                leitor.onload = function (evento) {

                    const card = document.createElement("div");
                    card.classList.add("preview-foto-card");

                    const botaoRemover = document.createElement("button");
                    botaoRemover.type = "button";
                    botaoRemover.textContent = "×";
                    botaoRemover.classList.add("remover-foto");

                    botaoRemover.addEventListener("click", function () {
                        arquivosSelecionados.splice(index, 1);
                        atualizarPreview();
                    });

                    const imagem = document.createElement("img");
                    imagem.src = evento.target.result;

                    card.appendChild(botaoRemover);
                    card.appendChild(imagem);

                    previewFotos.appendChild(card);
                };

                leitor.readAsDataURL(arquivo);
            });

            inputFotos.files = dataTransfer.files;
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {

    const buscaPaciente = document.getElementById("buscaPacienteAgenda");
    const pacienteId = document.getElementById("pacienteIdAgenda");
    const resultado = document.getElementById("resultadoPacienteAgenda");

    const dataAgenda = document.getElementById("dataAgenda");
    const horariosDiv = document.getElementById("horariosDisponiveis");
    const horaSelecionada = document.getElementById("horaSelecionada");

    if (!buscaPaciente || !resultado) {
        return;
    }

    buscaPaciente.addEventListener("input", function () {

        const termo = buscaPaciente.value.trim();

        pacienteId.value = "";
        resultado.innerHTML = "";

        if (termo.length < 2) {
            return;
        }

        fetch(`/pacientes/autocomplete/?q=${encodeURIComponent(termo)}`)
            .then(response => response.json())
            .then(data => {

                resultado.innerHTML = "";

                data.forEach(function (paciente) {

                    const item = document.createElement("div");
                    item.classList.add("autocomplete-item");

                    item.innerHTML = `
                        <strong>${paciente.nome}</strong>
                    `;

                    item.addEventListener("click", function () {
                        buscaPaciente.value = paciente.nome;
                        pacienteId.value = paciente.id;
                        resultado.innerHTML = "";
                    });

                    resultado.appendChild(item);
                });
            });
    });

    dataAgenda.addEventListener("change", carregarHorarios);
    if (dataAgenda.value) {
        carregarHorarios();
    }
    if (!dataAgenda.value) {
        const hoje = new Date().toISOString().split("T")[0];
        dataAgenda.value = hoje;
        carregarHorarios();
    }

    function carregarHorarios() {

        const data = dataAgenda.value;

        horariosDiv.innerHTML = "";
        horaSelecionada.value = "";

        const cardAgendamentos = document.getElementById("cardAgendamentosDia");
        const listaAgendamentos = document.getElementById("listaAgendamentosDia");

        if (cardAgendamentos && listaAgendamentos) {
            cardAgendamentos.style.display = "none";
            listaAgendamentos.innerHTML = "";
        }

        if (!data) {
            return;
        }

        fetch(`/agenda/horarios/?data=${data}`)
            .then(response => response.json())
            .then(data => {

                horariosDiv.innerHTML = "";
                atualizarListaDia(
                    data.horarios,
                    dataAgenda.value
                );

                if (cardAgendamentos && listaAgendamentos) {
                    cardAgendamentos.style.display = "block";
                }

                data.horarios.forEach(function (item) {

                    const linha = document.createElement("div");
                    linha.classList.add("linha-agendamento-dia");

                    if (item.disponivel) {
                        linha.innerHTML = `
                            <strong>${item.hora}</strong> - Livre
                        `;
                        linha.classList.add("linha-livre");
                    } else {
                        linha.innerHTML = `
                            <strong>${item.hora}</strong> - Bloqueado
                        `;
                        linha.classList.add("linha-bloqueada");
                    }

                    if (listaAgendamentos) {
                        listaAgendamentos.appendChild(linha);
                    }

                    const botao = document.createElement("button");
                    botao.type = "button";
                    botao.textContent = item.hora;

                    if (item.disponivel) {

                        botao.classList.add("horario-livre");

                        botao.addEventListener("click", function () {

                            document
                                .querySelectorAll(".horario-livre")
                                .forEach(btn => btn.classList.remove("selecionado"));

                            botao.classList.add("selecionado");
                            horaSelecionada.value = item.hora;
                        });

                    } else {

                        botao.classList.add("horario-bloqueado");
                        botao.disabled = true;
                    }

                    horariosDiv.appendChild(botao);
                });
            });
    }
    });
const cardAgendamentos =
document.getElementById("cardAgendamentosDia");

const listaAgendamentos =
document.getElementById("listaAgendamentosDia");

function atualizarListaDia(horarios, dataSelecionada){

    const cardAgendamentos =
    document.getElementById("cardAgendamentosDia");

    const listaAgendamentos =
    document.getElementById("listaAgendamentosDia");

    if(!cardAgendamentos || !listaAgendamentos){
        return;
    }

    cardAgendamentos.style.display = "block";
    listaAgendamentos.innerHTML = "";

    horarios.forEach(function(item){

        const linha = document.createElement("div");

        linha.classList.add("linha-agendamento-dia");

        if(item.tipo === "livre"){

            linha.classList.add("linha-livre");

            linha.innerHTML = `
                <strong>${item.hora}</strong> - Livre
            `;
        }

        if(item.tipo === "bloqueio"){

            linha.classList.add("linha-bloqueada");

            linha.innerHTML = `
                <strong>${item.hora}</strong> - Horário bloqueado

                <a href="/agenda/desbloquear/?data=${dataSelecionada}&hora=${item.hora}"
                   class="btn-desbloquear">
                    Desbloquear
                </a>
            `;
        }

        if(item.tipo === "consulta"){

            linha.classList.add("linha-consulta");

            linha.innerHTML = `
                <strong>${item.hora}</strong> -
                ${item.paciente}

                <a href="/agenda/desmarcar/${item.id}/"
                   class="btn-desmarcar"
                   onclick="return confirm('Deseja realmente desmarcar esta consulta?')">
                    Desmarcar
                </a>
            `;
        }

        listaAgendamentos.appendChild(linha);
    });
}
document.addEventListener("DOMContentLoaded", function () {

    const buscarAgendado = document.getElementById("buscarAgendado");
    const pacienteAgendadoId = document.getElementById("pacienteAgendadoId");
    const resultadoAuto = document.getElementById("resultadoAgendadoAutocomplete");
    const resultadoAgenda = document.getElementById("resultadoAgendamentosPaciente");

    if (!buscarAgendado || !pacienteAgendadoId || !resultadoAuto || !resultadoAgenda) {
        return;
    }

    buscarAgendado.addEventListener("input", function () {

        const termo = buscarAgendado.value.trim();

        resultadoAuto.innerHTML = "";
        resultadoAgenda.innerHTML = "";
        pacienteAgendadoId.value = "";

        if (termo.length < 2) {
            return;
        }

        fetch("/pacientes/autocomplete/?q=" + encodeURIComponent(termo))
            .then(response => response.json())
            .then(data => {

                resultadoAuto.innerHTML = "";

                if (data.length === 0) {
                    resultadoAuto.innerHTML = `
                        <div class="autocomplete-vazio">
                            Nenhum paciente encontrado.
                        </div>
                    `;
                    return;
                }

                data.forEach(function (paciente) {

                    const item = document.createElement("div");
                    item.classList.add("autocomplete-item");

                    item.innerHTML = `
                        <strong>${paciente.nome}</strong>
                    `;

                    item.addEventListener("click", function () {

                        buscarAgendado.value = paciente.nome;
                        pacienteAgendadoId.value = paciente.id;
                        resultadoAuto.innerHTML = "";

                        carregarAgendamentosPaciente(paciente.id);
                    });

                    resultadoAuto.appendChild(item);
                });
            })
            .catch(error => {
                console.error("Erro no autocomplete consultar agendados:", error);
            });
    });

    function carregarAgendamentosPaciente(id) {

        resultadoAgenda.innerHTML = "Carregando...";

        fetch("/agenda/consultar-agendados/?paciente_id=" + id)
            .then(response => response.json())
            .then(retorno => {

                resultadoAgenda.innerHTML = "";

                if (retorno.resultados.length === 0) {
                    resultadoAgenda.innerHTML = `
                        <p class="sem-agendamento">
                            Nenhum agendamento encontrado.
                        </p>
                    `;
                    return;
                }

                retorno.resultados.forEach(function (ag) {

                    const linha = document.createElement("div");
                    linha.classList.add("linha-consulta-paciente");

                    linha.innerHTML = `
                        <strong>${ag.data}</strong> -
                        <strong>${ag.hora}</strong> -
                        ${ag.paciente}

                        <a href="/agenda/desmarcar/${ag.id}/"
                           class="btn-desmarcar"
                           onclick="return confirm('Deseja realmente desmarcar esta consulta?')">
                            Desmarcar
                        </a>
                    `;

                    resultadoAgenda.appendChild(linha);
                });
            })
            .catch(error => {
                console.error("Erro ao consultar agendamentos:", error);
            });
    }

});