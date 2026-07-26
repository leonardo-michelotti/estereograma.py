(() => {
    const form = document.querySelector("#studio-form");
    if (!form) return;

    const status = document.querySelector("#studio-status");
    const canvasLabel = document.querySelector("#canvas-label");
    const errorSlot = document.querySelector("#studio-error-slot");
    const overlay = document.querySelector("#generation-overlay");
    const eyeInput = document.querySelector("#eye_separation");
    const eyeValue = document.querySelector("#eye-value");

    const selectedValue = (name) => form.querySelector(`[name="${name}"]:checked`)?.value;
    const selectedLabel = (name) => form.querySelector(`[name="${name}"]:checked + label span:last-child`)?.textContent
        || form.querySelector(`[name="${name}"]:checked + label`)?.textContent?.trim();

    function syncSubject() {
        const subjectType = selectedValue("subject_type");
        document.querySelectorAll("[data-subject-panel]").forEach((panel) => {
            panel.hidden = panel.dataset.subjectPanel !== subjectType;
        });
        updateCanvasLabel();
    }

    function updateCanvasLabel() {
        const subject = selectedValue("subject_type") === "text"
            ? (document.querySelector("#text_subject")?.value || "texto")
            : (selectedLabel("subject") || "esfera");
        const texture = selectedLabel("texture") || "mosaico";
        canvasLabel.textContent = `prévia · ${subject.toLowerCase()} · ${texture.toLowerCase()}`;
    }

    function clearError() {
        errorSlot.hidden = true;
        errorSlot.replaceChildren();
    }

    form.addEventListener("change", (event) => {
        if (event.target.name === "subject_type") syncSubject();
        updateCanvasLabel();
    });
    form.addEventListener("input", updateCanvasLabel);
    eyeInput.addEventListener("input", () => { eyeValue.value = eyeInput.value; });

    form.addEventListener("htmx:beforeRequest", () => {
        clearError();
        overlay.hidden = false;
        form.classList.add("is-generating");
        status.textContent = "Gerando uma nova versão sem apagar o resultado anterior.";
    });

    form.addEventListener("htmx:afterRequest", (event) => {
        overlay.hidden = true;
        form.classList.remove("is-generating");
        if (event.detail.successful) status.textContent = "Resultado pronto. Revele, varie, baixe ou compartilhe.";
    });

    form.addEventListener("htmx:responseError", (event) => {
        errorSlot.innerHTML = event.detail.xhr.responseText;
        errorSlot.hidden = false;
        status.textContent = "A geração falhou, mas o último resultado continua disponível.";
    });

    document.addEventListener("click", async (event) => {
        const dismiss = event.target.closest("[data-dismiss-error]");
        if (dismiss) {
            clearError();
            form.querySelector("input, button, select")?.focus();
            return;
        }

        if (event.target.closest("[data-vary]")) {
            document.querySelector("#seed").value = "";
            form.requestSubmit();
            return;
        }

        const copyButton = event.target.closest("[data-copy-link]");
        if (copyButton) {
            const render = copyButton.closest("[data-subject-type]");
            const query = new URLSearchParams({
                subject_type: render.dataset.subjectType,
                subject: render.dataset.subject,
                texture: render.dataset.texture,
                depth: render.dataset.depth,
                seed: render.dataset.seed,
                eye_separation: render.dataset.eyeSeparation,
            });
            const url = `${window.location.origin}/studio?${query}`;
            try {
                await navigator.clipboard.writeText(url);
                status.textContent = "Link reproduzível copiado.";
            } catch {
                window.prompt("Copie o link do resultado:", url);
            }
        }
    });

    syncSubject();
})();
