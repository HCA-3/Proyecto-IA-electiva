"""
app.py
------
Enrutador de la aplicación Justicia IA con Groq Cloud.
"""

import streamlit as st

import config
from auth import AuthManager, Role
from core import GroqClient
from ui import CSS_STYLES, get_css_styles
from views.login import render_login_page
from views.user_panel import render_user_panel
from views.admin_panel import render_admin_panel, _load_admin_settings

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar configuración del administrador para aplicar el tema
if "admin_settings" not in st.session_state:
    st.session_state["admin_settings"] = _load_admin_settings()

current_theme = st.session_state["admin_settings"].get("theme", "Moderno (Default)")
st.markdown(get_css_styles(current_theme), unsafe_allow_html=True)

if "auth_manager" not in st.session_state:
    st.session_state["auth_manager"] = AuthManager()

if "api_client" not in st.session_state:
    st.session_state["api_client"] = GroqClient()

def main():
    auth = st.session_state["auth_manager"]
    client = st.session_state["api_client"]
    
    # --- LÓGICA DE PERSISTENCIA ---
    # Si no estamos autenticados en session_state, revisamos la URL (Query Params)
    if not st.session_state.get("authenticated", False):
        query_user = st.query_params.get("active_user")
        if query_user:
            # Intentar recuperar la sesión del usuario guardado
            user_obj = next((u for u in auth.list_users() if u.username == query_user), None)
            if user_obj:
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = user_obj
                st.session_state["role"] = user_obj.role
                st.rerun()

    is_authenticated = st.session_state.get("authenticated", False)

    if not is_authenticated:
        # Al loguearse con éxito, guardamos en query_params
        res = render_login_page(auth)
        if res: # Si el login fue exitoso
            st.query_params["active_user"] = st.session_state["current_user"].username
            st.rerun()
    else:
        role = st.session_state.get("role")
        user = st.session_state.get("current_user")

        if getattr(role, "value", role) == Role.SUPERADMIN.value:
            render_admin_panel(user, client, auth)
        else:
            render_user_panel(user, client)

if __name__ == "__main__":
    main()