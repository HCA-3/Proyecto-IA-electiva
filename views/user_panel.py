"""
views/user_panel.py
--------------------
Panel del Asistente Judicial de Justicia IA (Groq).
Incluye: organización por carpetas, filtros de búsqueda y Workspace integrado.
Flujo de trabajo: 1. Seleccionar Carpeta -> 2. Seleccionar/Subir Archivos -> 3. Botón "INICIAR PROCESO".
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import datetime
import time

import config
from auth import User, Role
from core import (
    GroqClient, DocumentExtractor, DocumentAnalyzer,
    load_triage_cases, save_triage_case, update_case_chat_bulk,
    load_folders, save_folder, delete_folder, update_folder_name, 
    assign_case_to_folder, delete_case, update_case_metadata
)
from core.vector_db import MockVectorDB
from ui.components import (
    render_sidebar, render_metrics,
    render_extracted_text, render_results, SidebarState,
    render_floating_assistant, render_file_explorer
)
from ui.styles import show_book_animation


def render_user_panel(user: User, client: GroqClient) -> None:
    _render_topbar(user)

    if user.role == Role.SUPERADMIN:
        sidebar = render_sidebar(client)
    else:
        # Para usuarios normales, mostramos una versión reducida de la sidebar que incluya el asistente
        with st.sidebar:
            st.markdown(f"### 🛡️ Justicia IA - {user.display_name}")
            st.caption(f"Rol: {user.role.value}")
            st.divider()
        
        from core.database import load_api_key
        api_key = load_api_key()
        if api_key:
            client.set_api_key(api_key)
        connected, models = client.check_connection()
        sidebar = SidebarState(
            api_connected=connected,
            available_models=models,
            selected_model=models[0] if models else "llama3-8b-8192",
            chunk_size=config.DEFAULT_CHUNK_SIZE,
            max_parts=config.DEFAULT_MAX_PARTS
        )
    
    # Renderizamos el nuevo asistente legal flotante en la sidebar
    render_floating_assistant(client, sidebar.selected_model)

    st.warning(
        "⚖️ **Asistente de Soporte Judicial:** Esta herramienta genera borradores de decisiones basados en el contenido "
        "de los expedientes cargados. La responsabilidad final de la providencia recae en el funcionario judicial humano."
    )

    st.divider()

    # --- Cargar datos ---
    if "cases_db" not in st.session_state:
        st.session_state["cases_db"] = load_triage_cases()
    
    if f"folders_{user.username}" not in st.session_state:
        st.session_state[f"folders_{user.username}"] = load_folders(user.username)

    # Definir pestañas según el rol
    is_admin = getattr(user.role, "value", user.role) == Role.SUPERADMIN.value
    
    if is_admin:
        tab_list = ["🔍 Cargar y Analizar", "⚖️ Workspace", "🌐 Rama Judicial", "🗄️ Archivos", "🧩 Info"]
    else:
        # Los usuarios normales solo ven la funcionalidad core
        tab_list = ["🔍 Cargar y Analizar Expediente", "⚖️ Workspace: Sentencias y Pruebas", "🗄️ Archivos (Categorización Real)"]
    
    tabs = st.tabs(tab_list)

    if is_admin:
        with tabs[0]: _render_analysis_tab(user, client, sidebar)
        with tabs[1]: _render_workspace_tab(user, client, sidebar)
        with tabs[2]: _render_rama_tab(user, client, sidebar)
        with tabs[3]: 
            from core.database import ORGANIZED_PATH
            render_file_explorer(ORGANIZED_PATH)
        with tabs[4]: _render_info_tab()
    else:
        with tabs[0]: _render_analysis_tab(user, client, sidebar)
        with tabs[1]: _render_workspace_tab(user, client, sidebar)
        with tabs[2]:
            from core.database import ORGANIZED_PATH
            render_file_explorer(ORGANIZED_PATH)


def _render_analysis_tab(user: User, client: GroqClient, sidebar: SidebarState) -> None:
    st.markdown("### 🔍 Configuración del Análisis")
    
    folders = st.session_state.get(f"folders_{user.username}", ["Sin carpeta"])
    
    # 1. PASO: RAMA JUDICIAL
    st.markdown("#### 1. SELECCIONAR RAMA JUDICIAL")
    rama_judicial = st.selectbox(
        "⚖️ Especialidad del despacho:",
        ["Administrativo", "Civil", "Familia", "Laboral", "Penal", "Otros"],
        key=f"rama_activa_{user.username}"
    )

    st.divider()

    # 2. PASO: SELECCIONAR CARPETA
    st.markdown("#### 2. SELECCIONAR CARPETA DE DESTINO")
    col_c1, col_c2 = st.columns([3, 2])
    with col_c1:
        f_active = st.selectbox("📂 Carpeta activa para el nuevo proceso:", options=folders, key=f"f_active_{user.username}")
    with col_c2:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("➕ Nueva Carpeta", key="btn_new_f_ana"):
            st.session_state["show_n_f_ana"] = True
            
    if st.session_state.get("show_n_f_ana"):
        with st.container(border=True):
            nf = st.text_input("Nombre de carpeta:", key="nf_ana_input")
            c1, c2 = st.columns(2)
            if c1.button("Crear", key="nf_ana_ok"):
                if nf.strip():
                    save_folder(user.username, nf.strip())
                    st.session_state[f"folders_{user.username}"] = load_folders(user.username)
                    st.session_state["show_n_f_ana"] = False
                    st.rerun()
            if c2.button("Cancelar", key="nf_ana_cancel"):
                st.session_state["show_n_f_ana"] = False
                st.rerun()

    st.divider()

    # 3. PASO: SELECCIONAR ARCHIVOS
    st.markdown("#### 3. SELECCIONAR ARCHIVOS DEL EXPEDIENTE")
    up_files = st.file_uploader(
        "Arrastra aquí los archivos (.pdf, .jpg, .png):",
        type=config.SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        key=f"u_files_{user.username}"
    )

    st.divider()

    # 4. PASO: BOTON INICIAR
    st.markdown("#### 4. EJECUTAR PROCESAMIENTO")
    if not up_files:
        st.info("Selecciona al menos un archivo para habilitar el botón de inicio.")
        st.button("🚀 INICIAR PROCESO DE ANÁLISIS", disabled=True)
    else:
        if st.button("🚀 INICIAR PROCESO DE ANÁLISIS", type="primary", use_container_width=True):
            if not sidebar.api_connected:
                st.error("❌ Groq no configurado. Verifica la API en el panel de Admin.")
            else:
                progress_bar = st.progress(0, text="Iniciando motor de IA...")
                extractor = DocumentExtractor(client=client)
                total = len(up_files)

                for i, f in enumerate(up_files):
                    try:
                        def on_prog(p, m):
                            progress_bar.progress(min((i + p) / total, 1.0), text=f"Documento {i+1}/{total}: {m}")

                        # Extracción
                        ext = extractor.extract(f, f.type, progress_cb=on_prog)
                        if not ext.text: continue

                        # Análisis IA
                        analyzer = DocumentAnalyzer(client=client, progress_cb=on_prog)
                        ana = analyzer.analyze(
                            text=ext.text,
                            model=sidebar.selected_model,
                            chunk_size=sidebar.chunk_size,
                            max_parts=sidebar.max_parts
                        )

                        # Guardar
                        new_case = {
                            "Archivo": f.name,
                            "Modelo": sidebar.selected_model,
                            "Extracto_Texto": ext.text[:5000],
                            "Reporte_Extendido": ana.final_report,
                            "Analisis_Pruebas": ana.evidence_analysis,
                            "Tipo_Proceso": rama_judicial,  # Usamos la rama seleccionada manualmente
                            "Chat": [],
                            "Carpeta": f_active,
                            "Duracion": ana.duration,
                            "Costo_Est": ana.estimated_cost,
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Owner": user.username
                        }

                        # Guardar físicamente en carpetas por categoría (MOCK DOWNLOAD)
                        import os
                        organized_path = os.path.join("data", "organized", ana.process_type, f.name)
                        try:
                            with open(organized_path, "wb") as file_dest:
                                file_dest.write(f.getvalue())
                        except: pass

                        save_triage_case(new_case, user.username, f_active)
                        st.success(f"✅ Finalizado con éxito: {f.name}")
                    except Exception as exc:
                        st.error(f"❌ Error procesando {f.name}: {exc}")

                st.session_state["cases_db"] = load_triage_cases()
                progress_bar.progress(1.0, text="¡Análisis completado! Ve a la pestaña 'Workspace'.")
                show_book_animation()
                time.sleep(3) # Pausa para ver la lluvia de abogados
                st.rerun()


def _render_workspace_tab(user: User, client: GroqClient, sidebar: SidebarState) -> None:
    st.markdown("### ⚖️ Gestión de Expedientes y Sentencias")
    
    folders = st.session_state.get(f"folders_{user.username}", ["Sin carpeta"])
    cases_db = [c for c in load_triage_cases() if c.get("Owner") == user.username or user.role == Role.SUPERADMIN]

    # Barra lateral de organización (Solo visible en Workspace)
    with st.sidebar:
        if user.role != Role.SUPERADMIN:
            st.markdown("---")
            st.markdown("### 📁 Carpetas del Usuario")
            for f_name in folders:
                if f_name == "Sin carpeta":
                    st.write(f"📂 {f_name}")
                else:
                    c_edit, c_del = st.columns([1, 1])
                    if c_edit.button(f"✏️ {f_name}", key=f"edit_{f_name}"):
                        st.session_state["renaming_folder"] = f_name
                    if c_del.button(f"🗑️", key=f"del_{f_name}"):
                        delete_folder(user.username, f_name)
                        st.rerun()

            if "renaming_folder" in st.session_state:
                with st.form("rename_form"):
                    old = st.session_state["renaming_folder"]
                    new_val = st.text_input(f"Renombrar '{old}':")
                    if st.form_submit_button("Guardar"):
                        if new_val.strip():
                            update_folder_name(user.username, old, new_val.strip())
                            del st.session_state["renaming_folder"]
                            st.rerun()

    # Filtros
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        f_folder = st.selectbox("📂 Carpeta", ["Todas"] + folders, key="ws_f_folder")
    with c_f2:
        proc_types = ["Todos", "Civil", "Familia", "Laboral", "Penal", "Administrativo", "Otros"]
        f_type = st.selectbox("🗂️ Tipo de Proceso", proc_types, key="ws_f_type")
    with c_f3:
        f_search = st.text_input("🔍 Buscar Nombre", placeholder="Expediente...", key="ws_f_search")

    filtered = cases_db
    if f_folder != "Todas":
        filtered = [c for c in filtered if c.get("Carpeta") == f_folder]
    if f_type != "Todos":
        filtered = [c for c in filtered if c.get("Tipo_Proceso") == f_type]
    if f_search.strip():
        filtered = [c for c in filtered if f_search.lower() in c.get("Archivo", "").lower()]

    if not filtered:
        st.info("No se encontraron expedientes con los filtros seleccionados.")
        return

    # Selector de Expediente
    sel_opts = [f"[{c.get('Carpeta')}] {c.get('Archivo')}" for c in filtered]
    sel_label = st.selectbox("📂 ABIERTOS RECIENTEMENTE:", sel_opts)
    
    fname = sel_label.split("] ", 1)[-1] if "] " in sel_label else sel_label
    curr = next((c for c in cases_db if c.get("Archivo") == fname), None)

    if curr:
        with st.expander("🛠️ ACCIONES RÁPIDAS (Mover / Borrar)", expanded=False):
            m1, m2 = st.columns(2)
            with m1:
                mov_dest = st.selectbox("Mover a:", folders, index=folders.index(curr.get("Carpeta")) if curr.get("Carpeta") in folders else 0)
                if st.button("Mover Expediente"):
                    assign_case_to_folder(fname, user.username, mov_dest)
                    st.rerun()
            with m2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("🗑️ ELIMINAR EXPEDIENTE", type="primary"):
                    delete_case(fname, user.username)
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### ✅ VALIDACIÓN DE RESULTADOS (IA Accuracy)")
            st.caption("Evalúa si la respuesta de la IA fue acertada para el cálculo de métricas de precisión.")
            
            # Estado actual de validación
            valid_val = curr.get("Validacion", "Pendiente")
            valid_notes = curr.get("Notas_Validacion", "")
            
            c_v1, c_v2 = st.columns([1, 2])
            with c_v1:
                new_v = st.radio("Resultado:", ["Correcto", "Incorrecto", "Pendiente"], 
                                 index=["Correcto", "Incorrecto", "Pendiente"].index(valid_val),
                                 key=f"rad_v_{fname}")
            with c_v2:
                new_n = st.text_area("Observaciones (Sesgos, errores, etc.):", value=valid_notes, height=70, key=f"notes_v_{fname}")
                
            if st.button("💾 Guardar Evaluación Técnica"):
                update_case_metadata(fname, user.username, {"Validacion": new_v, "Notas_Validacion": new_n})
                st.success("Evaluación guardada para el informe final.")
                st.rerun()

            st.markdown("---")
            st.markdown("#### 📁 Cargar Prueba Adicional (Documentos de Escritura)")
            st.caption("Solo se permiten documentos de texto (.pdf, .docx, .txt). No se admiten fotos ni videos.")
            extra_file = st.file_uploader("Adjuntar documento de prueba:", type=["pdf", "docx", "txt"], key=f"extra_{fname}")
            if extra_file:
                if st.button("Interpretación de Prueba", use_container_width=True):
                    with st.spinner("Analizando prueba multimedia..."):
                        extracted_text = ""
                        # Procesar como documento de texto
                        from core.extractor import DocumentExtractor
                        extractor = DocumentExtractor(client=client)
                        ext = extractor.extract(extra_file, extra_file.type)
                        extracted_text = ext.text
                        
                        # Interpretar prueba
                        prompt = f"Analiza esta prueba específica y explica su relevancia para el caso: '{extracted_text}'"
                        interpretation = client.generate(prompt, sidebar.selected_model)
                        
                        # Guardar en el análisis de pruebas
                        new_evid = f"\n\n---\n**Nueva Prueba ({extra_file.name}):**\n{interpretation}"
                        curr["Analisis_Pruebas"] = curr.get("Analisis_Pruebas", "") + new_evid
                        
                        # También añadir al chat
                        msg = {"role": "assistant", "content": f"He analizado la prueba **{extra_file.name}**. Resultados: {interpretation}"}
                        curr["Chat"].append(msg)
                        
                        from core.database import update_case_metadata, update_case_chat_bulk
                        update_case_metadata(fname, user.username, {"Analisis_Pruebas": curr["Analisis_Pruebas"]})
                        update_case_chat_bulk(fname, [msg])
                        st.success("✅ Prueba integrada y analizada con éxito.")
                        st.rerun()

        st.divider()

        # Métricas de Desempeño del Prototipo
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏱️ Tiempo Proc.", f"{curr.get('Duracion', 0)}s")
        m2.metric("🗂️ Categoría", curr.get("Tipo_Proceso", "Otros"))
        m3.metric("🧠 Modelo", curr.get("Modelo", "Desconocido").split("-")[0])
        m4.metric("📄 Folios", f"{len(curr.get('Extracto_Texto','')) // 1000}+")

        st.divider()

        # --- SECCIÓN DE JURISPRUDENCIA (MOCK VECTOR DB) ---
        with st.container(border=True):
            col_j1, col_j2 = st.columns([3, 1])
            with col_j1:
                st.markdown("#### ⚖️ Consulta de Jurisprudencia y Precedentes")
                st.caption("Uso de Base de Datos Vectorial (Simulación) para búsqueda de casos similares en el repositorio judicial.")
            with col_j2:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("🔍 Buscar Precedentes", use_container_width=True, key="btn_vector_search"):
                    st.session_state["show_jurisprudencia"] = True
            
            if st.session_state.get("show_jurisprudencia"):
                vdb = MockVectorDB()
                # Usamos el tipo de proceso y archivo como query semántico
                query = f"{curr.get('Tipo_Proceso')} {curr.get('Archivo')} {curr.get('Extracto_Texto', '')[:100]}"
                results = vdb.search_precedents(query)
                
                if results:
                    st.success(f"Se han encontrado {len(results)} precedentes relevantes en la base de datos vectorial.")
                    for res in results:
                        with st.expander(f"📍 Precedente: {res.get('Archivo')}"):
                            st.write(f"**Tipo:** {res.get('Tipo_Proceso')}")
                            st.write(f"**Decisión Previa:** {res.get('Reporte_Extendido', '')[:500]}...")
                            if st.button("Inyectar en Contexto", key=f"inj_{res.get('Archivo')}"):
                                # Añadir nota al chat
                                msg = {"role": "system", "content": f"REFERENCIA DE PRECEDENTE ({res.get('Archivo')}): {res.get('Reporte_Extendido', '')[:1000]}"}
                                if "Chat" not in curr: curr["Chat"] = []
                                curr["Chat"].append(msg)
                                from core.database import update_case_chat_bulk
                                update_case_chat_bulk(fname, [msg])
                                st.info("Precedente inyectado en el chat del asistente.")
                else:
                    st.info("No se encontraron casos similares suficientes para establecer un precedente vectorial.")

        st.divider()

        # Workspace de 3 columnas
        cw1, cw2, cw3 = st.columns([1, 1, 1], gap="medium")
        
        with cw1:
            st.markdown("#### 📜 SENTENCIA")
            txt = curr.get("Reporte_Extendido", "")
            st.markdown(f'<div class="card" style="height:500px; overflow-y:auto; padding:15px; background:white; color:black;">{txt}</div>', unsafe_allow_html=True)
        
        with cw2:
            st.markdown("#### 🔍 PRUEBAS")
            t_p = curr.get("Analisis_Pruebas", "")
            st.markdown(f'<div class="card" style="height:500px; overflow-y:auto; padding:15px; background:#f4f4f9; color:black;">{t_p}</div>', unsafe_allow_html=True)
            
        with cw3:
            st.markdown("#### 💬 CHAT")
            chat_container = st.container(height=450)
            with chat_container:
                for m in curr.get("Chat", []):
                    with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if q := st.chat_input("Hacer consulta específica..."):
                with chat_container:
                    with st.chat_message("user"): st.markdown(q)
                    with st.chat_message("assistant"):
                        with st.spinner("Analizando..."):
                            ctx = f"Sentencia: {curr.get('Reporte_Extendido')}\nPruebas: {curr.get('Analisis_Pruebas')}"
                            ans = client.generate(f"Contexto: {ctx[:4000]}\n\nPregunta: {q}", sidebar.selected_model)
                            st.markdown(ans)
                update_case_chat_bulk(fname, [{"role":"user","content":q}, {"role":"assistant","content":ans}])


def _render_rama_tab(user: User, client: GroqClient, sidebar: SidebarState) -> None:
    st.markdown("### 🌐 Conexión API Rama Judicial (Fines Académicos)")
    st.info("Ingresa el número de radicado (23 dígitos) para sincronizar el expediente directamente con la base de datos judicial.")
    
    col1, col2 = st.columns([3, 1])
    rad = col1.text_input("Número de Radicación Nacional Unificado:", placeholder="05001310300220230000100", max_chars=23)
    
    if col2.button("Sincronizar API", use_container_width=True):
        if len(rad) < 23:
            st.error("❌ El radicado debe tener 23 dígitos oficiales.")
        else:
            with st.spinner("Conectando con Servidores de la Rama Judicial..."):
                from core.database import mock_rama_judicial_search
                res = mock_rama_judicial_search(rad)
                
                st.success(f"✅ Proceso encontrado: {res['despacho']}")
                
                # Sincronización Automática
                with st.expander("📂 Detalles del Expediente Sincronizado", expanded=True):
                    st.json(res)
                
                # Crear el caso en el sistema
                new_case = {
                    "Archivo": f"Radicado_{rad}.pdf",
                    "Modelo": sidebar.selected_model,
                    "Extracto_Texto": f"Documento sincronizado automáticamente desde la Rama Judicial. Radicado: {rad}\nÚltima actuación: {res['ultima_actuacion']}",
                    "Reporte_Extendido": f"### Sincronización API\nEl proceso ha sido importado con éxito. Se recomienda realizar un análisis detallado de pruebas.",
                    "Analisis_Pruebas": f"Actuación Reciente: {res['ultima_actuacion']}\nTipo de Proceso: {res['tipo']}",
                    "Tipo_Proceso": res['tipo'],
                    "Chat": [{"role": "assistant", "content": "Hola, soy tu asistente judicial. He sincronizado este expediente desde la Rama Judicial. ¿Cómo puedo ayudarte hoy?"}],
                    "Carpeta": "Sincronizados API",
                    "Duracion": 1.5,
                    "Costo_Est": 0.0,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Owner": user.username
                }
                
                # Crear carpeta si no existe
                from core.database import save_folder, save_triage_case
                save_folder(user.username, "Sincronizados API")
                save_triage_case(new_case, user.username, "Sincronizados API")
                
                st.info(f"📂 El expediente se ha descargado y organizado en: `data/organized/{res['tipo']}/Radicado_{rad}.pdf`")
                show_book_animation()
                time.sleep(3) # Pausa para ver la animación
                st.rerun()


def _render_info_tab() -> None:
    st.markdown("### 🧩 Documentación y Selección de Flujos de IA")
    
    with st.expander("📊 1. Matriz de Decisión del Flujo de Trabajo", expanded=True):
        st.markdown("""
        | Criterio | Selección | Justificación Técnica |
        | :--- | :--- | :--- |
        | **Dominio** | Justicia | Se enfoca en la descongestión judicial y apoyo al despacho. |
        | **Tipo de IA** | Generativa (LLM) | Ideal para resumir expedientes y proponer borradores legales. |
        | **Modelo** | Groq LPU (Llama 3) | Latencia ultra-baja (<1s) necesaria para flujos de trabajo masivos. |
        | **Infraestructura** | Streamlit + Python | Prototipado rápido y desplegable en navegador sin instalación local. |
        | **Datos** | Texto No Estructurado | OCR integrado para PDFs escaneados y extracción de pruebas. |
        """)

    with st.expander("⚖️ 2. Consideraciones Éticas y de Privacidad"):
        st.markdown("""
        **Evaluación Crítica del Prototipo:**
        - **Sesgos:** Los modelos de lenguaje pueden heredar sesgos de sus datos de entrenamiento. Se requiere supervisión humana constante.
        - **Privacidad:** Los datos se procesan mediante API. En una fase de producción, se recomienda el uso de LLMs locales (ej. Llama 3 vía Ollama) para asegurar aislamiento total.
        - **Alucinaciones:** La IA puede inventar fechas o nombres. El prototipo incluye una advertencia persistente en todas las interfaces.
        - **Fuerza Probatoria:** La valoración de pruebas es una sugerencia; el Juez debe confrontar el expediente original.
        """)

    with st.expander("🚀 3. Escalabilidad y Siguientes Pasos"):
        st.markdown("""
        1. **Integración con SIGLO (o sistemas locales):** Conexión vía API a bases de datos judiciales reales.
        2. **RAG (Retrieval Augmented Generation):** Implementar base de conocimientos con la jurisprudencia de las altas cortes.
        3. **Firma Digital:** Integración de procesos de firma electrónica para cerrar el ciclo del documento.
        """)

def _render_topbar(user: User) -> None:
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown('<p class="main-title">⚖️ Justicia IA — Asistente</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"<br><div style='text-align:right;'><b>{user.display_name}</b></div>", unsafe_allow_html=True)
        if st.button("Salir", key="top_logout"):
            st.session_state.clear()
            st.query_params.clear() # Limpiar persistencia de la URL
            st.rerun()
