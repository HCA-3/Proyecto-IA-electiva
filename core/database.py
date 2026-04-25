"""
core/database.py
----------------
Capa de persistencia dual para Justicia IA.

- MODO LOCAL  : Usa archivos JSON en data/ (desarrollo y ejecución local).
- MODO CLOUD  : Usa MongoDB Atlas cuando existe la variable de entorno MONGODB_URI.
                Render la inyecta automáticamente en producción.

El resto de la aplicación NO necesita saber qué backend está activo;
la interfaz pública de funciones es idéntica en ambos modos.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Detección automática de entorno
# ──────────────────────────────────────────────────────────────────────────────

MONGODB_URI: str | None = os.getenv("MONGODB_URI")
USE_MONGO: bool = bool(MONGODB_URI)

# ──────────────────────────────────────────────────────────────────────────────
# BACKEND: MongoDB Atlas
# ──────────────────────────────────────────────────────────────────────────────

if USE_MONGO:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    import certifi

    try:
        _mongo_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            tlsCAFile=certifi.where(),   # Certificados SSL actualizados (fix para Python 3.12+)
        )
        # Verificar conexión real al iniciar
        _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client["justicia_ia"]
        _MONGO_OK = True
        print("[INFO] MongoDB Atlas conectado correctamente.")
    except Exception as _mongo_err:
        import sys
        print(f"[WARNING] MongoDB no disponible: {_mongo_err}. Usando almacenamiento local.", file=sys.stderr)
        _MONGO_OK = False
        USE_MONGO = False

    def _col(name: str) -> "Collection":
        """Devuelve la colección MongoDB indicada."""
        return _mongo_db[name]


# ──────────────────────────────────────────────────────────────────────────────
# BACKEND: JSON local  (rutas de archivos)
# ──────────────────────────────────────────────────────────────────────────────

DB_PATH = "data"
DB_FILE = os.path.join(DB_PATH, "cases.json")
FOLDERS_FILE = os.path.join(DB_PATH, "folders.json")
ORGANIZED_PATH = os.path.join(DB_PATH, "organized")
CONFIG_FILE = os.path.join(DB_PATH, "config.json")
SEARCHES_FILE = os.path.join(DB_PATH, "searches.json")


def _ensure_db() -> None:
    """Inicializa el sistema de archivos local si hace falta."""
    if USE_MONGO:
        return  # MongoDB no necesita estructura de carpetas local
    os.makedirs(DB_PATH, exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(FOLDERS_FILE):
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    os.makedirs(ORGANIZED_PATH, exist_ok=True)
    for cat in ["Civil", "Familia", "Laboral", "Penal", "Administrativo", "Otros"]:
        os.makedirs(os.path.join(ORGANIZED_PATH, cat), exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CARPETAS
# ══════════════════════════════════════════════════════════════════════════════

def load_folders(owner: str) -> list[str]:
    """Carga las carpetas del usuario."""
    if USE_MONGO:
        doc = _col("folders").find_one({"owner": owner})
        return doc["folders"] if doc else ["Sin carpeta"]

    _ensure_db()
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get(owner, ["Sin carpeta"])
    except Exception:
        return ["Sin carpeta"]


def save_folder(owner: str, folder_name: str) -> None:
    """Crea una nueva carpeta para el usuario si no existe."""
    if USE_MONGO:
        current = load_folders(owner)
        if folder_name not in current:
            current.append(folder_name)
            _col("folders").update_one(
                {"owner": owner},
                {"$set": {"folders": current}},
                upsert=True,
            )
        return

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
    if folder_name == "Sin carpeta":
        return

    if USE_MONGO:
        current = load_folders(owner)
        if folder_name in current:
            current.remove(folder_name)
            _col("folders").update_one({"owner": owner}, {"$set": {"folders": current}})
        # Mover casos huérfanos
        _col("cases").update_many(
            {"Owner": owner, "Carpeta": folder_name},
            {"$set": {"Carpeta": "Sin carpeta"}},
        )
        return

    _ensure_db()
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            all_folders = json.load(f)
    except Exception:
        all_folders = {}
    if owner in all_folders and folder_name in all_folders[owner]:
        all_folders[owner].remove(folder_name)
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_folders, f, indent=4, ensure_ascii=False)
    # Mover casos huérfanos
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
    if old_name == "Sin carpeta" or not new_name.strip():
        return

    if USE_MONGO:
        current = load_folders(owner)
        if old_name in current:
            idx = current.index(old_name)
            current[idx] = new_name
            _col("folders").update_one({"owner": owner}, {"$set": {"folders": current}})
        _col("cases").update_many(
            {"Owner": owner, "Carpeta": old_name},
            {"$set": {"Carpeta": new_name}},
        )
        return

    _ensure_db()
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
    if USE_MONGO:
        _col("cases").update_one(
            {"Archivo": filename, "Owner": owner},
            {"$set": {"Carpeta": folder_name}},
        )
        return

    cases = load_triage_cases()
    for case in cases:
        if case.get("Archivo") == filename and case.get("Owner") == owner:
            case["Carpeta"] = folder_name
            break
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
#  CASOS
# ══════════════════════════════════════════════════════════════════════════════

def load_triage_cases() -> list[dict[str, Any]]:
    """Carga todos los expedientes."""
    if USE_MONGO:
        docs = list(_col("cases").find({}, {"_id": 0}))
        return docs

    _ensure_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_triage_case(case: dict[str, Any], owner: str, folder: str = "Sin carpeta") -> None:
    """Guarda o actualiza un expediente."""
    case["Owner"] = owner
    if "Carpeta" not in case:
        case["Carpeta"] = folder
    if "Fecha" not in case:
        case["Fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if USE_MONGO:
        # _id no debe guardarse como campo; usamos upsert por Archivo+Owner
        doc = {k: v for k, v in case.items() if k != "_id"}
        _col("cases").update_one(
            {"Archivo": case["Archivo"], "Owner": owner},
            {"$set": doc},
            upsert=True,
        )
        return

    cases = load_triage_cases()
    existing_idx = next(
        (i for i, c in enumerate(cases)
         if c.get("Archivo") == case.get("Archivo") and c.get("Owner") == owner),
        -1,
    )
    if existing_idx >= 0:
        cases[existing_idx] = case
    else:
        cases.append(case)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)


def delete_case(filename: str, owner: str) -> None:
    """Elimina un expediente."""
    if USE_MONGO:
        _col("cases").delete_one({"Archivo": filename, "Owner": owner})
        return

    cases = load_triage_cases()
    initial = len(cases)
    cases = [c for c in cases if not (c.get("Archivo") == filename and c.get("Owner") == owner)]
    if len(cases) < initial:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=4, ensure_ascii=False)


def update_case_metadata(filename: str, owner: str, new_metadata: dict) -> None:
    """Actualiza campos específicos de un expediente."""
    if USE_MONGO:
        _col("cases").update_one(
            {"Archivo": filename, "Owner": owner},
            {"$set": new_metadata},
        )
        return

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


def update_case_chat(filename: str, message: dict[str, str]) -> None:
    """Añade un mensaje al chat de un expediente."""
    update_case_chat_bulk(filename, [message])


def update_case_chat_bulk(filename: str, messages: list[dict[str, str]]) -> None:
    """Añade múltiples mensajes al chat en una sola operación."""
    if USE_MONGO:
        _col("cases").update_one(
            {"Archivo": filename},
            {"$push": {"Chat": {"$each": messages}}},
        )
        return

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
    """Marca o desmarca un expediente para entrenamiento."""
    if USE_MONGO:
        _col("cases").update_one(
            {"Archivo": filename, "Owner": owner},
            {"$set": {"training_ready": flag}},
        )
        return

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


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN (API KEY)
# ══════════════════════════════════════════════════════════════════════════════

def load_api_key() -> str:
    """Carga la clave API de Groq.
    
    Prioridad:
    1. Variable de entorno GROQ_API_KEY (ideal para Render)
    2. MongoDB 'config' (si está en modo cloud)
    3. Archivo local data/config.json
    """
    # 1. Variable de entorno (la más segura en producción)
    env_key = os.getenv("GROQ_API_KEY", "")
    if env_key:
        return env_key

    # 2. MongoDB
    if USE_MONGO:
        doc = _col("config").find_one({"_id": "groq"})
        return (doc or {}).get("groq_api_key", "")

    # 3. JSON local
    _ensure_db()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("groq_api_key", "")
        except Exception:
            return ""
    return ""


def save_api_key(api_key: str) -> None:
    """Guarda la clave API (solo persiste en DB/JSON; la env var es inmutable en runtime)."""
    if USE_MONGO:
        _col("config").update_one(
            {"_id": "groq"},
            {"$set": {"groq_api_key": api_key}},
            upsert=True,
        )
        return

    _ensure_db()
    config_data: dict = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            pass
    config_data["groq_api_key"] = api_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORIAL DE BÚSQUEDAS
# ══════════════════════════════════════════════════════════════════════════════

def save_search_history(query: str, response: str) -> None:
    """Guarda el historial de consultas del buscador legal."""
    entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "consulta": query,
        "respuesta_ia": response,
    }

    if USE_MONGO:
        _col("searches").insert_one({k: v for k, v in entry.items()})
        return

    _ensure_db()
    searches: list = []
    if os.path.exists(SEARCHES_FILE):
        try:
            with open(SEARCHES_FILE, "r", encoding="utf-8") as f:
                searches = json.load(f)
        except Exception:
            searches = []
    searches.append(entry)
    with open(SEARCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(searches, f, indent=4, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════════════════════

def mock_rama_judicial_search(radicado: str) -> dict[str, Any]:
    """Simula una búsqueda en la API de la Rama Judicial (fines académicos)."""
    import random
    import time
    time.sleep(1.5)
    categories = ["Civil", "Familia", "Laboral", "Penal", "Administrativo"]
    category = random.choice(categories)
    return {
        "radicado": radicado,
        "despacho": f"Juzgado {random.randint(1, 50)} {category} del Circuito",
        "demandante": "Buscando en Registro...",
        "demandado": "Buscando en Registro...",
        "tipo": category,
        "estado": "En Trámite",
        "ultima_actuacion": "Auto que admite demanda",
        "url_mock": f"https://mock-rama.gov.co/expediente/{radicado}.pdf",
    }
