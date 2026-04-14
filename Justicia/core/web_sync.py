"""
core/web_sync.py
----------------
Simulación de sincronización con la API de la Corte Constitucional.
Permite descargar y procesar lotes de Jurisprudencia por categorías.
"""

import time
import random
from datetime import datetime
from core.database import save_triage_case, save_folder

class JurisprudenciaSync:
    def __init__(self, client):
        self.client = client

    def sync_from_court(self, category: str, quantity: int, progress_callback=None):
        """
        Simula la descarga y procesamiento de sentencias de la web.
        """
        results = []
        for i in range(quantity):
            if progress_callback:
                progress_callback((i / quantity), f"Descargando sentencia {i+1} de la Corte ({category})...")
            
            # Simulamos latencia de red
            time.sleep(1.2)
            
            # Generamos datos ficticios realistas para la Corte Constitucional
            sentencia_id = f"SU-{random.randint(100, 999)}-26" if random.random() > 0.5 else f"T-{random.randint(200, 800)}-26"
            filename = f"Sentencia_{sentencia_id}_{category}.pdf"
            
            # Contenido simulado de alta calidad
            mock_text = f"SENTENCIA {sentencia_id}. MAGISTRADO PONENTE: Dr. Justicia IA. " \
                        f"Tema: Protección de derechos en el ámbito {category}. " \
                        f"Hechos: El accionante solicita el amparo de sus derechos fundamentales. " \
                        f"Resuelve: Conceder el amparo y ordenar la reparación integral."

            # Guardamos en el sistema
            new_case = {
                "Archivo": filename,
                "Modelo": "llama3-8b-8192",
                "Extracto_Texto": mock_text,
                "Reporte_Extendido": f"### ANÁLISIS DE JURISPRUDENCIA ({sentencia_id})\nEsta sentencia ha sido importada automáticamente desde la Corte para fortalecer la base de datos de {category}.",
                "Analisis_Pruebas": f"Tipo de Sentencia: {sentencia_id}\nCorte: Constitucional\nRelevancia: Alta para casos de {category}.",
                "Tipo_Proceso": category,
                "Chat": [],
                "Carpeta": f"Jurisprudencia {category}",
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Owner": "Sincronizador Global"
            }
            
            save_folder("Sincronizador Global", f"Jurisprudencia {category}")
            save_triage_case(new_case, "Sincronizador Global", f"Jurisprudencia {category}")
            results.append(filename)
            
        return results
