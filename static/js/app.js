// ---------- Modo oscuro / claro ----------
// El diseño nace oscuro (estética Y2K). El modo claro se guarda en localStorage.
const CLAVE_TEMA = "tema-lista-tareas";
const CLAVE_PALETA = "paleta-lista-tareas";
const CLAVE_DISPOSICION = "disposicion-lista-tareas";
const CLAVE_LISTA_COMPACTA = "lista-tareas-compacta";
const CLAVE_TAMANO_TEXTO = "tamano-texto-lista-tareas";
const CLAVE_CONTRASTE = "contraste-lista-tareas";
const CLAVE_ANIMACIONES = "animaciones-lista-tareas";
const themeButton = document.querySelector("#theme-toggle");
const themeLabel = document.querySelector("#theme-label");
const themeSetting = document.querySelector("#theme-setting");
const layoutSetting = document.querySelector("#layout-setting");
const paletteSetting = document.querySelector("#palette-setting");
const textSizeSetting = document.querySelector("#text-size-setting");
const densitySetting = document.querySelector("#density-setting");
const contrastSetting = document.querySelector("#contrast-setting");
const motionSetting = document.querySelector("#motion-setting");

const PALETAS_VALIDAS = ["violet", "ocean", "sunset", "mint", "citrus", "berry"];
const TAMANOS_VALIDOS = ["normal", "large", "x-large"];
const DISPOSICIONES_VALIDAS = ["compact", "extended"];

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
const disposicionGuardada = leerPreferencia(CLAVE_DISPOSICION);
const disposicionInicial = DISPOSICIONES_VALIDAS.includes(disposicionGuardada)
    ? disposicionGuardada
    : "extended";
document.documentElement.dataset.layout = disposicionInicial;
layoutSetting.value = disposicionInicial;
const paletaGuardada = leerPreferencia(CLAVE_PALETA);
const paletaInicial = PALETAS_VALIDAS.includes(paletaGuardada) ? paletaGuardada : "violet";
document.documentElement.dataset.palette = paletaInicial;
paletteSetting.value = paletaInicial;

const tamanoGuardado = leerPreferencia(CLAVE_TAMANO_TEXTO);
const tamanoInicial = TAMANOS_VALIDOS.includes(tamanoGuardado) ? tamanoGuardado : "normal";
document.documentElement.dataset.textSize = tamanoInicial;
textSizeSetting.value = tamanoInicial;

document.documentElement.dataset.density =
    leerPreferencia(CLAVE_LISTA_COMPACTA) === "true" ? "compact" : "comfortable";
densitySetting.checked = document.documentElement.dataset.density === "compact";
document.documentElement.dataset.contrast =
    leerPreferencia(CLAVE_CONTRASTE) === "true" ? "high" : "normal";
contrastSetting.checked = document.documentElement.dataset.contrast === "high";
document.documentElement.dataset.motion =
    leerPreferencia(CLAVE_ANIMACIONES) === "false" ? "off" : "on";
motionSetting.checked = document.documentElement.dataset.motion !== "off";

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

layoutSetting.addEventListener("change", () => {
    const disposicion = DISPOSICIONES_VALIDAS.includes(layoutSetting.value)
        ? layoutSetting.value
        : "extended";
    document.documentElement.dataset.layout = disposicion;
    guardarPreferencia(CLAVE_DISPOSICION, disposicion);
});

paletteSetting.addEventListener("change", () => {
    const paleta = PALETAS_VALIDAS.includes(paletteSetting.value) ? paletteSetting.value : "violet";
    document.documentElement.dataset.palette = paleta;
    guardarPreferencia(CLAVE_PALETA, paleta);
});

textSizeSetting.addEventListener("change", () => {
    const tamano = TAMANOS_VALIDOS.includes(textSizeSetting.value) ? textSizeSetting.value : "normal";
    document.documentElement.dataset.textSize = tamano;
    guardarPreferencia(CLAVE_TAMANO_TEXTO, tamano);
});

densitySetting.addEventListener("change", () => {
    document.documentElement.dataset.density = densitySetting.checked ? "compact" : "comfortable";
    guardarPreferencia(CLAVE_LISTA_COMPACTA, String(densitySetting.checked));
});

contrastSetting.addEventListener("change", () => {
    document.documentElement.dataset.contrast = contrastSetting.checked ? "high" : "normal";
    guardarPreferencia(CLAVE_CONTRASTE, String(contrastSetting.checked));
});

motionSetting.addEventListener("change", () => {
    document.documentElement.dataset.motion = motionSetting.checked ? "on" : "off";
    guardarPreferencia(CLAVE_ANIMACIONES, String(motionSetting.checked));
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
