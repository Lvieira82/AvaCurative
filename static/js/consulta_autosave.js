(function () {
    "use strict";

    const form = document.querySelector("form");
    if (!form) return;

    let consultaId = form.dataset.consultaId;
    let autosaveUrl = form.dataset.autosaveUrl;

    const statusEl = document.getElementById("autosave-status");

    // Enquanto a consulta ainda não existe no banco, usamos uma chave
    // baseada na URL da nova consulta para preservar o que foi digitado.
    const chaveNovaConsulta = "ava_curative_nova_" + window.location.pathname;
    const storageKey = consultaId
        ? "ava_curative_consulta_" + consultaId
        : chaveNovaConsulta;

    let enviando = false;
    let rascunhoCriado = Boolean(consultaId && autosaveUrl);

    function mostrarStatus(texto) {
        if (statusEl) {
            statusEl.textContent = texto;
        }
    }

    function coletarDados() {
        const dados = {};

        form.querySelectorAll("input, textarea, select").forEach(function (campo) {
            if (
                !campo.name ||
                campo.name === "csrfmiddlewaretoken" ||
                campo.name === "fotos"
            ) {
                return;
            }

            if (campo.type === "checkbox") {
                dados[campo.name] = campo.checked;
            } else if (campo.type !== "file") {
                dados[campo.name] = campo.value;
            }
        });

        return dados;
    }

    function guardarLocal() {
        try {
            localStorage.setItem(
                storageKey,
                JSON.stringify({
                    dados: coletarDados(),
                    salvoLocalmenteEm: new Date().toISOString()
                })
            );
        } catch (e) {
            console.warn("Não foi possível usar localStorage.", e);
        }
    }

    function removerLocal() {
        try {
            localStorage.removeItem(storageKey);
        } catch (e) {}
    }

    function recuperarLocal() {
        try {
            const bruto = localStorage.getItem(storageKey);
            if (!bruto) return;

            const pacote = JSON.parse(bruto);
            if (!pacote || !pacote.dados) return;

            Object.keys(pacote.dados).forEach(function (nome) {
                const campo = form.querySelector(
                    '[name="' + CSS.escape(nome) + '"]'
                );

                if (!campo) return;

                if (campo.type === "checkbox") {
                    campo.checked = Boolean(pacote.dados[nome]);
                } else {
                    campo.value = pacote.dados[nome];
                }
            });

            mostrarStatus("Rascunho recuperado do navegador");
        } catch (e) {
            console.warn("Não foi possível recuperar o rascunho local.", e);
        }
    }

    async function criarRascunhoNoServidor() {
        if (rascunhoCriado || enviando) return;

        enviando = true;
        guardarLocal();
        mostrarStatus("Criando rascunho seguro...");

        const dados = new FormData(form);

        try {
            const resposta = await fetch(form.action || window.location.href, {
                method: "POST",
                body: dados,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                credentials: "same-origin"
            });

            if (!resposta.ok) {
                throw new Error("Não foi possível criar o rascunho.");
            }

            // nova_consulta redireciona para /consulta/editar/<id>/.
            // O navegador passa então a trabalhar com o ID real da consulta.
            if (resposta.redirected && resposta.url) {
                removerLocal();
                window.location.assign(resposta.url);
                return;
            }

            throw new Error("O servidor não criou o rascunho.");
        } catch (erro) {
            mostrarStatus(
                "⚠ Servidor indisponível — cópia local preservada"
            );
            console.warn(erro);
            enviando = false;
        }
    }

    async function enviarAutosave() {
        if (!rascunhoCriado || !autosaveUrl || enviando) return;

        guardarLocal();

        const dados = new FormData(form);
        dados.delete("fotos");

        enviando = true;
        mostrarStatus("Salvando rascunho...");

        try {
            const resposta = await fetch(autosaveUrl, {
                method: "POST",
                body: dados,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                credentials: "same-origin"
            });

            if (!resposta.ok) {
                const json = await resposta.json().catch(function () {
                    return {};
                });

                throw new Error(
                    json.erro || "Falha no autosave."
                );
            }

            const resultado = await resposta.json();

            if (resultado.ok) {
                mostrarStatus(
                    "✓ Rascunho salvo automaticamente às " +
                    resultado.salvo_em
                );

                removerLocal();
            }
        } catch (erro) {
            mostrarStatus(
                "⚠ Sem sincronização com o servidor — cópia local preservada"
            );
            console.warn(erro);
        } finally {
            enviando = false;
        }
    }

    // Preserva localmente cada alteração imediatamente.
    form.addEventListener("input", function () {
        guardarLocal();

        // Na primeira digitação, a consulta ainda não existe no banco.
        // Criamos o rascunho imediatamente para que os próximos autosaves
        // de 10 segundos tenham um ID real para atualizar.
        if (!rascunhoCriado) {
            criarRascunhoNoServidor();
        }
    });

    form.addEventListener("change", function () {
        guardarLocal();

        if (!rascunhoCriado) {
            criarRascunhoNoServidor();
        }
    });

    recuperarLocal();

    // Autosave oficial no banco a cada 10 segundos.
    setInterval(enviarAutosave, 10000);

    // Se faltar energia ou a página for fechada antes do primeiro envio,
    // os dados continuam disponíveis no navegador.
    window.addEventListener("beforeunload", guardarLocal);

})();
