def show_book_animation():
    import streamlit as st
    import random
    
    # Emojis temáticos de Abogados y Justicia
    law_emojis = ["👨‍⚖️", "👩‍⚖️", "💼", "🏢", "⚖️", "📜", "🏛️", "🖋️", "🤝"]
    html_code = ""
    
    # Creamos un contenedor para que la lluvia no se corte al instante
    for i in range(35):
        emoji = random.choice(law_emojis)
        left = random.randint(0, 95)
        delay = random.uniform(0, 1.5)
        duration = random.uniform(2.5, 4.5)
        size = random.uniform(2.0, 3.5)
        html_code += f'<div class="book-particle" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; font-size:{size}rem;">{emoji}</div>'
    
    st.markdown(html_code, unsafe_allow_html=True)

def get_css_styles(theme: str = "Moderno (Default)") -> str:
    # Colores por defecto (Moderno)
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    text_main = "#1e293b"
    text_muted = "#64748b"
    primary_color = "#3b82f6"
    hover_color = "#2563eb"
    border_color = "#e2e8f0"
    
    if theme == "Oscuro Judicial":
        bg_color = "#0f172a"
        card_bg = "#1e293b"
        text_main = "#f1f5f9"
        text_muted = "#94a3b8"
        primary_color = "#60a5fa"
        hover_color = "#3b82f6"
        border_color = "#334155"
    elif theme == "Alto Contraste":
        bg_color = "#000000"
        card_bg = "#111111"
        text_main = "#ffffff"
        text_muted = "#ffff00"
        primary_color = "#ffff00"
        hover_color = "#ffffff"
        border_color = "#ffffff"

    return f"""
<style>
/* Variables dinámicas según el tema */
:root {{
    --bg-color: {bg_color};
    --card-bg: {card_bg};
    --text-main: {text_main};
    --text-muted: {text_muted};
    --primary-color: {primary_color};
    --hover-color: {hover_color};
    --border-color: {border_color};
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}}

/* Animación de Libros Voladores */
@keyframes book-fly {{
    0% {{ transform: translateY(110vh) rotate(0deg); opacity: 0; }}
    10% {{ opacity: 1; }}
    90% {{ opacity: 1; }}
    100% {{ transform: translateY(-20vh) rotate(360deg); opacity: 0; }}
}}

.book-particle {{
    position: fixed;
    bottom: -100px;
    z-index: 999999;
    pointer-events: none;
    animation: book-fly linear forwards;
}}

.stApp {{
    background-color: var(--bg-color) !important;
    color: var(--text-main) !important;
}}

/* Forzar color de texto en todos los elementos markdown */
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div, h1, h2, h3, h4, h5, h6 {{
    color: var(--text-main) !important;
}}

.main-title {{
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0;
    background: linear-gradient(90deg, var(--primary-color), #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}}

.card_black_border {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}}

[data-testid="stSidebar"] {{
    background-color: var(--card-bg) !important;
    border-right: 1px solid var(--border-color);
}}

/* Inputs y Selectores */
.stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
    background-color: var(--card-bg) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-color) !important;
}}

/* Botones */
button[kind="primary"] {{
    background: var(--primary-color) !important;
    color: { "#000000" if theme == "Alto Contraste" else "#ffffff" } !important;
    border: none !important;
}}
</style>
"""

# Mantener por compatibilidad inicial
CSS_STYLES = get_css_styles()
