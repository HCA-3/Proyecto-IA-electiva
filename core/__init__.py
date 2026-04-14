"""
core/
-----
Módulo central de Justicia IA.
Contiene la lógica de negocio: cliente Ollama, extracción y análisis de documentos.
"""

from .groq_client import GroqClient
from .extractor import DocumentExtractor
from .analyzer import DocumentAnalyzer
from .database import (
    load_triage_cases, save_triage_case, update_case_chat, update_case_chat_bulk,
    load_folders, save_folder, delete_folder, update_folder_name, assign_case_to_folder,
    delete_case, update_case_metadata
)

__all__ = [
    "GroqClient", "DocumentExtractor", "DocumentAnalyzer",
    "load_triage_cases", "save_triage_case", "update_case_chat", "update_case_chat_bulk",
    "load_folders", "save_folder", "delete_folder", "update_folder_name", "assign_case_to_folder",
    "delete_case", "update_case_metadata"
]
