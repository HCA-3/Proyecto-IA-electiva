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
    # Colores Judiciales con Alto Contraste y Letras Negras
    bg_color = "#dee2e6"
    card_bg = "#ffffff"
    text_main = "#000000"  # Negro puro
    text_muted = "#000000" # Negro puro
    primary_color = "#1e3a8a"
    hover_color = "#2c5282"
    border_color = "#cbd5e1"
    gold_accent = "#b8860b"
    
    if theme == "Oscuro Judicial":
        bg_color = "#0f172a"
        card_bg = "#ffffff" # Forzamos blanco para que se vea la letra negra
        text_main = "#000000"
        text_muted = "#000000"
        primary_color = "#38bdf8"
        hover_color = "#0ea5e9"
        border_color = "#334155"
        gold_accent = "#fbbf24"
    elif theme == "Alto Contraste":
        bg_color = "#ffffff"
        card_bg = "#ffffff"
        text_main = "#000000"
        text_muted = "#000000"
        primary_color = "#000000"
        hover_color = "#000000"
        border_color = "#000000"
        gold_accent = "#000000"

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
    --gold-accent: {gold_accent};
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 10px 25px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 25px 50px rgba(0, 0, 0, 0.18);
    --glass-bg: {"rgba(255, 255, 255, 0.95)"};
    --glass-border: {"rgba(203, 213, 225, 0.8)"};
}}


/* Forzar color negro en todo el sitio */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp, p, h1, h2, h3, h4, h5, h6, span, div, li, a, label, .stMarkdown {{
    color: #000000 !important;
    font-family: 'Inter', sans-serif !important;
}}

.stApp {{
    background-color: var(--bg-color) !important;
    background-image: radial-gradient(circle at 2px 2px, rgba(0,0,0,0.02) 1px, transparent 0);
    background-size: 24px 24px;
}}

/* Glassmorphism Card Judicial */
.glass-card {{
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-top: 4px solid var(--gold-accent);
    border-radius: 12px;
    padding: 1.8rem;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}}

.main-title {{
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--gold-accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
    animation: fadeIn 1s ease-out;
}}



@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Improved Sidebar Judicial con Letras Negras */
[data-testid="stSidebar"] {{
    background-color: #f8fafc !important;
    border-right: 1px solid var(--gold-accent);
}}

[data-testid="stSidebar"] * {{
    color: #000000 !important;
}}

/* Custom Buttons */
.stButton>button {{
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    font-weight: 600 !important;
    border: 1px solid var(--border-color) !important;
    color: #000000 !important;
}}

.stButton>button:hover {{
    border-color: var(--gold-accent) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}}

/* Tooltip style for tutorial con Letras Negras */
.tutorial-box {{
    background: #ffffff;
    color: #000000 !important;
    padding: 1.8rem;
    border-radius: 12px;
    position: relative;
    margin-bottom: 1.5rem;
    box-shadow: 0 15px 40px rgba(0,0,0,0.1);
    border-left: 6px solid var(--gold-accent);
    animation: slideInUp 0.5s ease-out;
    border: 1px solid var(--border-color);
}}

.tutorial-box * {{
    color: #000000 !important;
}}



@keyframes slideInUp {{
    from {{ transform: translateY(20px); opacity: 0; }}
    to {{ transform: translateY(0); opacity: 1; }}
}}

@keyframes bounce {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-8px); }}
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
    overflow: hidden;
}}

.card_black_border {{
    background: var(--card-bg);
    border: 1px solid rgba(37, 99, 235, 0.22);
    border-radius: 18px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
}}

/* Fix for File Uploader text overlap */
[data-testid="stFileUploader"] section {{
    padding: 1rem !important;
}}

[data-testid="stFileUploader"] label {{
    margin-bottom: 0.5rem !important;
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
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}}

/* Fix for Selectbox arrow alignment */
.stSelectbox [data-testid="stMarkdownContainer"] {{
    line-height: 1.5 !important;
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
