// ---------- Modo oscuro / claro ----------
// El diseño nace oscuro (estética Y2K). El modo claro se guarda en localStorage.
const CLAVE_TEMA = "tema-lista-tareas";
const themeButton = document.querySelector("#theme-toggle");
const themeLabel = document.querySelector("#theme-label");

function leerTemaGuardado() {
    try {
        return localStorage.getItem(CLAVE_TEMA);
    } catch (e) {
        return null; // por si el navegador bloquea localStorage
    }
}

function aplicarTema(tema) {
    document.documentElement.dataset.theme = tema;
    const oscuro = tema === "dark";
    // El botón muestra la acción que va a ocurrir al hacer clic.
    themeLabel.textContent = oscuro ? "Modo claro" : "Modo oscuro";
    themeButton.setAttribute("aria-label", oscuro ? "Activar modo claro" : "Activar modo oscuro");
}

aplicarTema(leerTemaGuardado() === "light" ? "light" : "dark");

themeButton.addEventListener("click", () => {
    const nuevo = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    aplicarTema(nuevo);
    try {
        localStorage.setItem(CLAVE_TEMA, nuevo);
    } catch (e) {}
});

// ---------- Confirmar eliminación ----------
document.querySelectorAll(".delete-form").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
        if (!window.confirm(formulario.dataset.confirm)) {
            evento.preventDefault();
        }
    });
});
