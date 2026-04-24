"""
core/groq_client.py
-------------------
Cliente API para comunicarse con Groq Cloud (proveedor gratuito y ultra-rápido).
Reemplaza la funcionalidad local de Ollama.
"""

from __future__ import annotations

import os
from typing import Any
from groq import Groq
import streamlit as st
import config

class GroqClient:
    """
    Cliente para interactuar con la API REST de Groq.
    """

    # Modelos recomendados de Groq que siempre están disponibles
    _MODELS = [
        "llama-3.1-8b-instant",        # Recomendado por ser más ligero y rápido (menos propenso a Rate Limit)
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "deepseek-r1-distill-llama-70b",
        "llama3-8b-8192",
        "llama3-70b-8192",
    ]

    def __init__(self, api_key: str | None = None) -> None:
        """Inicializa validando si hay una API KEY."""
        self._api_key = api_key or st.session_state.get("groq_api_key", "")
        if self._api_key:
            try:
                self.client = Groq(api_key=self._api_key)
            except Exception:
                self.client = None
        else:
            self.client = None

    def set_api_key(self, api_key: str) -> None:
        """Actualiza la clave de API en tiemp de ejecución."""
        self._api_key = api_key.strip()
        st.session_state["groq_api_key"] = self._api_key
        try:
            self.client = Groq(api_key=self._api_key)
        except Exception:
            self.client = None

    # ------------------------------------------------------------------
    # Conectividad
    # ------------------------------------------------------------------

    def check_connection(self) -> tuple[bool, list[str]]:
        """
        Verifica si la API KEY es válida haciendo una consulta rápida.
        """
        if not self.client:
            return False, self._MODELS
            
        try:
            # Validamos enumerando los modelos permitidos en Groq
            _ = self.client.models.list()
            return True, self._MODELS
        except Exception:
            return False, self._MODELS

    @property
    def is_connected(self) -> bool:
        """Verdadero si el cliente de Groq puede autenticarse."""
        connected, _ = self.check_connection()
        return connected

    # ------------------------------------------------------------------
    # Generación
    # ------------------------------------------------------------------

    def generate(self, prompt: str, model: str, timeout: int | None = None) -> str:
        """
        Envía un prompt al modelo indicado en la nube de Groq.
        Incluye reintentos automáticos cuando se alcanza el límite de tokens por minuto (TPM).
        """
        import time
        import re

        if not self.client:
            raise RuntimeError("API Key de Groq no configurada. Añádela en la barra lateral.")

        max_retries = 4
        for attempt in range(max_retries):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=model,
                    temperature=0.1,  # Bajo para mayor precisión legal
                    max_tokens=800,   # Limitar respuesta para ahorrar tokens
                )
                return chat_completion.choices[0].message.content.strip()

            except Exception as exc:
                error_msg = str(exc)
                # Detectar error de Rate Limit (TPM o TPD)
                if "rate_limit_exceeded" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        # Extraer tiempo de espera del mensaje de error
                        wait_match = re.search(r'try again in (\d+(?:\.\d+)?)s', error_msg)
                        wait_seconds = float(wait_match.group(1)) if wait_match else (10 * (attempt + 1))
                        wait_seconds = min(wait_seconds + 2, 60)  # Añadir 2s de margen, máximo 60s
                        time.sleep(wait_seconds)
                        continue  # Reintentar
                    else:
                        raise RuntimeError(
                            f"⏳ Límite de velocidad de Groq alcanzado. "
                            f"El sistema esperó pero no pudo completar la solicitud. "
                            f"Por favor, intenta con un documento más corto o espera unos minutos.\n\nDetalle técnico: {exc}"
                        )
                raise RuntimeError(f"Error en la API de Groq: {exc}")

    def generate_vision(self, prompt: str, image_bytes: bytes, model: str = "llama-3.2-11b-vision-preview") -> str:
        """
        Envía una imagen a Groq para extraer texto o analizar contenido.
        """
        import base64
        if not self.client:
            raise RuntimeError("API Key de Groq no configurada.")

        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=model,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"Error en Vision API de Groq: {exc}")

    def transcribe(self, audio_file: Any) -> str:
        """
        Transcribe un archivo de audio (mp3, wav, m4a, etc.) usando Whisper en Groq.
        """
        if not self.client:
            raise RuntimeError("API Key de Groq no configurada.")
            
        try:
            # Groq soporta whisper-large-v3 para transcripción
            transcription = self.client.audio.transcriptions.create(
                file=(audio_file.name, audio_file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="es", # Forzamos español para procesos judiciales
            )
            return transcription
        except Exception as exc:
            raise RuntimeError(f"Error en transcripción de audio: {exc}")

