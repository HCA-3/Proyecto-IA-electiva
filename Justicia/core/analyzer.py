"""
core/analyzer.py
----------------
Clase DocumentAnalyzer: orquesta el análisis de texto técnico-legal enfocado en
la generación de borradores de sentencias, resúmenes de expedientes y análisis de pruebas.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import streamlit as st

import config
from core.groq_client import GroqClient


@dataclass
class AnalysisResult:
    """Resultado del análisis enfocado en decisiones judiciales y pruebas."""
    model: str
    final_report: str # Contiene el resumen y la propuesta de sentencia
    evidence_analysis: str = "" # Nuevo campo para análisis de pruebas
    process_type: str = "Otros" # Categoría del proceso (Civil, Familia, etc.)
    partial_summaries: list[str] = field(default_factory=list)
    parts_analyzed: int = 0
    duration: float = 0.0 # Tiempo total en segundos
    estimated_cost: float = 0.0 # Costo proyectado (ej. vs OpenAI)
    errors: list[str] = field(default_factory=list)

    def to_text(self, filename: str) -> str:
        """Genera un texto exportable con el informe completo."""
        separator = "=" * 60
        return (
            f"INFORME JUDICIAL — JUSTICIA IA\n"
            f"Expediente       : {filename}\n"
            f"Modelo IA        : {self.model}\n\n"
            f"{separator}\n"
            f"1. RESUMEN Y PROPUESTA DE DECISIÓN\n"
            f"{separator}\n\n"
            f"{self.final_report}\n\n"
            f"{separator}\n"
            f"2. ANÁLISIS DE PRUEBAS Y HECHOS\n"
            f"{separator}\n\n"
            f"{self.evidence_analysis}\n"
        )

    def to_pdf(self, filename: str) -> bytes:
        """Exporta el reporte en formato PDF."""
        from fpdf import FPDF
        
        class ReportPDF(FPDF):
            def header(self):
                self.set_font("helvetica", "B", 14)
                self.cell(0, 10, "ASISTENTE JUDICIAL - JUSTICIA IA", align="C", new_x="LMARGIN", new_y="NEXT")
                self.set_font("helvetica", "", 10)
                fname_clean = filename.encode('latin-1', 'replace').decode('latin-1')
                self.cell(0, 10, f"Expediente: {fname_clean}", align="C", new_x="LMARGIN", new_y="NEXT")
                self.line(10, 30, 200, 30)
                self.ln(10)
                
            def footer(self):
                self.set_y(-15)
                self.set_font("helvetica", "I", 8)
                self.cell(0, 10, f"Página {self.page_no()}", align="C")

        pdf = ReportPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # 1. Resumen y Propuesta
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "1. RESUMEN Y PROPUESTA DE SENTENCIA", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 10)
        report_text = self.final_report.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, report_text)
        pdf.ln(10)

        # 2. Análisis de Pruebas
        pdf.add_page()
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "2. ANÁLISIS DE PRUEBAS Y ELEMENTOS PROBATORIOS", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "", 10)
        evid_text = self.evidence_analysis.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, evid_text)
        
        return bytes(pdf.output())


class DocumentAnalyzer:
    """
    Orquesta el análisis para generar borradores de decisiones judiciales.
    """

    _PARTIAL_PROMPT_TEMPLATE = """\
Eres un relator judicial experto. Tu tarea es extraer la esencia jurídica de este fragmento de expediente.
IMPORTANTE: Sé extremadamente preciso con las FECHAS y NOMBRES. Si una fecha no es clara, NO la inventes; indica "[Fecha por verificar]".

Enfócate en:
- Cronología de hechos (Fechas exactas).
- Pruebas mencionadas (documentales, testimoniales, periciales).
- Normas o leyes citadas.
- Pretensiones de las partes.

Fragmento del documento:
{text}"""

    _FINAL_PROMPT_TEMPLATE = """\
Actúa como un Magistrado de alta corte. Basándote en la síntesis del expediente judicial proporcionada, genera un informe estructurado que sirva de borrador para una decisión judicial o sentencia.

REGLAS DE ORO:
1. Cronología Estricta: Si mencionas fechas, deben aparecer en los resúmenes parciales. 
2. No Alucinar: Si hay vacíos de información, indícalo explícitamente.
3. Estilo Judicial: Mantén un lenguaje formal, técnico y objetivo.

Responde EXACTAMENTE con este formato Markdown:

### 📥 1. Resumen Ejecutivo del Caso
[Resume los hechos principales, las partes involucrados y el conflicto jurídico central. Incluye una cronología resumida si es posible]

### ⚖️ 2. Consideraciones y Fundamentos Jurídicos
[Analiza cómo se aplica la ley a los hechos encontrados. Cita principios o normas si fueron detectados en el texto]

### 📜 3. Propuesta de Decisión / Resolución (Sentencia)
[Redacta una propuesta formal de la parte resolutiva del fallo basándote en la información disponible]

### ⚠️ 6. Evaluación Crítica de la IA (Riesgos y Verificación)
[Analiza posibles riesgos de alucinación en FECHAS o DATOS. Indica qué partes del texto original debe revisar el juez con prioridad]

---

### 📝 Resúmenes Parciales del Expediente:
{combined}"""

    _EVIDENCE_PROMPT_TEMPLATE = """\
Analiza exclusivamente el material probatorio mencionado en los siguientes resúmenes del expediente judicial. 
Tu objetivo es identificar la fuerza de las pruebas, posibles contradicciones y su relevancia para el fallo.
IMPORTANTE: Cruza las FECHAS de las pruebas con la cronología de los hechos.

Responde EXACTAMENTE con este formato Markdown:

### 🔍 4. Análisis Detallado de Pruebas
- **Pruebas Documentales**: [Listado, fechas e impacto]
- **Testimonios/Peritajes**: [Relevancia]
- **Valoración Probatoria**: [Análisis de la validez o fuerza de las pruebas]

### ⚠️ 5. Vacíos Probatorios o Contradicciones
[Identifica qué falta o qué se contradice en el expediente, especialmente inconsistencias cronológicas]

Contexto para análisis de pruebas:
{combined}"""

    def __init__(
        self,
        client: GroqClient,
        progress_cb: Callable[[float, str], None] | None = None,
    ) -> None:
        self._client = client
        self._progress_cb = progress_cb or (lambda val, msg: None)

    def analyze(
        self,
        text: str,
        model: str,
        chunk_size: int = config.DEFAULT_CHUNK_SIZE,
        max_parts: int = config.DEFAULT_MAX_PARTS,
    ) -> AnalysisResult:
        start_time = time.time()
        truncated_text = text[: config.MAX_TEXT_LENGTH]
        chunks = self._split_text(truncated_text, chunk_size, max_parts)

        partial_summaries: list[str] = []
        errors: list[str] = []
        # Pasos: chunks + sintesis + pruebas
        total_steps = len(chunks) + 2 

        for i, chunk in enumerate(chunks):
            self._progress_cb(i / total_steps, f"📖 Procesando folio {i + 1} de {len(chunks)}...")
            try:
                summary = self._analyze_chunk(chunk, model)
                partial_summaries.append(summary)
            except RuntimeError as exc:
                partial_summaries.append(f"[Error: {exc}]")
                errors.append(str(exc))
            time.sleep(0.1)

        combined = "\n\n".join(partial_summaries)
        # Truncar para que el prompt de síntesis no supere el límite TPM de Groq
        combined_trimmed = combined[:2000]

        # 1. Síntesis y Propuesta de Sentencia
        self._progress_cb((len(chunks)) / total_steps, "✍️ Redactando propuesta de sentencia...")
        final_report = self._synthesize(combined_trimmed, model)

        # 2. Análisis de Pruebas (Apartado separado)
        self._progress_cb((len(chunks) + 1) / total_steps, "🔎 Realizando análisis detallado de pruebas...")
        evidence_analysis = self._analyze_evidence(combined_trimmed, model)

        # 3. Categorización del Proceso
        self._progress_cb(1.0, "🗂️ Categorizando tipo de proceso...")
        process_type = self._detect_process_type(combined_trimmed, model)


        self._progress_cb(1.0, "✅ Documento analizado integralmente")
        
        duration = time.time() - start_time
        # Estimación simple de costo (asumiendo 0.5 USD por 1M tokens vs OpenAI)
        tokens_est = len(text.split()) * 1.3 
        cost_est = (tokens_est / 1_000_000) * 0.5 

        return AnalysisResult(
            model=model,
            final_report=final_report,
            evidence_analysis=evidence_analysis,
            process_type=process_type,
            partial_summaries=partial_summaries,
            parts_analyzed=len(chunks),
            duration=round(duration, 2),
            estimated_cost=round(cost_est, 4),
            errors=errors,
        )

    def _split_text(self, text: str, chunk_size: int, max_parts: int) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text) and len(chunks) < max_parts:
            end = min(start + chunk_size, len(text))
            if end < len(text):
                natural_cut = text.rfind("\n", start, end)
                if natural_cut > start:
                    end = natural_cut
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        return chunks

    def _analyze_chunk(self, chunk: str, model: str) -> str:
        prompt = self._PARTIAL_PROMPT_TEMPLATE.format(text=chunk)
        return self._client.generate(prompt=prompt, model=model)

    def _synthesize(self, combined: str, model: str) -> str:
        prompt = self._FINAL_PROMPT_TEMPLATE.format(combined=combined)
        try:
            return self._client.generate(prompt=prompt, model=model)
        except Exception as exc:
            return f"Error en redacción: {exc}"

    def _analyze_evidence(self, combined: str, model: str) -> str:
        prompt = self._EVIDENCE_PROMPT_TEMPLATE.format(combined=combined)
        try:
            return self._client.generate(prompt=prompt, model=model)
        except Exception as exc:
            return f"Error en análisis de pruebas: {exc}"

    def _detect_process_type(self, combined: str, model: str) -> str:
        prompt = f"""
        Analiza el siguiente extracto de expediente judicial y categorízalo EXACTAMENTE en una de estas categorías:
        - Civil
        - Familia
        - Laboral
        - Penal
        - Administrativo
        - Otros
        
        Responde SOLO con la categoría.
        
        Texto: {combined[:1500]}
        """
        try:
            res = self._client.generate(prompt=prompt, model=model).strip().replace(".", "")
            valid = ["Civil", "Familia", "Laboral", "Penal", "Administrativo", "Otros"]
            for v in valid:
                if v.lower() in res.lower():
                    return v
            return "Otros"
        except:
            return "Otros"
