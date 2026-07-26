(() => {
    const root = document.querySelector(".v03-learn");
    if (!root) return;

    const steps = [
        {
            kicker: "PASSO 1 DE 3",
            title: "Aproxime o rosto da imagem",
            description: "Chegue perto até o padrão perder a nitidez. Não tente identificar a figura ainda.",
            distance: "5 cm da tela",
            eyeGuide: "relaxe o foco",
        },
        {
            kicker: "PASSO 2 DE 3",
            title: "Funda os dois pontos",
            description: "Relaxe o foco e olhe através da tela. Os dois pontos coral devem parecer três; mantenha o ponto central estável.",
            distance: "funda os pontos",
            eyeGuide: "una os dois pontos",
        },
        {
            kicker: "PASSO 3 DE 3",
            title: "Afaste-se bem devagar",
            description: "Mantenha o foco relaxado enquanto aumenta a distância. Quando o coração surgir, pare e deixe o cérebro estabilizar as duas camadas.",
            distance: "30–50 cm da tela",
            eyeGuide: "mantenha a fusão",
        },
    ];

    let current = 0;
    const kicker = root.querySelector("#step-kicker");
    const title = root.querySelector("#step-title");
    const description = root.querySelector("#step-description");
    const distance = root.querySelector("#focus-distance");
    const eyeGuide = root.querySelector("#eye-guide-label");
    const previous = root.querySelector("#previous-step");
    const next = root.querySelector("#next-step");
    const helpButton = root.querySelector("#need-help");
    const helpPanel = root.querySelector("#help-panel");
    const complete = root.querySelector("#tutorial-complete");
    const instruction = root.querySelector("#tutorial-instruction");
    const tabs = [...root.querySelectorAll("[data-step]")];

    function renderStep(index) {
        current = index;
        const step = steps[index];
        kicker.textContent = step.kicker;
        title.textContent = step.title;
        description.textContent = step.description;
        distance.textContent = step.distance;
        eyeGuide.textContent = step.eyeGuide;
        previous.hidden = index === 0;
        next.textContent = index === steps.length - 1 ? "Concluir treino" : "Próximo passo";
        instruction.hidden = false;
        complete.hidden = true;
        tabs.forEach((tab, tabIndex) => {
            if (tabIndex === index) tab.setAttribute("aria-current", "step");
            else tab.removeAttribute("aria-current");
        });
    }

    tabs.forEach((tab) => tab.addEventListener("click", () => renderStep(Number(tab.dataset.step))));
    previous.addEventListener("click", () => renderStep(Math.max(0, current - 1)));
    next.addEventListener("click", () => {
        if (current < steps.length - 1) {
            renderStep(current + 1);
            return;
        }
        instruction.hidden = true;
        previous.hidden = true;
        next.hidden = true;
        complete.hidden = false;
        complete.querySelector("a").focus();
    });

    helpButton.addEventListener("click", () => {
        const expanded = helpButton.getAttribute("aria-expanded") === "true";
        helpButton.setAttribute("aria-expanded", String(!expanded));
        helpPanel.hidden = expanded;
    });

    renderStep(0);
})();
