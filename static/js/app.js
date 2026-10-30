// ---------- Modo oscuro / claro ----------
// El diseño nace oscuro (estética Y2K). El modo claro se guarda en localStorage.
const CLAVE_TEMA = "tema-lista-tareas";
const CLAVE_PALETA = "paleta-lista-tareas";
const CLAVE_IDIOMA = "idioma-lista-tareas";
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
const languageSetting = document.querySelector("#language-setting");
const textSizeSetting = document.querySelector("#text-size-setting");
const densitySetting = document.querySelector("#density-setting");
const contrastSetting = document.querySelector("#contrast-setting");
const motionSetting = document.querySelector("#motion-setting");

const PALETAS_VALIDAS = ["violet", "ocean", "sunset", "mint", "citrus", "berry", "coral", "forest", "sapphire", "rose"];
const TEMAS_VALIDOS = ["dark", "light", "amoled"];
const IDIOMAS_VALIDOS = ["es", "en", "pt", "zh", "ja", "ko"];
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
    if (!TEMAS_VALIDOS.includes(tema)) tema = "dark";
    document.documentElement.dataset.theme = tema;
    document.querySelector("meta[name='theme-color']").content = tema === "amoled"
        ? "#000000"
        : tema === "light" ? "#eceaff" : "#0b0a1a";
    const idioma = document.documentElement.lang;
    const etiquetas = {
        es: { dark: ["Modo claro", "Activar modo claro"], light: ["Modo AMOLED", "Activar modo AMOLED"], amoled: ["Modo oscuro", "Activar modo oscuro"] },
        en: { dark: ["Light mode", "Switch to light mode"], light: ["AMOLED mode", "Switch to AMOLED mode"], amoled: ["Dark mode", "Switch to dark mode"] },
        pt: { dark: ["Modo claro", "Ativar modo claro"], light: ["Modo AMOLED", "Ativar modo AMOLED"], amoled: ["Modo escuro", "Ativar modo escuro"] },
        zh: { dark: ["浅色模式", "切换到浅色模式"], light: ["AMOLED 模式", "切换到 AMOLED 模式"], amoled: ["深色模式", "切换到深色模式"] },
        ja: { dark: ["ライトモード", "ライトモードに切り替え"], light: ["AMOLED モード", "AMOLED モードに切り替え"], amoled: ["ダークモード", "ダークモードに切り替え"] },
        ko: { dark: ["라이트 모드", "라이트 모드로 전환"], light: ["AMOLED 모드", "AMOLED 모드로 전환"], amoled: ["다크 모드", "다크 모드로 전환"] }
    };
    themeLabel.textContent = etiquetas[idioma][tema][0];
    themeButton.setAttribute("aria-label", etiquetas[idioma][tema][1]);
    themeSetting.value = tema;
}

aplicarTema(leerTemaGuardado());
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
    const actual = document.documentElement.dataset.theme;
    const nuevo = actual === "dark" ? "light" : actual === "light" ? "amoled" : "dark";
    aplicarTema(nuevo);
    try {
        localStorage.setItem(CLAVE_TEMA, nuevo);
    } catch (e) {}
});

themeSetting.addEventListener("change", () => {
    aplicarTema(themeSetting.value);
    guardarPreferencia(CLAVE_TEMA, themeSetting.value);
});

languageSetting.addEventListener("change", () => {
    aplicarIdioma(languageSetting.value);
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

const TRADUCCIONES = {
    en: {
        "Espacio": "Workspace", "Secciones principales": "Main sections", "Resumen": "Overview", "Tareas": "Tasks", "Configuración": "Settings", "Ajustes": "Settings",
        "Un poco más de enfoque.": "A little more focus.", "Una tarea a la vez. Haz espacio para lo importante.": "One task at a time. Make room for what matters.", "Todo listo para avanzar": "Ready to move forward",
        "Una mente clara. Un día enfocado.": "A clear mind. A focused day.", "Tu progreso y lo que necesita atención.": "Your progress and what needs attention.", "Tu espacio, a tu manera.": "Your space, your way.", "Organiza lo que importa y avanza a tu ritmo.": "Organize what matters and move at your own pace.",
        "Modo claro": "Light mode", "Modo oscuro": "Dark mode", "Modo AMOLED": "AMOLED mode", "Activar modo claro": "Switch to light mode", "Activar modo oscuro": "Switch to dark mode", "Activar modo AMOLED": "Switch to AMOLED mode",
        "Agregar una tarea": "Add a task", "Tarea": "Task", "¿Qué necesitas hacer?": "What do you need to do?", "Descripción": "Description", "(opcional)": "(optional)", "Añade algunos detalles": "Add a few details", "Categoría": "Category", "Fecha límite": "Due date", "Etiquetas": "Tags", "#urgente, equipo": "#urgent, team", "Hasta 5, separadas por espacios o comas.": "Up to 5, separated by spaces or commas.", "Agregar tarea": "Add task",
        "Tu lista": "Your list", "tarea": "task", "encontrada": "found", "Estado": "Status", "Todos": "All", "Pendientes": "Pending", "Terminadas": "Completed", "Todas": "All", "Etiqueta": "Tag", "Ordenar": "Sort by", "Más recientes": "Newest", "Más antiguas": "Oldest", "Por título": "By title", "Aplicar": "Apply", "pendiente": "pending", "terminada": "completed", "Vence": "Due", "Eliminar": "Delete", "Eliminar tarea": "Delete task", "¿Eliminar esta tarea?": "Delete this task?", "No hay tareas con estos filtros.": "No tasks match these filters.", "Limpiar filtros": "Clear filters",
        "Tu progreso de hoy": "Your progress today", "Una mirada clara a tus avances y próximas fechas límite.": "A clear look at your progress and upcoming due dates.", "Total de tareas": "Total tasks", "Por hacer": "To do", "Completadas": "Completed", "Próximas · 7 días": "Upcoming · 7 days", "Vencidas": "Overdue", "Progreso completado": "Completion progress", "de": "of", "tareas completadas": "tasks completed", "Progreso de tareas completadas": "Completed task progress", "Estado de tus tareas": "Your task status", "pendiente": "pending", "pendientes": "pending", "completadas": "completed", "Agrega tu primera tarea para ver las estadísticas.": "Add your first task to see statistics.", "Tareas por categoría": "Tasks by category", "Fechas límite": "Due dates", "Tareas atrasadas y pendientes para los próximos siete días.": "Overdue and upcoming tasks for the next seven days.", "Ver tareas": "View tasks", "Próximos siete días": "Next seven days", "No tienes tareas pendientes con fecha límite próxima.": "You have no pending tasks due soon.",
        "Ajustes de la web": "Website settings", "Personaliza la apariencia. Tus preferencias se guardan en este navegador.": "Customize the appearance. Your preferences are saved in this browser.", "Diseño de interfaz": "Interface layout", "Alterna entre la interfaz anterior y la nueva barra lateral.": "Switch between the previous interface and the new sidebar.", "Anterior · navegación superior": "Classic · top navigation", "Nueva · barra lateral": "New · sidebar", "Apariencia": "Appearance", "Elige el tema claro u oscuro.": "Choose light, dark, or AMOLED theme.", "Tema de la web": "Website theme", "Oscuro": "Dark", "Claro": "Light", "AMOLED (negro puro)": "AMOLED (pure black)", "Personalización de color": "Color customization", "Elige el ambiente cromático de la web y del logo.": "Choose the color palette for the website and logo.", "Paleta de color": "Color palette", "Holográfica": "Holographic", "Océano": "Ocean", "Atardecer": "Sunset", "Menta": "Mint", "Cítrico": "Citrus", "Frambuesa": "Berry", "Coral": "Coral", "Bosque": "Forest", "Zafiro": "Sapphire", "Rosa": "Rose", "Idioma": "Language", "Elige el idioma de la interfaz.": "Choose the interface language.", "Idioma de la interfaz": "Interface language", "Tamaño del texto": "Text size", "Haz la lectura más cómoda.": "Make reading more comfortable.", "Normal": "Normal", "Grande": "Large", "Muy grande": "Extra large", "Lista compacta": "Compact list", "Reduce el espacio entre las tareas.": "Reduce the spacing between tasks.", "Contraste reforzado": "High contrast", "Aumenta la diferencia entre texto y fondo.": "Increase the contrast between text and background.", "Animaciones": "Animations", "Activa las transiciones y efectos visuales.": "Enable transitions and visual effects."
    },
    pt: {
        "Agrega tu primera tarea para ver las estadísticas.": "Adicione sua primeira tarefa para ver as estatísticas.",
        "Tareas atrasadas y pendientes para los próximos siete días.": "Tarefas atrasadas e pendentes para os próximos sete dias.",
        "Espacio": "Espaço", "Secciones principales": "Seções principais", "Resumen": "Resumo", "Tareas": "Tarefas", "Configuración": "Configurações", "Ajustes": "Ajustes",
        "Un poco más de enfoque.": "Um pouco mais de foco.", "Una tarea a la vez. Haz espacio para lo importante.": "Uma tarefa de cada vez. Abra espaço para o que importa.", "Todo listo para avanzar": "Tudo pronto para avançar",
        "Una mente clara. Un día enfocado.": "Uma mente clara. Um dia focado.", "Tu progreso y lo que necesita atención.": "Seu progresso e o que precisa de atenção.", "Tu espacio, a tu manera.": "Seu espaço, do seu jeito.", "Organiza lo que importa y avanza a tu ritmo.": "Organize o que importa e avance no seu ritmo.",
        "Modo claro": "Modo claro", "Modo oscuro": "Modo escuro", "Modo AMOLED": "Modo AMOLED", "Activar modo claro": "Ativar modo claro", "Activar modo oscuro": "Ativar modo escuro", "Activar modo AMOLED": "Ativar modo AMOLED",
        "Agregar una tarea": "Adicionar uma tarefa", "Tarea": "Tarefa", "¿Qué necesitas hacer?": "O que você precisa fazer?", "Descripción": "Descrição", "(opcional)": "(opcional)", "Añade algunos detalles": "Adicione alguns detalhes", "Categoría": "Categoria", "Fecha límite": "Prazo", "Etiquetas": "Etiquetas", "#urgente, equipo": "#urgente, equipe", "Hasta 5, separadas por espacios o comas.": "Até 5, separadas por espaços ou vírgulas.", "Agregar tarea": "Adicionar tarefa",
        "Tu lista": "Sua lista", "tarea": "tarefa", "encontrada": "encontrada", "Estado": "Status", "Todos": "Todos", "Pendientes": "Pendentes", "Terminadas": "Concluídas", "Todas": "Todas", "Etiqueta": "Etiqueta", "Ordenar": "Ordenar", "Más recientes": "Mais recentes", "Más antiguas": "Mais antigas", "Por título": "Por título", "Aplicar": "Aplicar", "pendiente": "pendente", "terminada": "concluída", "Vence": "Vence", "Eliminar": "Excluir", "Eliminar tarea": "Excluir tarefa", "¿Eliminar esta tarea?": "Excluir esta tarefa?", "No hay tareas con estos filtros.": "Não há tarefas com estes filtros.", "Limpiar filtros": "Limpar filtros",
        "Tu progreso de hoy": "Seu progresso de hoje", "Una mirada clara a tus avances y próximas fechas límite.": "Uma visão clara do seu progresso e dos próximos prazos.", "Total de tareas": "Total de tarefas", "Por hacer": "A fazer", "Completadas": "Concluídas", "Próximas · 7 días": "Próximos · 7 dias", "Vencidas": "Atrasadas", "Progreso completado": "Progresso concluído", "de": "de", "tareas completadas": "tarefas concluídas", "Progreso de tareas completadas": "Progresso de tarefas concluídas", "Estado de tus tareas": "Status das suas tarefas", "pendientes": "pendentes", "completadas": "concluídas", "Agrega tu primera tarea para ver las estatísticas.": "Adicione sua primeira tarefa para ver as estatísticas.", "Tareas por categoría": "Tarefas por categoria", "Fechas límite": "Prazos", "Tareas atrasadas y pendientes para los próximos sete días.": "Tarefas atrasadas e pendentes para os próximos sete dias.", "Ver tareas": "Ver tarefas", "Próximos siete días": "Próximos sete dias", "No tienes tareas pendientes con fecha límite próxima.": "Você não tem tarefas pendentes com prazo próximo.",
        "Ajustes de la web": "Configurações do site", "Personaliza la apariencia. Tus preferencias se guardan en este navegador.": "Personalize a aparência. Suas preferências são salvas neste navegador.", "Diseño de interfaz": "Layout da interface", "Alterna entre la interfaz anterior y la nueva barra lateral.": "Alterne entre a interface anterior e a nova barra lateral.", "Anterior · navegación superior": "Clássica · navegação superior", "Nueva · barra lateral": "Nova · barra lateral", "Apariencia": "Aparência", "Elige el tema claro u oscuro.": "Escolha o tema claro, escuro ou AMOLED.", "Tema de la web": "Tema do site", "Oscuro": "Escuro", "Claro": "Claro", "AMOLED (negro puro)": "AMOLED (preto puro)", "Personalización de color": "Personalização de cores", "Elige el ambiente cromático de la web y del logo.": "Escolha a paleta de cores do site e do logotipo.", "Paleta de color": "Paleta de cores", "Holográfica": "Holográfica", "Océano": "Oceano", "Atardecer": "Pôr do sol", "Menta": "Menta", "Cítrico": "Cítrico", "Frambuesa": "Framboesa", "Coral": "Coral", "Bosque": "Floresta", "Zafiro": "Safira", "Rosa": "Rosa", "Idioma": "Idioma", "Elige el idioma de la interfaz.": "Escolha o idioma da interface.", "Idioma de la interfaz": "Idioma da interface", "Tamaño del texto": "Tamanho do texto", "Haz la lectura más cómoda.": "Deixe a leitura mais confortável.", "Normal": "Normal", "Grande": "Grande", "Muy grande": "Extra grande", "Lista compacta": "Lista compacta", "Reduce el espacio entre las tareas.": "Reduza o espaço entre as tarefas.", "Contraste reforzado": "Alto contraste", "Aumenta la diferencia entre texto y fondo.": "Aumente o contraste entre o texto e o fundo.", "Animaciones": "Animações", "Activa las transiciones y efectos visuales.": "Ative as transições e os efeitos visuais."
    }
};

TRADUCCIONES.zh = {
    "Espacio": "工作区", "Secciones principales": "主导航", "Resumen": "概览", "Tareas": "任务", "Configuración": "设置", "Ajustes": "设置",
    "Un poco más de enfoque.": "专注多一点。", "Una tarea a la vez. Haz espacio para lo importante.": "一次专注一项任务，为重要的事留出空间。", "Todo listo para avanzar": "一切就绪，开始前进",
    "Una mente clara. Un día enfocado.": "思路清晰，专注每一天。", "Tu progreso y lo que necesita atención.": "查看进度和需要关注的事项。", "Tu espacio, a tu manera.": "按你的方式布置空间。", "Organiza lo que importa y avanza a tu ritmo.": "整理重要事项，按自己的节奏前进。",
    "Modo claro": "浅色模式", "Modo oscuro": "深色模式", "Modo AMOLED": "AMOLED 模式", "Activar modo claro": "切换到浅色模式", "Activar modo oscuro": "切换到深色模式", "Activar modo AMOLED": "切换到 AMOLED 模式",
    "Agregar una tarea": "添加任务", "Tarea": "任务", "¿Qué necesitas hacer?": "你需要做什么？", "Descripción": "描述", "(opcional)": "（可选）", "Añade algunos detalles": "添加一些详情", "Categoría": "类别", "Fecha límite": "截止日期", "Etiquetas": "标签", "#urgente, equipo": "#紧急, 团队", "Hasta 5, separadas por espacios o comas.": "最多 5 个，用空格或逗号分隔。", "Agregar tarea": "添加任务",
    "Tu lista": "任务列表", "encontrada": "已找到", "Estado": "状态", "Todos": "全部", "Pendientes": "待办", "Terminadas": "已完成", "Todas": "全部", "Etiqueta": "标签", "Ordenar": "排序", "Más recientes": "最新优先", "Más antiguas": "最早优先", "Por título": "按标题", "Aplicar": "应用", "pendiente": "待办", "terminada": "已完成", "Vence": "截止", "Eliminar": "删除", "Eliminar tarea": "删除任务", "¿Eliminar esta tarea?": "确定删除此任务吗？", "No hay tareas con estos filtros.": "没有符合这些筛选条件的任务。", "Limpiar filtros": "清除筛选",
    "Tu progreso de hoy": "今日进度", "Una mirada clara a tus avances y próximas fechas límite.": "清晰查看进度和即将到来的截止日期。", "Total de tareas": "任务总数", "Por hacer": "待处理", "Completadas": "已完成", "Próximas · 7 días": "未来 7 天", "Vencidas": "已逾期", "Progreso completado": "完成进度", "de": "/", "tareas completadas": "项任务已完成", "Progreso de tareas completadas": "任务完成进度", "Estado de tus tareas": "任务状态", "pendientes": "待办", "completadas": "已完成", "Agrega tu primera tarea para ver las estadísticas.": "添加第一个任务以查看统计信息。", "Tareas por categoría": "按类别统计任务", "Fechas límite": "截止日期", "Tareas atrasadas y pendientes para los próximos siete días.": "逾期任务和未来七天内到期的任务。", "Ver tareas": "查看任务", "Próximos siete días": "未来七天", "No tienes tareas pendientes con fecha límite próxima.": "近期没有待办的截止任务。",
    "Ajustes de la web": "网站设置", "Personaliza la apariencia. Tus preferencias se guardan en este navegador.": "自定义外观。偏好设置保存在此浏览器中。", "Diseño de interfaz": "界面布局", "Alterna entre la interfaz anterior y la nueva barra lateral.": "在旧版界面和新版侧边栏之间切换。", "Anterior · navegación superior": "经典版 · 顶部导航", "Nueva · barra lateral": "新版 · 侧边栏", "Apariencia": "外观", "Elige el tema claro u oscuro.": "选择浅色、深色或 AMOLED 主题。", "Tema de la web": "网站主题", "Oscuro": "深色", "Claro": "浅色", "AMOLED (negro puro)": "AMOLED（纯黑）", "Personalización de color": "颜色自定义", "Elige el ambiente cromático de la web y del logo.": "选择网站和标志的配色。", "Paleta de color": "配色方案", "Holográfica": "全息", "Océano": "海洋", "Atardecer": "日落", "Menta": "薄荷", "Cítrico": "柑橘", "Frambuesa": "树莓", "Coral": "珊瑚", "Bosque": "森林", "Zafiro": "蓝宝石", "Rosa": "玫瑰", "Idioma": "语言", "Elige el idioma de la interfaz.": "选择界面语言。", "Idioma de la interfaz": "界面语言", "Tamaño del texto": "文字大小", "Haz la lectura más cómoda.": "调整文字大小，让阅读更舒适。", "Normal": "标准", "Grande": "大", "Muy grande": "特大", "Lista compacta": "紧凑列表", "Reduce el espacio entre las tareas.": "缩小任务之间的间距。", "Contraste reforzado": "高对比度", "Aumenta la diferencia entre texto y fondo.": "提高文字与背景之间的对比度。", "Animaciones": "动画", "Activa las transiciones y efectos visuales.": "启用过渡效果和视觉动画。"
};

TRADUCCIONES.ja = {
    "Espacio": "ワークスペース", "Secciones principales": "メインメニュー", "Resumen": "概要", "Tareas": "タスク", "Configuración": "設定", "Ajustes": "設定",
    "Un poco más de enfoque.": "もう少し集中。", "Una tarea a la vez. Haz espacio para lo importante.": "一度に一つのタスクに集中し、大切なことのための余白を作りましょう。", "Todo listo para avanzar": "準備完了。進みましょう",
    "Una mente clara. Un día enfocado.": "頭をすっきり、集中できる一日。", "Tu progreso y lo que necesita atención.": "進捗と対応が必要な項目を確認できます。", "Tu espacio, a tu manera.": "自分らしいワークスペースに。", "Organiza lo que importa y avanza a tu ritmo.": "大切なことを整理して、自分のペースで進みましょう。",
    "Modo claro": "ライトモード", "Modo oscuro": "ダークモード", "Modo AMOLED": "AMOLED モード", "Activar modo claro": "ライトモードに切り替え", "Activar modo oscuro": "ダークモードに切り替え", "Activar modo AMOLED": "AMOLED モードに切り替え",
    "Agregar una tarea": "タスクを追加", "Tarea": "タスク", "¿Qué necesitas hacer?": "何をしますか？", "Descripción": "説明", "(opcional)": "（任意）", "Añade algunos detalles": "詳細を追加", "Categoría": "カテゴリ", "Fecha límite": "期限", "Etiquetas": "タグ", "#urgente, equipo": "#緊急, チーム", "Hasta 5, separadas por espacios o comas.": "最大 5 個。スペースまたはカンマで区切ってください。", "Agregar tarea": "タスクを追加",
    "Tu lista": "タスクリスト", "encontrada": "件見つかりました", "Estado": "状態", "Todos": "すべて", "Pendientes": "未完了", "Terminadas": "完了", "Todas": "すべて", "Etiqueta": "タグ", "Ordenar": "並べ替え", "Más recientes": "新しい順", "Más antiguas": "古い順", "Por título": "タイトル順", "Aplicar": "適用", "pendiente": "未完了", "terminada": "完了", "Vence": "期限", "Eliminar": "削除", "Eliminar tarea": "タスクを削除", "¿Eliminar esta tarea?": "このタスクを削除しますか？", "No hay tareas con estos filtros.": "条件に一致するタスクはありません。", "Limpiar filtros": "フィルターをクリア",
    "Tu progreso de hoy": "今日の進捗", "Una mirada clara a tus avances y próximas fechas límite.": "進捗と今後の期限を確認できます。", "Total de tareas": "タスク合計", "Por hacer": "未対応", "Completadas": "完了", "Próximas · 7 días": "今後 7 日間", "Vencidas": "期限切れ", "Progreso completado": "完了状況", "de": "/", "tareas completadas": "件完了", "Progreso de tareas completadas": "タスク完了状況", "Estado de tus tareas": "タスクの状態", "pendientes": "未完了", "completadas": "完了", "Agrega tu primera tarea para ver las estadísticas.": "最初のタスクを追加して統計を表示しましょう。", "Tareas por categoría": "カテゴリ別タスク", "Fechas límite": "期限", "Tareas atrasadas y pendientes para los próximos siete días.": "期限超過のタスクと今後 7 日以内のタスクです。", "Ver tareas": "タスクを見る", "Próximos siete días": "今後 7 日間", "No tienes tareas pendientes con fecha límite próxima.": "期限が近い未完了タスクはありません。",
    "Ajustes de la web": "ウェブ設定", "Personaliza la apariencia. Tus preferencias se guardan en este navegador.": "外観をカスタマイズできます。設定はこのブラウザーに保存されます。", "Diseño de interfaz": "画面レイアウト", "Alterna entre la interfaz anterior y la nueva barra lateral.": "旧画面と新しいサイドバーを切り替えます。", "Anterior · navegación superior": "従来版 · 上部ナビゲーション", "Nueva · barra lateral": "新しい版 · サイドバー", "Apariencia": "外観", "Elige el tema claro u oscuro.": "ライト、ダーク、AMOLED から選択します。", "Tema de la web": "ウェブのテーマ", "Oscuro": "ダーク", "Claro": "ライト", "AMOLED (negro puro)": "AMOLED（完全な黒）", "Personalización de color": "カラー設定", "Elige el ambiente cromático de la web y del logo.": "ウェブとロゴの配色を選択します。", "Paleta de color": "カラーパレット", "Holográfica": "ホログラフィック", "Océano": "オーシャン", "Atardecer": "サンセット", "Menta": "ミント", "Cítrico": "シトラス", "Frambuesa": "ラズベリー", "Coral": "コーラル", "Bosque": "フォレスト", "Zafiro": "サファイア", "Rosa": "ローズ", "Idioma": "言語", "Elige el idioma de la interfaz.": "画面の言語を選択します。", "Idioma de la interfaz": "画面の言語", "Tamaño del texto": "文字サイズ", "Haz la lectura más cómoda.": "読みやすい文字サイズに調整します。", "Normal": "標準", "Grande": "大", "Muy grande": "特大", "Lista compacta": "コンパクトなリスト", "Reduce el espacio entre las tareas.": "タスク間の余白を小さくします。", "Contraste reforzado": "高コントラスト", "Aumenta la diferencia entre texto y fondo.": "文字と背景のコントラストを高めます。", "Animaciones": "アニメーション", "Activa las transiciones y efectos visuales.": "切り替えや視覚効果を有効にします。"
};

TRADUCCIONES.ko = {
    "Espacio": "작업 공간", "Secciones principales": "주요 메뉴", "Resumen": "요약", "Tareas": "작업", "Configuración": "설정", "Ajustes": "설정",
    "Un poco más de enfoque.": "조금 더 집중해 보세요.", "Una tarea a la vez. Haz espacio para lo importante.": "한 번에 하나씩 처리하고 중요한 일을 위한 여유를 만드세요.", "Todo listo para avanzar": "시작할 준비가 되었습니다",
    "Una mente clara. Un día enfocado.": "맑은 생각, 집중하는 하루.", "Tu progreso y lo que necesita atención.": "진행 상황과 확인이 필요한 항목을 살펴보세요.", "Tu espacio, a tu manera.": "나만의 방식으로 공간을 꾸며보세요.", "Organiza lo que importa y avanza a tu ritmo.": "중요한 일을 정리하고 나만의 속도로 진행하세요.",
    "Modo claro": "라이트 모드", "Modo oscuro": "다크 모드", "Modo AMOLED": "AMOLED 모드", "Activar modo claro": "라이트 모드로 전환", "Activar modo oscuro": "다크 모드로 전환", "Activar modo AMOLED": "AMOLED 모드로 전환",
    "Agregar una tarea": "작업 추가", "Tarea": "작업", "¿Qué necesitas hacer?": "무엇을 해야 하나요?", "Descripción": "설명", "(opcional)": "(선택 사항)", "Añade algunos detalles": "세부 정보 추가", "Categoría": "범주", "Fecha límite": "마감일", "Etiquetas": "태그", "#urgente, equipo": "#긴급, 팀", "Hasta 5, separadas por espacios o comas.": "최대 5개까지 입력하고 공백이나 쉼표로 구분하세요.", "Agregar tarea": "작업 추가",
    "Tu lista": "작업 목록", "encontrada": "개 찾음", "Estado": "상태", "Todos": "전체", "Pendientes": "대기 중", "Terminadas": "완료됨", "Todas": "전체", "Etiqueta": "태그", "Ordenar": "정렬", "Más recientes": "최신순", "Más antiguas": "오래된순", "Por título": "제목순", "Aplicar": "적용", "pendiente": "대기 중", "terminada": "완료됨", "Vence": "마감", "Eliminar": "삭제", "Eliminar tarea": "작업 삭제", "¿Eliminar esta tarea?": "이 작업을 삭제할까요?", "No hay tareas con estos filtros.": "이 필터에 해당하는 작업이 없습니다.", "Limpiar filtros": "필터 지우기",
    "Tu progreso de hoy": "오늘의 진행 상황", "Una mirada clara a tus avances y próximas fechas límite.": "진행 상황과 다가오는 마감일을 한눈에 확인하세요.", "Total de tareas": "전체 작업", "Por hacer": "할 일", "Completadas": "완료됨", "Próximas · 7 días": "향후 7일", "Vencidas": "기한 초과", "Progreso completado": "완료 진행률", "de": "/", "tareas completadas": "개 작업 완료", "Progreso de tareas completadas": "작업 완료 진행률", "Estado de tus tareas": "작업 상태", "pendientes": "대기 중", "completadas": "완료됨", "Agrega tu primera tarea para ver las estadísticas.": "첫 작업을 추가해 통계를 확인하세요.", "Tareas por categoría": "범주별 작업", "Fechas límite": "마감일", "Tareas atrasadas y pendientes para los próximos siete días.": "기한이 지난 작업과 향후 7일 이내의 작업입니다.", "Ver tareas": "작업 보기", "Próximos siete días": "향후 7일", "No tienes tareas pendientes con fecha límite próxima.": "마감일이 임박한 대기 중 작업이 없습니다.",
    "Ajustes de la web": "웹 설정", "Personaliza la apariencia. Tus preferencias se guardan en este navegador.": "화면 모양을 사용자 지정하세요. 설정은 이 브라우저에 저장됩니다.", "Diseño de interfaz": "화면 레이아웃", "Alterna entre la interfaz anterior y la nueva barra lateral.": "이전 화면과 새 사이드바 화면을 전환합니다.", "Anterior · navegación superior": "기존 · 상단 탐색", "Nueva · barra lateral": "새 화면 · 사이드바", "Apariencia": "화면 모양", "Elige el tema claro u oscuro.": "라이트, 다크 또는 AMOLED 테마를 선택하세요.", "Tema de la web": "웹 테마", "Oscuro": "다크", "Claro": "라이트", "AMOLED (negro puro)": "AMOLED (순수 검정)", "Personalización de color": "색상 사용자 지정", "Elige el ambiente cromático de la web y del logo.": "웹과 로고에 사용할 색상 팔레트를 선택하세요.", "Paleta de color": "색상 팔레트", "Holográfica": "홀로그래픽", "Océano": "오션", "Atardecer": "선셋", "Menta": "민트", "Cítrico": "시트러스", "Frambuesa": "베리", "Coral": "코랄", "Bosque": "포레스트", "Zafiro": "사파이어", "Rosa": "로즈", "Idioma": "언어", "Elige el idioma de la interfaz.": "화면 언어를 선택하세요.", "Idioma de la interfaz": "화면 언어", "Tamaño del texto": "글자 크기", "Haz la lectura más cómoda.": "읽기 편하도록 글자 크기를 조정하세요.", "Normal": "보통", "Grande": "크게", "Muy grande": "매우 크게", "Lista compacta": "간격 좁은 목록", "Reduce el espacio entre las tareas.": "작업 사이의 간격을 줄입니다.", "Contraste reforzado": "고대비", "Aumenta la diferencia entre texto y fondo.": "글자와 배경의 대비를 높입니다.", "Animaciones": "애니메이션", "Activa las transiciones y efectos visuales.": "전환 효과와 시각 효과를 사용합니다."
};

const textosOriginales = new WeakMap();
const atributosOriginales = new WeakMap();

function aplicarIdioma(idioma) {
    if (!IDIOMAS_VALIDOS.includes(idioma)) idioma = "es";
    document.documentElement.lang = idioma;
    languageSetting.value = idioma;
    guardarPreferencia(CLAVE_IDIOMA, idioma);
    const traducciones = TRADUCCIONES[idioma] || {};
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let nodo;
    while ((nodo = walker.nextNode())) {
        if (nodo.parentElement.closest(".task-content, .category-badge, .tag-badge, .upcoming-task, .category-stats, .notice, .sidebar-brand-name")) continue;
        if (!textosOriginales.has(nodo)) textosOriginales.set(nodo, nodo.nodeValue);
        const original = textosOriginales.get(nodo);
        const texto = original.trim();
        if (!texto) continue;
        const traducido = traducciones[texto];
        if (traducido) nodo.nodeValue = original.replace(texto, traducido);
        else if (idioma !== "es" && /^(\d+)\s+(pendientes|completadas)$/.test(texto)) {
            const [, cantidad, estado] = texto.match(/^(\d+)\s+(pendientes|completadas)$/);
            const etiqueta = idioma === "en"
                ? estado === "pendientes" ? "pending" : "completed"
                : traducciones[estado] || (estado === "pendientes" ? "pendentes" : "concluídas");
            nodo.nodeValue = original.replace(texto, `${cantidad} ${etiqueta}`);
        }
        else if (idioma !== "es" && /^(\d+)\s+tareas?\s+encontradas?$/.test(texto)) {
            const [, cantidad] = texto.match(/^(\d+)\s+tareas?\s+encontradas?$/);
            const resultado = idioma === "en"
                ? `${cantidad} task${cantidad === "1" ? "" : "s"} found`
                : idioma === "pt"
                    ? `${cantidad} tarefa${cantidad === "1" ? "" : "s"} encontrada${cantidad === "1" ? "" : "s"}`
                    : idioma === "zh" ? `${cantidad} 项任务` : idioma === "ja" ? `${cantidad} 件のタスクが見つかりました` : `${cantidad}개의 작업을 찾았습니다`;
            nodo.nodeValue = original.replace(texto, resultado);
        }
        else if (idioma !== "es" && /^(\d+)\s+de\s+(\d+)\s+tareas completadas$/.test(texto)) {
            const [, completadas, total] = texto.match(/^(\d+)\s+de\s+(\d+)\s+tareas completadas$/);
            const progreso = idioma === "en"
                ? `${completadas} of ${total} tasks completed`
                : idioma === "pt"
                    ? `${completadas} de ${total} tarefas concluídas`
                    : idioma === "zh" ? `已完成 ${completadas} / ${total} 项任务`
                        : idioma === "ja" ? `${completadas} / ${total} 件のタスクが完了`
                            : `${completadas} / ${total}개 작업 완료`;
            nodo.nodeValue = original.replace(texto, progreso);
        }
        else if (idioma === "es") nodo.nodeValue = original;
    }
    document.querySelectorAll("[aria-label], [title], [placeholder], [data-confirm], meta[name='description']").forEach((elemento) => {
        const atributo = elemento.hasAttribute("content") ? "content" : elemento.hasAttribute("placeholder") ? "placeholder" : elemento.hasAttribute("title") ? "title" : "aria-label";
        const atributoTraducible = elemento.hasAttribute("data-confirm") ? "data-confirm" : atributo;
        if (!atributosOriginales.has(elemento)) atributosOriginales.set(elemento, elemento.getAttribute(atributoTraducible));
        const original = atributosOriginales.get(elemento);
        if (original && traducciones[original]) elemento.setAttribute(atributoTraducible, traducciones[original]);
        else if (idioma === "es" && original) elemento.setAttribute(atributoTraducible, original);
    });
    document.querySelectorAll(".toggle-form input[data-task-title]").forEach((checkbox) => {
        const pendiente = checkbox.dataset.completed === "true";
        const titulo = checkbox.dataset.taskTitle;
        checkbox.setAttribute("aria-label", idioma === "en"
            ? `Mark ${titulo} as ${pendiente ? "pending" : "completed"}`
            : idioma === "pt"
                ? `Marcar ${titulo} como ${pendiente ? "pendente" : "concluída"}`
                : idioma === "zh" ? `将“${titulo}”标记为${pendiente ? "待办" : "已完成"}`
                    : idioma === "ja" ? `${titulo}を${pendiente ? "未完了" : "完了"}にする`
                        : idioma === "ko" ? `${titulo} 작업을 ${pendiente ? "대기 중" : "완료됨"}(으)로 표시`
                            : `Marcar ${titulo} como ${pendiente ? "pendiente" : "terminada"}`);
    });
    document.querySelectorAll(".button-delete[data-task-title]").forEach((button) => {
        const titulo = button.dataset.taskTitle;
        button.setAttribute("aria-label", idioma === "en" ? `Delete ${titulo}` : idioma === "pt" ? `Excluir ${titulo}`
            : idioma === "zh" ? `删除${titulo}` : idioma === "ja" ? `${titulo}を削除` : idioma === "ko" ? `${titulo} 삭제` : `Eliminar ${titulo}`);
    });
    document.querySelectorAll(".donut-chart[aria-label]").forEach((chart) => {
        const textoOriginal = atributosOriginales.get(chart);
        const conteos = textoOriginal?.match(/^(\d+) tareas pendientes y (\d+) completadas$/);
        if (!conteos) return;
        chart.setAttribute("aria-label", idioma === "en"
            ? `${conteos[1]} pending tasks and ${conteos[2]} completed`
            : idioma === "pt"
                ? `${conteos[1]} tarefas pendentes e ${conteos[2]} concluídas`
                : idioma === "zh" ? `${conteos[1]} 项待办任务，${conteos[2]} 项已完成任务`
                    : idioma === "ja" ? `${conteos[1]} 件の未完了タスク、${conteos[2]} 件完了`
                        : idioma === "ko" ? `대기 중 작업 ${conteos[1]}개, 완료된 작업 ${conteos[2]}개`
                : textoOriginal);
    });
    document.title = idioma === "en" ? "Estudi Web | Organize your day"
        : idioma === "pt" ? "Estudi Web | Organize seu dia"
            : idioma === "zh" ? "Estudi Web | 整理每一天"
                : idioma === "ja" ? "Estudi Web | 一日を整理"
                    : idioma === "ko" ? "Estudi Web | 하루를 정리하세요" : "Estudi Web | Organiza tu día";
    document.querySelector("meta[name='description']").content = idioma === "en"
        ? "Estudi Web: a simple space to organize your tasks, categories, and tags."
        : idioma === "pt"
            ? "Estudi Web: um espaço simples para organizar suas tarefas, categorias e etiquetas."
            : idioma === "zh" ? "Estudi Web：轻松整理任务、类别和标签的空间。"
                : idioma === "ja" ? "Estudi Web：タスク、カテゴリ、タグを整理するシンプルな場所です。"
                    : idioma === "ko" ? "Estudi Web: 작업, 범주, 태그를 간편하게 정리하는 공간입니다." : "Estudi Web: un espacio sencillo para organizar tus tareas, categorías y etiquetas.";
    aplicarTema(document.documentElement.dataset.theme);
}

aplicarIdioma(leerPreferencia(CLAVE_IDIOMA) || "es");

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
