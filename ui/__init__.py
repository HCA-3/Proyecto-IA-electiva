"""
ui/
----
Módulo de interfaz de usuario de Justicia IA.
Contiene estilos CSS y componentes reutilizables de Streamlit.
"""

from .styles import CSS_STYLES, get_css_styles
from .components import render_sidebar, render_metrics, render_results

__all__ = ["CSS_STYLES", "get_css_styles", "render_sidebar", "render_metrics", "render_results"]
