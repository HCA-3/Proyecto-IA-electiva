"""
views/login.py
--------------
Página de inicio de sesión y registro de Justicia IA.
Maneja la autenticación y permite a nuevos usuarios registrarse.
"""

from __future__ import annotations

import streamlit as st
from auth import AuthManager, Role


def render_login_page(auth: AuthManager) -> None:
    """
    Renderiza la pantalla de login y registro.
    """
    # Centrar el formulario
    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        st.markdown("""
        <div class="glass-card" style="padding: 2rem;">
            <div style="text-align:center; padding-bottom: 1rem;">
                <span style="font-size:3.5rem;">⚖️</span>
                <h1 style="
                    font-size:2rem; font-weight:700; margin:0.5rem 0 0.2rem;
                    background: linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text;">
                    Justicia IA
                </h1>
                <p style="color:#9ca3af; font-size:0.9rem; margin-bottom:1.5rem;">
                    Asistente Judicial Inteligente
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            """
            <div style="background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 18px; padding: 1rem; margin-bottom: 1rem;">
                <h3 style="margin:0; color: #0f172a;">🚀 Bienvenido a Justicia IA</h3>
                <p style="margin:0.4rem 0 0; color: #475569;">
                    Usa esta plataforma para organizar expedientes, analizar documentos legales y generar borradores de decisiones con asistencia de IA.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info("""
        **🎓 Proyecto de Investigación Académica:**  
        Desarrollado para la asignatura *'Descubrimiento de problemas y diseño de soluciones con IA'*. 
        """)

        _render_login_guide()

        mode = st.radio("Selecciona una opción", ["Iniciar Sesión", "Registrarse"], horizontal=True, label_visibility="collapsed")

        if mode == "Iniciar Sesión":
            _render_login_form(auth)
        else:
            _render_signup_form(auth)
        
        st.markdown('</div>', unsafe_allow_html=True)


def _render_login_form(auth: AuthManager) -> None:
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<p style="color:#d1d5db; font-weight:600; margin-bottom:0.3rem;">👤 Usuario</p>', unsafe_allow_html=True)
        username = st.text_input("Usuario", placeholder="Ingresa tu usuario", label_visibility="collapsed")

        st.markdown('<p style="color:#d1d5db; font-weight:600; margin:0.8rem 0 0.3rem;">🔒 Contraseña</p>', unsafe_allow_html=True)
        password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed")

        submitted = st.form_submit_button("Entrar al Sistema", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("⚠️ Completa todos los campos.")
            return

        user = auth.authenticate(username, password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = user
            st.session_state["role"] = user.role
            st.session_state["display_name"] = user.display_name
            # Guardamos persistencia en la URL
            st.query_params["active_user"] = user.username
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")


def _render_login_guide() -> None:
    st.markdown("---")
    with st.expander("📘 Guía rápida de inicio", expanded=True):
        st.markdown(
            """
            **Sigue estos pasos para usar Justicia IA:**
            1. Regístrate o inicia sesión con tu cuenta judicial.
            2. En el panel principal, carga tu expediente en PDF o imagen.
            3. Selecciona la carpeta de destino y la rama judicial correspondiente.
            4. Presiona `INICIAR PROCESO DE ANÁLISIS` para generar el borrador.
            5. Revisa el informe, descarga archivos y consulta el Workspace para seguimiento.
            """
        )
        st.info("Puedes volver a esta guía desde el panel principal si necesitas repasar el flujo de trabajo.")


def _render_signup_form(auth: AuthManager) -> None:
    with st.form("signup_form", clear_on_submit=False):
        st.markdown('<p style="color:#d1d5db; font-weight:600; margin-bottom:0.3rem;">👤 Nombre Completo</p>', unsafe_allow_html=True)
        display_name = st.text_input("Nombre", placeholder="Ej: Juan Pérez", label_visibility="collapsed")

        st.markdown('<p style="color:#d1d5db; font-weight:600; margin:0.8rem 0 0.3rem;">🆔 Usuario</p>', unsafe_allow_html=True)
        username = st.text_input("Usuario ID", placeholder="Ej: juan.perez", label_visibility="collapsed")

        st.markdown('<p style="color:#d1d5db; font-weight:600; margin:0.8rem 0 0.3rem;">🔒 Contraseña</p>', unsafe_allow_html=True)
        password = st.text_input("Contraseña", type="password", placeholder="Crea tu contraseña", label_visibility="collapsed")

        st.divider()
        st.markdown("### 📄 Política de Tratamiento de Datos")
        with st.container(height=150):
            st.markdown("""
            **1. Finalidad:** Los datos cargados (expedientes, grabaciones) se procesan exclusivamente para demostrar capacidades de IA en un entorno académico.  
            **2. Privacidad:** El sistema utiliza la API de Groq para inferencia. No se almacenan datos personales de terceros de forma permanente en servidores externos.  
            **3. Eliminación:** El usuario tiene control total para eliminar sus expedientes y chats en cualquier momento desde el panel de Workspace.  
            **4. Responsabilidad:** Los resultados son sugerencias de IA y deben ser validados por un profesional humano.
            """)
        
        accept_terms = st.checkbox("He leído y acepto la política de tratamiento de datos para fines académicos.", key="terms_signup")

        submitted = st.form_submit_button("Crear Cuenta Judicial", use_container_width=True)

    if submitted:
        if not accept_terms:
            st.error("⚠️ Debes aceptar la política de tratamiento de datos para continuar.")
            return
            
        if not display_name or not username or not password:
            st.error("⚠️ Todos los campos son obligatorios.")
            return

        try:
            auth.add_user(username, password, Role.USER, display_name)
            st.success("✅ Cuenta creada con éxito. ¡Ahora puedes iniciar sesión!")
            st.info("💡 Cambia a la pestaña 'Iniciar Sesión' arriba.")
        except ValueError as exc:
            st.error(f"❌ Error: {exc}")
