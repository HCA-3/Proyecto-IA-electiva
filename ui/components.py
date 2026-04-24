"""
ui/components.py
----------------
Componentes reutilizables de la interfaz Streamlit de Justicia IA.
Actualizado para soportar la API de Groq.
"""

from __future__ import annotations

from dataclasses import dataclass

import os
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
            
        if api_key:
            client.set_api_key(api_key)

        connected, models = client.check_connection()

        if connected:
            st.markdown('<span class="status-ok">🟢 Groq Conectado</span>', unsafe_allow_html=True)
            st.caption("Peticiones ultra-rápidas mediante LPU")
        else:
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
        selected_model=selected_model or models[0],
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
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.download_button(
            label="📄 Descargar Informe (PDF)",
            data=result.to_pdf(filename),
            file_name=f"{base_name}_judicial.pdf",
            mime="application/pdf",
        )
    with col_d2:
        st.download_button(
            label="📝 Descargar (TXT)",
            data=result.to_text(filename),
            file_name=f"{base_name}_judicial.txt",
            mime="text/plain",
        )


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
