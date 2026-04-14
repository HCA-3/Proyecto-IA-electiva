"""
core/vector_db.py
-----------------
Simulación de una base de datos vectorial para Justicia IA.
En un entorno real, aquí conectaríamos con Pinecone o FAISS.
"""

import json
import os
from core.database import load_triage_cases

class MockVectorDB:
    def __init__(self):
        self.cases = load_triage_cases()

    def search_precedents(self, query: str, top_k: int = 2) -> list[dict]:
        """
        Simula una búsqueda vectorial. 
        En producción: Generaría embeddings (vectores) del query y los compararía 
        con Pinecone usando similitud de coseno.
        """
        if not self.cases:
            return []

        # Algoritmo de relevancia simple (Simulación de similitud semántica)
        results = []
        query_words = set(query.lower().split())
        
        for case in self.cases:
            score = 0
            # Analizamos coincidencia en el reporte y extracto
            content = (case.get("Reporte_Extendido", "") + " " + case.get("Archivo", "")).lower()
            
            for word in query_words:
                if len(word) > 3: # Solo palabras significativas
                    if word in content:
                        score += 1
            
            if score > 0:
                results.append((score, case))
        
        # Ordenar por puntaje (relevancia)
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Devolver los top_k casos
        return [res[1] for res in results[:top_k]]

    def get_jurisprudencia_context(self, query: str) -> str:
        """Formatea los resultados para alimentar el contexto de la IA."""
        precedents = self.search_precedents(query)
        if not precedents:
            return "No se encontraron precedentes específicos en el repositorio local."
        
        ctx = "ANTECEDENTES Y JURISPRUDENCIA LOCAL ENCONTRADA:\n"
        for p in precedents:
            ctx += f"- Caso: {p.get('Archivo')}\n"
            ctx += f"  Decisión Sugerida Previa: {p.get('Reporte_Extendido', '')[:300]}...\n\n"
        return ctx
