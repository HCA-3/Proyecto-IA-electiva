"""
core/ollama_client.py
---------------------
Cliente HTTP para comunicarse con una instancia local de Ollama.
Encapsula toda la lógica de conexión, verificación y generación de respuestas.
"""

from __future__ import annotations

import json
import requests

import config


class OllamaClient:
    """
    Cliente para interactuar con la API REST de Ollama.

    Attributes:
        base_url (str): URL base del servidor Ollama.
    """

    def __init__(self, base_url: str = config.OLLAMA_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Conectividad
    # ------------------------------------------------------------------

    def check_connection(self) -> tuple[bool, list[str]]:
        """
        Verifica si Ollama está corriendo y retorna los modelos disponibles.

        Returns:
            (conectado: bool, modelos: list[str])
        """
        try:
            resp = requests.get(
                f"{self.base_url}/api/tags",
                timeout=config.OLLAMA_HEALTH_TIMEOUT,
            )
            resp.raise_for_status()
            modelos = [m["name"] for m in resp.json().get("models", [])]
            return True, modelos
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False, []
        except Exception:
            return False, []

    @property
    def is_connected(self) -> bool:
        """Verdadero si Ollama responde correctamente."""
        connected, _ = self.check_connection()
        return connected

    # ------------------------------------------------------------------
    # Generación
    # ------------------------------------------------------------------

    def generate(self, prompt: str, model: str, timeout: int | None = None) -> str:
        """
        Envía un prompt al modelo indicado y retorna la respuesta.

        Args:
            prompt:  Texto del prompt.
            model:   Nombre del modelo Ollama (e.g. 'tinyllama').
            timeout: Segundos de espera máximos. Usa el default de config si es None.

        Returns:
            Texto de respuesta del modelo.

        Raises:
            RuntimeError: Si ocurre cualquier error de red o de protocolo.
        """
        if timeout is None:
            timeout = config.OLLAMA_TIMEOUT_FINAL

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Tiempo agotado ({timeout}s) esperando respuesta del modelo '{model}'."
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "No se pudo conectar con Ollama. Asegúrate de que esté corriendo."
            )
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(f"Error HTTP de Ollama ({exc.response.status_code}): {exc}")
        except json.JSONDecodeError:
            raise RuntimeError("Ollama devolvió una respuesta con formato inválido (JSON).")
