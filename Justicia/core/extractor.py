"""
core/extractor.py
-----------------
Clase DocumentExtractor: extrae texto de archivos PDF e imágenes y gestiona el guardado local.
Separa completamente la lógica de extracción de la interfaz de usuario.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import BinaryIO, Callable

import pdfplumber
from PIL import Image
import pytesseract


@dataclass
class ExtractionResult:
    """Resultado de la extracción de texto de un documento."""
    text: str
    num_pages: int | None = None
    source_type: str = "unknown"   # "pdf" | "image"
    local_path: str | None = None  # Ruta al archivo guardado localmente
    warnings: list[str] = field(default_factory=list)


class DocumentExtractor:
    """
    Extrae texto de documentos PDF e imágenes y guarda una copia local en 'data/raw_documents'.
    """

    _OCR_LANGUAGES: str = "spa+eng"
    _RAW_DOCS_PATH: str = os.path.join("data", "raw_documents")

    def __init__(self) -> None:
        if not os.path.exists(self._RAW_DOCS_PATH):
            os.makedirs(self._RAW_DOCS_PATH)

    def extract(self, file: BinaryIO, mime_type: str, progress_cb: Callable[[float, str], None] | None = None) -> ExtractionResult:
        self._progress_cb = progress_cb or (lambda p, m: None)
        
        # Primero guardamos una copia local
        filename = getattr(file, "name", "documento_desconocido")
        local_path = self.save_locally(file, filename)
        
        # Reposicionamos el puntero del archivo para la lectura
        file.seek(0)
        
        if mime_type == "application/pdf":
            result = self._extract_pdf(file)
        elif mime_type.startswith("image/"):
            result = self._extract_image(file)
        elif "wordprocessingml.document" in mime_type or "word" in mime_type:
            result = self._extract_docx(file)
        else:
            raise ValueError(f"Tipo de archivo no soportado: '{mime_type}'")
            
        result.local_path = local_path
        return result

    def save_locally(self, file: BinaryIO, filename: str) -> str:
        """Guarda el archivo subido en el disco local para persistencia física."""
        path = os.path.join(self._RAW_DOCS_PATH, filename)
        with open(path, "wb") as f:
            f.write(file.read())
        return path

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------
    
    def _extract_docx(self, file: BinaryIO) -> ExtractionResult:
        import docx
        try:
            doc = docx.Document(file)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as exc:
            raise RuntimeError(f"Error al leer el archivo Word: {exc}") from exc

        return ExtractionResult(
            text=full_text,
            source_type="docx"
        )

    def _extract_pdf(self, file: BinaryIO) -> ExtractionResult:
        """Extrae texto de un PDF página a página con pdfplumber."""
        lines: list[str] = []
        warnings: list[str] = []

        try:
            with pdfplumber.open(file) as pdf:
                num_pages = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    self._progress_cb((i + 1) / num_pages * 0.4, f"Leyendo página {i+1} de {num_pages}...")
                    page_text = page.extract_text()
                    if page_text:
                        lines.append(page_text)
                    else:
                        warnings.append(f"Página {i + 1} no contiene texto seleccionable.")
        except Exception as exc:
            raise RuntimeError(f"Error al leer el PDF: {exc}") from exc

        full_text = "\n".join(lines).strip()
        return ExtractionResult(
            text=full_text,
            num_pages=num_pages,
            source_type="pdf",
            warnings=warnings,
        )

    def _extract_image(self, file: BinaryIO) -> ExtractionResult:
        """Extrae texto de una imagen mediante OCR (Tesseract)."""
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image, lang=self._OCR_LANGUAGES)
        except Exception as exc:
            raise RuntimeError(f"Error al procesar la imagen con OCR: {exc}") from exc

        return ExtractionResult(
            text=text.strip(),
            source_type="image",
        )
