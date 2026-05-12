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
    # Colores actualizados (Moderno - Más profundo y profesional)
    bg_color = "#eff6ff"
    card_bg = "#ffffff"
    text_main = "#0f172a"
    text_muted = "#475569"
    primary_color = "#2563eb"
    hover_color = "#1d4ed8"
    border_color = "#bfdbfe"
    
    if theme == "Oscuro Judicial":
        bg_color = "#020617"
        card_bg = "#111827"
        text_main = "#e2e8f0"
        text_muted = "#94a3b8"
        primary_color = "#7dd3fc"
        hover_color = "#38bdf8"
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

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
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --glass-bg: {"rgba(255, 255, 255, 0.7)" if theme == "Moderno (Default)" else "rgba(15, 23, 42, 0.7)"};
    --glass-border: {"rgba(226, 232, 240, 0.5)" if theme == "Moderno (Default)" else "rgba(51, 65, 85, 0.5)"};
}}

* {{
    font-family: 'Inter', sans-serif !important;
}}

.stApp {{
    background-color: var(--bg-color) !important;
    color: var(--text-main) !important;
}}

/* Glassmorphism Card */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}}

.glass-card:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}}

.main-title {{
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--primary-color), #8b5cf6, #d946ef);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeIn 1s ease-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Improved Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--card-bg) !important;
    border-right: 1px solid var(--border-color);
    box-shadow: 4px 0 15px rgba(0,0,0,0.05);
}}

/* Custom Buttons */
.stButton>button {{
    border-radius: 10px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
}}

.stButton>button:hover {{
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}}

/* Step Indicator for Tutorial */
.step-indicator {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: var(--primary-color);
    color: white;
    border-radius: 50%;
    font-weight: 800;
    margin-right: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}}

/* Tooltip style for tutorial */
.tutorial-box {{
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    border-radius: 12px;
    position: relative;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-lg);
    border-left: 5px solid #ffffff;
    animation: bounce 2s infinite;
}}

@keyframes bounce {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-5px); }}
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

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    height: 45px;
    background-color: var(--card-bg);
    border-radius: 8px 8px 0 0;
    border: 1px solid var(--border-color);
    border-bottom: none;
    padding: 0 20px;
}}

.stTabs [aria-selected="true"] {{
    background-color: var(--primary-color) !important;
    color: white !important;
}}

.card {{
    background: var(--card-bg);
    border: 1px solid rgba(37, 99, 235, 0.18);
    border-radius: 18px;
    padding: 1.6rem;
    box-shadow: 0 18px 48px rgba(37, 99, 235, 0.08);
    margin-bottom: 1.2rem;
}}

.card_black_border {{
    background: var(--card-bg);
    border: 1px solid rgba(37, 99, 235, 0.22);
    border-radius: 18px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
}}

.feature-card {{
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(248,250,252,0.95));
    border: 1px solid rgba(59,130,246,0.16);
    border-radius: 18px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 16px 40px rgba(15,23,42,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 1rem;
}}

.feature-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 24px 48px rgba(15,23,42,0.12);
}}

.feature-icon {{
    font-size: 2.2rem;
    width: 3.2rem;
    height: 3.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.75rem;
    border-radius: 50%;
    background: rgba(59,130,246,0.15);
}}

.hero-animation {{
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    padding: 2rem 1.5rem;
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(59,130,246,0.05));
    margin-bottom: 1.5rem;
    border: 1px solid rgba(59,130,246,0.18);
}}

.hero-pill {{
    position: absolute;
    border-radius: 999px;
    opacity: 0.65;
    filter: blur(12px);
}}

.hero-pill-1 {{
    width: 120px;
    height: 120px;
    background: rgba(59,130,246,0.35);
    top: 10px;
    left: -30px;
}}

.hero-pill-2 {{
    width: 90px;
    height: 90px;
    background: rgba(16,185,129,0.28);
    top: 20px;
    right: -20px;
}}

.hero-pill-3 {{
    width: 140px;
    height: 140px;
    background: rgba(236,72,153,0.25);
    bottom: -30px;
    left: 20%;
}}

.hero-text {{
    position: relative;
    z-index: 1;
}}

.hero-text h2 {{
    margin: 0;
    font-size: 2rem;
}}

.hero-text p {{
    color: var(--text-muted);
    margin-top: 0.5rem;
}}

.welcome-panel {{
    background: rgba(59,130,246,0.09);
    border: 1px solid rgba(59,130,246,0.22);
    border-radius: 18px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}}

.welcome-card {{
    border-radius: 20px;
    padding: 1.25rem;
    background: var(--card-bg);
    border: 1px solid rgba(59,130,246,0.12);
    box-shadow: 0 14px 30px rgba(15,23,42,0.05);
}}

.welcome-card h4 {{
    margin: 0.5rem 0 0.5rem;
}}

.welcome-card p {{
    color: var(--text-muted);
    margin: 0;
}}

.welcome-icon {{
    font-size: 2rem;
    width: 3rem;
    height: 3rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(59,130,246,0.14);
    margin-bottom: 0.75rem;
}}

/* Inputs y Selectores */
.stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {{
    background-color: var(--card-bg) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-color) !important;
}}

.stMarkdown {{
    color: var(--text-main) !important;
}}

/* Botones */
button[kind="primary"] {{
    background: var(--primary-color) !important;
    color: #ffffff !important;
    border: none !important;
}}

button[kind="primary"]:hover {{
    opacity: 0.92;
}}

.tutorial-card {{
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(249,250,251,0.95));
    border: 1px solid rgba(59,130,246,0.25);
    padding: 1rem;
    border-radius: 14px;
    box-shadow: 0 12px 32px rgba(15,23,42,0.08);
    margin-bottom: 1rem;
}}

.step-badge {{
    display: inline-block;
    background: var(--primary-color);
    color: #ffffff;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-weight: 700;
    margin-bottom: 0.75rem;
}}
</style>
"""

# Mantener por compatibilidad inicial
CSS_STYLES = get_css_styles()
