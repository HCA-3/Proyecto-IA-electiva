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
    is_authenticated = st.session_state.get("authenticated", False)

    if not is_authenticated:
        render_login_page(auth)
    else:
        role = st.session_state.get("role")
        user = st.session_state.get("current_user")

        if getattr(role, "value", role) == Role.SUPERADMIN.value:
            render_admin_panel(user, client, auth)
        else:
            render_user_panel(user, client)

if __name__ == "__main__":
    main()