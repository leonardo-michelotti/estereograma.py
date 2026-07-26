(() => {
    const input = document.querySelector("#depth-z");
    if (!input) return;

    const demo = document.querySelector(".v03-separation-demo");
    const depthOutput = document.querySelector("#depth-z-value");
    const separationOutput = document.querySelector("#separation-value");
    const explanation = document.querySelector("#separation-explanation");
    const eyeSeparation = 200;
    const mu = 0.333;

    function update() {
        const z = Number(input.value) / 100;
        const separation = Math.round(((1 - mu * z) * eyeSeparation) / (2 - mu * z));
        const visualSeparation = 42 + ((separation - 80) / 20) * 54;
        depthOutput.value = z.toFixed(2);
        separationOutput.value = separation;
        demo.style.setProperty("--separation", `${Math.max(42, Math.min(96, visualSeparation))}px`);

        if (z < 0.25) explanation.textContent = "No fundo, a separação fica maior e o ponto parece permanecer no plano da imagem.";
        else if (z > 0.75) explanation.textContent = "Perto do observador, a separação diminui e o ponto avança para fora do plano.";
        else explanation.textContent = "No meio do relevo, os pixels formam um par confortável para a fusão.";
    }

    input.addEventListener("input", update);
    update();
})();
