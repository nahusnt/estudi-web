// Guarda la preferencia de tema entre visitas.
const themeButton = document.querySelector("#theme-toggle");
const themeLabel = document.querySelector("#theme-label");
const savedTheme = localStorage.getItem("tema-lista-tareas");

if (savedTheme === "dark") {
    document.documentElement.dataset.theme = "dark";
}

function actualizarBotonTema() {
    const oscuro = document.documentElement.dataset.theme === "dark";
    themeLabel.textContent = oscuro ? "Modo claro" : "Modo oscuro";
    themeButton.setAttribute("aria-label", oscuro ? "Activar modo claro" : "Activar modo oscuro");
}

actualizarBotonTema();
themeButton.addEventListener("click", () => {
    const oscuro = document.documentElement.dataset.theme !== "dark";
    document.documentElement.dataset.theme = oscuro ? "dark" : "light";
    localStorage.setItem("tema-lista-tareas", oscuro ? "dark" : "light");
    actualizarBotonTema();
});

// Confirma la eliminacion para evitar borrar tareas por accidente.
document.querySelectorAll(".delete-form").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
        if (!window.confirm(formulario.dataset.confirm)) {
            evento.preventDefault();
        }
    });
});