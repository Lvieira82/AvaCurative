(function () {
    "use strict";

    const form = document.querySelector("form");
    if (!form) return;

    const consultaId = form.dataset.consultaId;
    const autosaveUrl = form.dataset.autosaveUrl;

    if (!consultaId || !autosaveUrl) return;

    const statusEl = document.getElementById("autosave-status");
    const storageKey = "ava_curative_consulta_" + consultaId;

    let enviando = false;

    function mostrarStatus(texto) {
        if (statusEl) {
            statusEl.textContent = texto;
        }
    }

    function coletarDados() {
        const dados = {};

        form.querySelectorAll("input, textarea, select").forEach(function (campo) {
            if (!campo.name || campo.name === "csrfmiddlewaretoken" || campo.name === "fotos") {
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

    function recuperarLocal() {
        try {
            const bruto = localStorage.getItem(storageKey);
            if (!bruto) return;

            const pacote = JSON.parse(bruto);
            if (!pacote || !pacote.dados) return;

            Object.keys(pacote.dados).forEach(function (nome) {
                const campo = form.querySelector('[name="' + CSS.escape(nome) + '"]');
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

    function enviarAutosave() {
        if (enviando) return;

        guardarLocal();

        const dados = new FormData(form);
        dados.delete("fotos");

        enviando = true;
        mostrarStatus("Salvando...");

        fetch(autosaveUrl, {
            method: "POST",
            body: dados,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            credentials: "same-origin"
        })
        .then(function (resposta) {
            if (!resposta.ok) {
                return resposta.json().catch(function () {
                    return {};
                }).then(function (json) {
                    throw new Error(json.erro || "Falha no autosave.");
                });
            }

            return resposta.json();
        })
        .then(function (resultado) {
            if (resultado.ok) {
                mostrarStatus(
                    "✓ Rascunho salvo automaticamente às " +
                    resultado.salvo_em
                );

                try {
                    localStorage.removeItem(storageKey);
                } catch (e) {}
            }
        })
        .catch(function (erro) {
            mostrarStatus(
                "⚠ Sem sincronização com o servidor — cópia local preservada"
            );
            console.warn(erro);
        })
        .finally(function () {
            enviando = false;
        });
    }

    // Guarda imediatamente no navegador enquanto a pessoa digita.
    form.addEventListener("input", guardarLocal);
    form.addEventListener("change", guardarLocal);

    // Tenta recuperar uma cópia local ao abrir.
    recuperarLocal();

    // Autosave oficial no banco a cada 10 segundos.
    setInterval(enviarAutosave, 10000);

    // Faz uma tentativa antes de fechar/recarregar.
    window.addEventListener("beforeunload", guardarLocal);

})();
