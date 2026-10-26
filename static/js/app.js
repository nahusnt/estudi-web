// ---------- Modo oscuro / claro ----------
// El diseño nace oscuro (estética Y2K). El modo claro se guarda en localStorage.
const CLAVE_TEMA = "tema-lista-tareas";
const CLAVE_LISTA_COMPACTA = "lista-tareas-compacta";
const themeButton = document.querySelector("#theme-toggle");
const themeLabel = document.querySelector("#theme-label");
const themeSetting = document.querySelector("#theme-setting");
const densitySetting = document.querySelector("#density-setting");

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
    themeLabel.textContent = oscuro ? "Modo claro" : "Modo oscuro";
    themeButton.setAttribute("aria-label", oscuro ? "Activar modo claro" : "Activar modo oscuro");
    themeSetting.value = tema;
}

aplicarTema(leerTemaGuardado() === "light" ? "light" : "dark");
document.documentElement.dataset.density =
    leerPreferencia(CLAVE_LISTA_COMPACTA) === "true" ? "compact" : "comfortable";
densitySetting.checked = document.documentElement.dataset.density === "compact";

themeButton.addEventListener("click", () => {
    const nuevo = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    aplicarTema(nuevo);
    try {
        localStorage.setItem(CLAVE_TEMA, nuevo);
    } catch (e) {}
});

themeSetting.addEventListener("change", () => {
    aplicarTema(themeSetting.value);
    guardarPreferencia(CLAVE_TEMA, themeSetting.value);
});

densitySetting.addEventListener("change", () => {
    document.documentElement.dataset.density = densitySetting.checked ? "compact" : "comfortable";
    guardarPreferencia(CLAVE_LISTA_COMPACTA, String(densitySetting.checked));
});

function leerPreferencia(clave) {
    try {
        return localStorage.getItem(clave);
    } catch (e) {
        return null;
    }
}

function guardarPreferencia(clave, valor) {
    try {
        localStorage.setItem(clave, valor);
    } catch (e) {}
}

// ---------- Confirmar eliminación ----------
document.querySelectorAll(".delete-form").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
        if (!window.confirm(formulario.dataset.confirm)) {
            evento.preventDefault();
        }
    });
});
