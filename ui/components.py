"""
ui/components.py
----------------
Componentes reutilizables de la interfaz Streamlit de Justicia IA.
Actualizado para soportar la API de Groq.
"""

from __future__ import annotations

from dataclasses import dataclass

import os
import urllib.parse
import streamlit as st

import config
from core.groq_client import GroqClient
from core.extractor import ExtractionResult
from core.analyzer import AnalysisResult


@dataclass
class SidebarState:
    api_connected: bool
    available_models: list[str]
    selected_model: str
    chunk_size: int
    max_parts: int


def render_sidebar(client: GroqClient) -> SidebarState:
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        st.divider()

        st.markdown("**🔑 Clave API Groq**")
        from core.database import load_api_key, save_api_key
        
        saved_key = load_api_key()
        if "groq_api_key" not in st.session_state and saved_key:
            st.session_state["groq_api_key"] = saved_key
            client.set_api_key(saved_key)

        # Solo mostramos la gestión de API Key si no hay una clave válida guardada
        # o si el usuario quiere cambiarla explícitamente (solo administradores)
        from auth import Role
        # Corregimos la lógica de detección de administrador
        current_role = st.session_state.get("role")
        is_admin = (getattr(current_role, "value", current_role) == Role.SUPERADMIN.value)
        
        # El input de la API Key solo se muestra si:
        # 1. No hay una clave guardada
        # 2. O el usuario es administrador (para que pueda cambiarla)
        if not saved_key or is_admin:
            api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get("groq_api_key", ""),
                placeholder="gsk_...",
                help="Consigue tu API Key gratis en console.groq.com",
                label_visibility="collapsed"
            )
            
            if api_key != st.session_state.get("groq_api_key", ""):
                st.session_state["groq_api_key"] = api_key
                save_api_key(api_key)
                client.set_api_key(api_key)
        else:
            api_key = saved_key

        connected, models = client.check_connection()

        if connected:
            if is_admin:
                st.markdown('<span class="status-ok">🟢 Groq Conectado</span>', unsafe_allow_html=True)
        else:
            if is_admin:
                st.markdown('<span class="status-error">🔴 Sin conexión</span>', unsafe_allow_html=True)
                if not api_key:
                    st.warning("⚠️ Introduce tu clave de API de Groq para continuar.")
                else:
                    st.error("⚠️ Clave de API inválida.")

        st.divider()

        st.markdown("**🤖 Modelo en la nube**")
        selected_model = st.selectbox(
            "Modelo Groq",
            options=models,
            index=0,
            disabled=not connected,
        )

        st.divider()

        with st.expander("🔧 Opciones avanzadas"):
            chunk_size = st.slider(
                "Tamaño de fragmento",
                min_value=500,
                max_value=3000,
                value=config.DEFAULT_CHUNK_SIZE,
                step=100,
            )
            max_parts = st.slider(
                "Fragmentos máximos",
                min_value=1,
                max_value=8,
                value=config.DEFAULT_MAX_PARTS,
            )

        st.divider()
        st.caption(f"Justicia IA — v{config.APP_VERSION}\nPotenciado por Groq")

    return SidebarState(
        api_connected=connected,
        available_models=models,
        selected_model=selected_model if (connected and models) else "llama-3.1-8b-instant",
        chunk_size=chunk_size,
        max_parts=max_parts,
    )


def render_header() -> None:
    st.markdown(f'<p class="main-title">{config.APP_ICON} Justicia IA</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{config.APP_DESCRIPTION}</p>', unsafe_allow_html=True)


def render_upload_section() -> object | None:
    col_upload, col_tip = st.columns([3, 1])
    with col_upload:
        uploaded = st.file_uploader(
            "📂 Sube un documento legal",
            type=config.SUPPORTED_FILE_TYPES,
        )
    with col_tip:
        st.info("💡 **Tip:** Groq es rapidísimo. Usa PDFs seleccionables para la máxima velocidad.")
    return uploaded


def render_metrics(filename: str, result: ExtractionResult) -> None:
    col1, col2, col3 = st.columns(3)
    display_name = filename[:25] + "..." if len(filename) > 25 else filename
    col1.metric("📄 Archivo", display_name)
    col2.metric("🔤 Caracteres", f"{len(result.text):,}")
    if result.num_pages:
        col3.metric("📑 Páginas", result.num_pages)
    else:
        col3.metric("🖼️ Tipo", "Imagen (OCR)")

    for warning in result.warnings:
        st.warning(f"⚠️ {warning}")


def render_extracted_text(filename: str, result: ExtractionResult) -> None:
    with st.expander("📝 Ver texto extraído", expanded=False):
        st.text_area("Contenido del documento", result.text, height=300, label_visibility="collapsed")
        base_name = filename.rsplit(".", 1)[0]
        st.download_button(
            label="⬇️ Descargar texto",
            data=result.text,
            file_name=f"{base_name}_texto.txt",
            mime="text/plain",
        )


def render_results(filename: str, result: AnalysisResult) -> None:
    st.success(
        f"✅ Análisis completado — {result.parts_analyzed} fragmento(s) "
        f"procesado(s) vía Groq ({result.model})"
    )

    st.markdown("### 📋 Informe del Documento")
    st.markdown(f'<div class="card">{result.final_report}</div>', unsafe_allow_html=True)

    if result.errors:
        with st.expander("⚠️ Errores durante el análisis", expanded=False):
            for err in result.errors:
                st.error(err)

    if len(result.partial_summaries) > 1:
        with st.expander("🔎 Ver análisis por fragmento", expanded=False):
            for i, summary in enumerate(result.partial_summaries):
                st.markdown(f"**Fragmento {i + 1}:**")
                st.markdown(summary)
                if i < len(result.partial_summaries) - 1:
                    st.divider()

    base_name = filename.rsplit(".", 1)[0]
    
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d1:
        st.download_button(
            label="📄 Descargar PDF",
            data=result.to_pdf(filename),
            file_name=f"{base_name}_judicial.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_d2:
        st.download_button(
            label="📝 Descargar DOCX",
            data=result.to_docx(filename),
            file_name=f"{base_name}_judicial.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    with col_d3:
        st.download_button(
            label="🗒️ Descargar TXT",
            data=result.to_text(filename),
            file_name=f"{base_name}_judicial.txt",
            mime="text/plain",
            use_container_width=True
        )


def render_visual_guide_cards(view: str = "user") -> None:
    """Muestra tarjetas de ayuda visual e iconos para reforzar el flujo de trabajo."""
    items = [
        {
            "icon": "📂",
            "title": "Carga expedientes",
            "text": "Sube documentos legales y organiza en carpetas con un solo clic.",
        },
        {
            "icon": "⚙️",
            "title": "Configura Groq",
            "text": "Verifica la API, selecciona el mejor modelo y ajusta fragmentos.",
        },
        {
            "icon": "📈",
            "title": "Revisa resultados",
            "text": "Descarga informes y consulta el Workspace para seguimiento.",
        },
    ]
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        col.markdown(
            f"<div class='feature-card'>"
            f"<div class='feature-icon'>{item['icon']}</div>"
            f"<h4>{item['title']}</h4>"
            f"<p>{item['text']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_initial_animation() -> None:
    """Muestra una animación inicial más visible con efecto de luz judicial."""
    st.markdown(
        """
        <div class='hero-animation'>
            <div class='hero-pill hero-pill-1'></div>
            <div class='hero-pill hero-pill-2'></div>
            <div class='hero-pill hero-pill-3'></div>
            <div class='hero-text'>
                <h2>Bienvenido a Justicia IA</h2>
                <p>Organiza expedientes, analiza documentos y genera borradores legales con un flujo guiado.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_dashboard() -> None:
    """Muestra un pequeño tablero de bienvenida con botones grandes e íconos."""
    st.markdown(
        """
        <div class='welcome-panel'>
            <h3>Inicio rápido</h3>
            <p>Elige una acción clave para comenzar tu trabajo judicial.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        {
            "icon": "📂",
            "title": "Cargar expediente",
            "text": "Sube tu PDF o imagen de prueba y comienza el análisis.",
        },
        {
            "icon": "⚙️",
            "title": "Configurar Groq",
            "text": "Verifica la conexión, selecciona el modelo y ajusta fragmentos.",
        },
        {
            "icon": "📋",
            "title": "Revisar resultados",
            "text": "Descarga informes y consulta el workspace de seguimiento.",
        },
    ]

    cols = st.columns(3)
    for col, card in zip(cols, cards):
        col.markdown(
            f"<div class='welcome-card'>"
            f"<div class='welcome-icon'>{card['icon']}</div>"
            f"<h4>{card['title']}</h4>"
            f"<p>{card['text']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )




def render_tour_modal(view: str = "user") -> None:
    """Muestra una tarjeta flotante lateral con el resumen del tour."""
    if st.query_params.get("tour") == "true":
        st.markdown(
            """
            <style>
            .floating-tour-card {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 380px;
                background: var(--card-bg);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                z-index: 9999;
                border: 1px solid var(--border-color);
                border-top: 5px solid var(--gold-accent);
                animation: slideInRight 0.4s ease-out;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            .tour-step-mini {
                padding: 8px 12px;
                border-left: 4px solid var(--gold-accent);
                background: rgba(26, 54, 93, 0.03);
                margin-bottom: 8px;
                border-radius: 4px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.container():
            st.markdown('<div class="floating-tour-card">', unsafe_allow_html=True)
            
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"#### <span style='color:var(--primary-color);'>🎯 Guía Rápida</span>", unsafe_allow_html=True)
            with c2:
                if st.button("✖️", key=f"tour_close_mini_{view}"):
                    del st.query_params["tour"]
                    st.rerun()

            st.markdown("<p style='font-size:0.85rem; color:var(--text-muted);'>Sigue estos pasos para dominar Justicia IA:</p>", unsafe_allow_html=True)
            
            steps = [
                ("1. Inicio", "Accede con tu usuario."),
                ("2. Carga", "Sube tus expedientes."),
                ("3. Proceso", "Analiza con IA Groq."),
                ("4. Workspace", "Gestiona y descarga.")
            ]

            for title, desc in steps:
                st.markdown(f"""
                <div class="tour-step-mini">
                    <b style="color:var(--primary-color); font-size:0.9rem;">{title}</b><br>
                    <span style="color:var(--text-main); font-size:0.8rem;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)

            
            if st.button("Abrir Guía Interactiva 📖", key=f"tour_open_full_{view}", use_container_width=True, type="primary"):
                st.session_state["show_tutorial"] = True
                del st.query_params["tour"]
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)





def render_interactive_guide(view: str = "user") -> None:
    """Muestra una guía paso a paso adaptada al rol de usuario."""
    tutorial_steps = [
        {
            "title": "Bienvenida al flujo judicial",
            "description": (
                "Aquí puedes cargar expedientes, revisar el estado de la API y procesar documentos legales. "
                "Sigue cada paso para obtener un análisis estructurado de tus archivos."
            ),
        },
        {
            "title": "Configura tu API y modelo",
            "description": (
                "En la barra lateral revisa la conexión con Groq, actualiza tu clave API si es necesario y selecciona el modelo adecuado. "
                "Un modelo correcto mejora la calidad del análisis."
            ),
        },
        {
            "title": "Carga y organiza tu expediente",
            "description": (
                "Sube uno o varios archivos PDF, imágenes o documentos legales. "
                "Asocia cada expediente a una carpeta para mantener tu trabajo ordenado."
            ),
        },
        {
            "title": "Procesa el documento",
            "description": (
                "Pulsa el botón de inicio para extraer y analizar el contenido. "
                "La aplicación mostrará progreso y luego te permitirá descargar resultados."
            ),
        },
        {
            "title": "Revisa el resultado y descarga",
            "description": (
                "Consulta el informe generado, visualiza el texto extraído y descarga el PDF o TXT. "
                "Si eres administrador, explora también el workspace y la configuración avanzada."
            ),
        },
    ]

    if view == "admin":
        tutorial_steps.insert(2, {
            "title": "Administra usuarios y datos",
            "description": (
                "Desde el panel de administración puedes crear usuarios, revisar el repositorio de entrenamiento "
                "y sincronizar jurisprudencia para mejorar la base de conocimiento."
            ),
        })

    key = f"tutorial_step_{view}"
    if key not in st.session_state:
        st.session_state[key] = 0

    current_index = st.session_state[key]
    total_steps = len(tutorial_steps)

    with st.expander("📘 Guía Interactiva de la Aplicación", expanded=False):
        st.markdown(
            f"<div class='tutorial-card'>"
            f"<p class='step-badge'>Paso {current_index + 1} de {total_steps}</p>"
            f"<h4>{tutorial_steps[current_index]['title']}</h4>"
            f"<p>{tutorial_steps[current_index]['description']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Usar una disposición más simple para evitar errores de reconciliación en el DOM
        col_nav = st.container()
        with col_nav:
            btn_prev, btn_reset, btn_next = st.columns(3)
            if btn_prev.button("◀️ Anterior", disabled=current_index == 0, key=f"tutorial_prev_{view}", use_container_width=True):
                st.session_state[key] = max(0, current_index - 1)
                st.rerun()
            if btn_reset.button("🔄 Reiniciar", key=f"tutorial_reset_{view}", use_container_width=True):
                st.session_state[key] = 0
                st.rerun()
            if btn_next.button("▶️ Siguiente", disabled=current_index == total_steps - 1, key=f"tutorial_next_{view}", use_container_width=True, type="primary"):
                st.session_state[key] = min(total_steps - 1, current_index + 1)
                st.rerun()



def render_floating_assistant(client: GroqClient, model: str) -> None:
    """Renderiza un asistente legal flotante mediante un Popover."""
    
    # CSS para posicionar el asistente de forma fija (opcional, Streamlit controla el popover)
    st.markdown("""
        <style>
        .floating-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.divider()
        with st.popover("📚 Consultor de Normas", use_container_width=True):
            st.markdown("### ⚖️ Buscador Legal Express")
            st.caption("Consulta leyes, códigos y normas colombianas al instante.")
            
            search_query = st.text_input("¿Qué norma buscas?", placeholder="Ej: Código General del Proceso Art 20...")
            
            if search_query:
                with st.spinner("Buscando en la normativa..."):
                    prompt = f"""
                    Eres un Asistente Legal experto en derecho colombiano. 
                    El usuario busca información sobre la siguiente norma o tema: '{search_query}'.
                    
                    Por favor, proporciona:
                    1. El nombre exacto de la norma/ley.
                    2. Un resumen del artículo o artículos relevantes.
                    3. Cómo se aplica comúnmente en procesos judiciales.
                    
                    Responde de forma concisa y técnica en Markdown.
                    """
                    try:
                        response = client.generate(prompt, model)
                        st.markdown(response)
                        
                        # GUARDAR EN DISPOSITIVO LOCAL
                        from core.database import save_search_history
                        save_search_history(search_query, response)
                        
                    except Exception as e:
                        st.error(f"Error en consulta: {e}")
            
            st.info("💡 Consejo: Sé específico con el número de artículo para mayor precisión.")
            
            # MOSTRAR HISTORIAL
            from core.database import load_search_history
            history = load_search_history()
            if history:
                st.divider()
                st.markdown("#### 🕒 Consultas Recientes")
                for h in history:
                    with st.expander(f"📌 {h['consulta'][:30]}...", expanded=False):
                        st.caption(f"Fecha: {h['fecha']}")
                        st.markdown(h['respuesta_ia'])


def render_file_explorer(organized_path: str) -> None:
    """Muestra un explorador de los archivos organizados físicamente por categoría."""
    st.markdown("### 📂 Explorador de Archivos (Categorizados)")
    
    if st.button("🔄 Actualizar Vista de Carpetas"):
        st.rerun()

    if not os.path.exists(organized_path):
        st.warning("No hay carpetas organizadas aún.")
        return

    categories = os.listdir(organized_path)
    for cat in categories:
        cat_path = os.path.join(organized_path, cat)
        if os.path.isdir(cat_path):
            files = os.listdir(cat_path)
            with st.expander(f"📁 {cat} ({len(files)} archivos)", expanded=False):
                if not files:
                    st.caption("Carpeta vacía")
                else:
                    for f in files:
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"📄 {f}")
                        # Botón MOCK para abrir/ver (en un app real abriría el archivo)
                        if c2.button("👁️", key=f"view_{cat}_{f}"):
                            st.info(f"Abriendo vista previa de: {f}")

def render_tutorial():
    """Muestra una guía interactiva paso a paso para el usuario."""
    if "tutorial_step" not in st.session_state:
        st.session_state["tutorial_step"] = 0
    
    steps = [
        {
            "title": "¡Bienvenido a Justicia IA!",
            "content": "Esta plataforma optimiza tu trabajo judicial mediante Inteligencia Artificial de vanguardia. Sigue esta guía para aprender a usarla en segundos.",
            "icon": "⚖️"
        },
        {
            "title": "Paso 1: Organiza tu Despacho",
            "content": "Primero, selecciona la **Rama Judicial** y crea una **Carpeta** para organizar tus procesos (ej: 'Civiles 2024').",
            "icon": "📂"
        },
        {
            "title": "Paso 2: Carga de Expedientes",
            "content": "Sube tus archivos PDF o imágenes. Justicia IA extraerá el texto automáticamente usando OCR de alta precisión sobre Groq.",
            "icon": "📤"
        },
        {
            "title": "Paso 3: Análisis Inteligente",
            "content": "Haz clic en **INICIAR PROCESO**. La IA generará un borrador de sentencia y analizará las pruebas con tecnología Llama 3.",
            "icon": "🚀"
        },
        {
            "title": "Paso 4: Workspace 360°",
            "content": "En la pestaña **Workspace**, podrás ver la sentencia, el análisis de pruebas y chatear directamente con el expediente para resolver dudas.",
            "icon": "💬"
        }
    ]
    
    step = st.session_state["tutorial_step"]
    current = steps[step]
    
    # Usar un contenedor dedicado para el contenido dinámico
    tutorial_container = st.container()
    with tutorial_container:
        st.markdown(f"""
        <div class="tutorial-box">
            <h4 style="color:white;"><span class="step-indicator">{step + 1}</span> {current['icon']} {current['title']}</h4>
            <p style="color:white; margin-top:10px;">{current['content']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        if step > 0:
            if c1.button("⬅️ Anterior", key="tut_prev", use_container_width=True):
                st.session_state["tutorial_step"] -= 1
                st.rerun()
        
        if step < len(steps) - 1:
            if c2.button("Siguiente ➡️", key="tut_next", use_container_width=True, type="primary"):
                st.session_state["tutorial_step"] += 1
                st.rerun()
        else:
            if c2.button("Finalizar 🎉", key="tut_finish", use_container_width=True, type="primary"):
                # Persistir que ya vio el tutorial
                auth = st.session_state.get("auth_manager")
                user = st.session_state.get("current_user")
                if auth and user:
                    auth.mark_tutorial_seen(user.username)
                    user.has_seen_tutorial = True
                
                st.session_state["show_tutorial"] = False
                st.session_state["tutorial_step"] = 0
                st.rerun()
        
        if c3.button("Cerrar ✖️", key="tut_close", use_container_width=True):
            # También persistimos si decide cerrarlo para no molestarlo cada vez
            auth = st.session_state.get("auth_manager")
            user = st.session_state.get("current_user")
            if auth and user:
                auth.mark_tutorial_seen(user.username)
                user.has_seen_tutorial = True
                
            st.session_state["show_tutorial"] = False
            st.rerun()


