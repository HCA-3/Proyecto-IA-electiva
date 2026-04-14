"""
config.py
---------
Constantes globales y configuración de la aplicación Justicia IA.
"""

# --- Ollama ---
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_TIMEOUT_PARTIAL: int = 120   # segundos por fragmento
OLLAMA_TIMEOUT_FINAL: int = 180     # segundos para síntesis final
OLLAMA_HEALTH_TIMEOUT: int = 5      # segundos para verificar conexión

# --- Procesamiento de texto ---
DEFAULT_CHUNK_SIZE: int = 1500      # caracteres por fragmento
DEFAULT_MAX_PARTS: int = 3          # Reducido de 4 a 3 para ahorrar tokens
MAX_TEXT_LENGTH: int = 4500         # Reducido de 6000 a 4500 para evitar Rate Limit

# --- Modelos sugeridos (si Ollama está desconectado) ---
SUGGESTED_MODELS: list[str] = [
    "tinyllama",
    "llama3",
    "llama3.2",
    "mistral",
    "gemma",
    "gemma2",
    "phi3",
    "qwen2",
]

# --- App ---
APP_TITLE: str = "Justicia IA – Análisis de Documentos"
APP_ICON: str = "⚖️"
APP_VERSION: str = "2.0.0"
APP_DESCRIPTION: str = "Análisis inteligente de documentos legales con IA local"

# --- Formatos soportados ---
SUPPORTED_FILE_TYPES: list[str] = ["pdf", "png", "jpg", "jpeg", "docx"]
