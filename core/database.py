"""
core/database.py
----------------
Manages persistent storage for the Triage Dashboard.
Saves analyzed cases in a local JSON file so they don't disappear when the app restarts.
Includes folder management and search/filter support.
"""

import json
import os
from datetime import datetime
from typing import Any

DB_PATH = "data"
DB_FILE = os.path.join(DB_PATH, "cases.json")
FOLDERS_FILE = os.path.join(DB_PATH, "folders.json")
ORGANIZED_PATH = os.path.join(DB_PATH, "organized")

def _ensure_db() -> None:
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(FOLDERS_FILE):
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(ORGANIZED_PATH):
        os.makedirs(ORGANIZED_PATH)
    
    # Asegurar subcarpetas por categoría
    for cat in ["Civil", "Familia", "Laboral", "Penal", "Administrativo", "Otros"]:
        cat_path = os.path.join(ORGANIZED_PATH, cat)
        if not os.path.exists(cat_path):
            os.makedirs(cat_path)

# ------------------------------------------------------------------
# Carpetas
# ------------------------------------------------------------------

def load_folders(owner: str) -> list[str]:
    """Carga las carpetas del usuario."""
    _ensure_db()
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            all_folders = json.load(f)
        return all_folders.get(owner, ["Sin carpeta"])
    except Exception:
        return ["Sin carpeta"]

def save_folder(owner: str, folder_name: str) -> None:
    """Crea una nueva carpeta para el usuario si no existe."""
    _ensure_db()
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            all_folders = json.load(f)
    except Exception:
        all_folders = {}

    if owner not in all_folders:
        all_folders[owner] = ["Sin carpeta"]

    if folder_name not in all_folders[owner]:
        all_folders[owner].append(folder_name)

    with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_folders, f, indent=4, ensure_ascii=False)

def delete_folder(owner: str, folder_name: str) -> None:
    """Elimina una carpeta (los casos quedan en 'Sin carpeta')."""
    _ensure_db()
    if folder_name == "Sin carpeta":
        return
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            all_folders = json.load(f)
    except Exception:
        all_folders = {}

    if owner in all_folders and folder_name in all_folders[owner]:
        all_folders[owner].remove(folder_name)
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_folders, f, indent=4, ensure_ascii=False)

    # Mover los casos de esa carpeta a "Sin carpeta"
    cases = load_triage_cases()
    changed = False
    for case in cases:
        if case.get("Owner") == owner and case.get("Carpeta") == folder_name:
            case["Carpeta"] = "Sin carpeta"
            changed = True
    if changed:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)

def update_folder_name(owner: str, old_name: str, new_name: str) -> None:
    """Renombra una carpeta y actualiza todos sus documentos."""
    _ensure_db()
    if old_name == "Sin carpeta" or not new_name.strip():
        return
    
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            all_folders = json.load(f)
    except Exception:
        return

    if owner in all_folders and old_name in all_folders[owner]:
        idx = all_folders[owner].index(old_name)
        all_folders[owner][idx] = new_name
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_folders, f, indent=4, ensure_ascii=False)

    # Actualizar carpetas en los casos
    cases = load_triage_cases()
    changed = False
    for case in cases:
        if case.get("Owner") == owner and case.get("Carpeta") == old_name:
            case["Carpeta"] = new_name
            changed = True
    if changed:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)

def assign_case_to_folder(filename: str, owner: str, folder_name: str) -> None:
    """Asigna un caso existente a una carpeta."""
    cases = load_triage_cases()
    for case in cases:
        if case.get("Archivo") == filename and case.get("Owner") == owner:
            case["Carpeta"] = folder_name
            break
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)

# ------------------------------------------------------------------
# Casos
# ------------------------------------------------------------------

def load_triage_cases() -> list[dict[str, Any]]:
    """Loads all saved cases from the JSON file."""
    _ensure_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def delete_case(filename: str, owner: str) -> None:
    """Elimina un caso específico de la base de datos."""
    cases = load_triage_cases()
    initial_len = len(cases)
    cases = [c for c in cases if not (c.get("Archivo") == filename and c.get("Owner") == owner)]
    if len(cases) < initial_len:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)

def update_case_metadata(filename: str, owner: str, new_metadata: dict) -> None:
    """Actualiza los metadatos de un caso específico."""
    cases = load_triage_cases()
    changed = False
    for case in cases:
        if case.get("Archivo") == filename and case.get("Owner") == owner:
            case.update(new_metadata)
            changed = True
            break
    if changed:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)

def save_triage_case(case: dict[str, Any], owner: str, folder: str = "Sin carpeta") -> None:
    """Guarda un caso analizado asignándole un dueño (usuario) y una carpeta."""
    _ensure_db()
    case["Owner"] = owner
    if "Carpeta" not in case:
        case["Carpeta"] = folder
    if "Fecha" not in case:
        case["Fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    cases = load_triage_cases()
    existing_idx = -1
    for i, c in enumerate(cases):
        if c.get("Archivo") == case.get("Archivo") and c.get("Owner") == owner:
            existing_idx = i
            break

    if existing_idx >= 0:
        cases[existing_idx] = case
    else:
        cases.append(case)

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)


CONFIG_FILE = os.path.join(DB_PATH, "config.json")

def load_api_key() -> str:
    """Carga la clave API almacenada localmente, si existe."""
    _ensure_db()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                return config_data.get("groq_api_key", "")
        except:
            return ""
    return ""

def save_api_key(api_key: str) -> None:
    """Guarda la clave API localmente."""
    _ensure_db()
    config_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except:
            pass

    config_data["groq_api_key"] = api_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def update_case_chat(filename: str, message: dict[str, str]) -> None:
    """Añade un mensaje al historial de chat de un caso específico."""
    cases = load_triage_cases()
    for case in cases:
        if case.get("Archivo") == filename:
            if "Chat" not in case:
                case["Chat"] = []
            case["Chat"].append(message)
            break
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)

def update_case_chat_bulk(filename: str, messages: list[dict[str, str]]) -> None:
    """Añade múltiples mensajes de chat en una sola escritura a disco (más eficiente)."""
    cases = load_triage_cases()
    for case in cases:
        if case.get("Archivo") == filename:
            if "Chat" not in case:
                case["Chat"] = []
            case["Chat"].extend(messages)
            break
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)


def toggle_training_flag(filename: str, owner: str, flag: bool) -> None:
    """Marca o desmarca un caso para entrenamiento futuro."""
    cases = load_triage_cases()
    found = False
    for case in cases:
        if case.get("Archivo") == filename and case.get("Owner") == owner:
            case["training_ready"] = flag
            found = True
            break

    if found:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)


def mock_rama_judicial_search(radicado: str) -> dict[str, Any]:
    """
    Simula una búsqueda en la API de la Rama Judicial.
    Para fines académicos, devuelve metadatos ficticios basados en el número.
    """
    import random
    # Simulamos latencia
    import time
    time.sleep(1.5)
    
    categories = ["Civil", "Familia", "Laboral", "Penal", "Administrativo"]
    category = random.choice(categories)
    
    return {
        "radicado": radicado,
        "despacho": f"Juzgado {random.randint(1,50)} {category} del Circuito",
        "demandante": "Buscando en Registro...",
        "demandado": "Buscando en Registro...",
        "tipo": category,
        "estado": "En Trámite",
        "ultima_actuacion": "Auto que admite demanda",
        "url_mock": f"https://mock-rama.gov.co/expediente/{radicado}.pdf"
    }
