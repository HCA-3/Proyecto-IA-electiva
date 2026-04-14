# ⚖️ Justicia IA — Asistente Judicial Inteligente.

> Prototipo profesional de IA para el apoyo a la toma de decisiones judiciales, desarrollado para la clase *"Descubrimiento de problemas y diseño de soluciones con IA"*. Optimiza la congestión judicial mediante Triage Inteligente, Organización por Carpetas y un Espacio de Trabajo Conversacional de alto rendimiento.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LPU%20Engine-f55036?logo=groq)
![Security](https://img.shields.io/badge/Privacy-Multi--Tenant-green)

---

## 🎯 Objetivo del Proyecto

Transformar el proceso de análisis de expedientes mediante **IA de Inferencia Ultrarrápida**. El sistema permite organizar el despacho judicial mediante carpetas personalizadas, procesar documentos masivamente y generar borradores técnicos de sentencias y análisis de pruebas en segundos.

---

## ✨ Características Principales (v2.0)

1. **📁 Gestión Organizacional (Carpetas)**:
   - Creación, renombramiento y eliminación de carpetas para organizar expedientes por año, tipo de proceso o despacho.
   - Movimiento dinámico de expedientes entre carpetas.
   - Filtros avanzados por nombre de archivo, carpeta y rango de fecha (Hoy, Semana, Mes).

2. **⚖️ Workspace Judicial 360°**:
   - **Propuesta de Sentencia**: Generación automática de borradores basados en el expediente.
   - **Análisis de Pruebas**: Evaluación técnica de la fuerza probatoria y hechos detectados.
   - **Chat Consultivo**: Preguntas directas al expediente con persistencia total de la conversación.

3. **🎨 Personalización y Accesibilidad**:
   - Soporte para múltiples temas visuales: **Moderno**, **Oscuro Judicial** (para fatiga visual) y **Alto Contraste**.
   - Títulos y descripciones del sistema configurables desde el panel administrativo.

4. **⚡ Resiliencia con Groq LPU**:
   - **Auto-Retry**: Lógica de reintento automático ante errores de *Rate Limit* (429) de la API de Groq con backoff exponencial.
   - Optimización de consumo de tokens para maximizar el procesamiento en cuentas gratuitas.

5. **🔐 Seguridad y Auditoría**:
   - Aislamiento total de datos por usuario (Ownership).
   - Panel de administración con estadísticas de uso, monitor de sistema y métricas de rendimiento.

---

## 🏗️ Arquitectura del Proyecto

```
Justicia/
├── app.py                  # Enrutador principal y aplicación de temas CSS
├── core/                   # Núcleo de Inteligencia y Datos
│   ├── groq_client.py      # Cliente con lógica de reintento automático
│   ├── analyzer.py         # Motores de síntesis jurídica y pruebas
│   └── database.py         # Gestor de JSON (Casos, Carpetas, Configuración)
├── views/                  # Interfaces de Usuario
│   ├── user_panel.py       # Flujo de 3 pasos: Carpeta -> Archivos -> Inicio
│   ├── admin_panel.py      # Gestión de sistema y persistencia de ajustes
│   └── login.py            # Autenticación segura
└── ui/                     # Diseño y Estilos
    ├── styles.py           # CSS Dinámico para temas Claro/Oscuro
    └── components.py       # Sidebar y componentes reutilizables
```

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- **Python 3.11+**
- **Groq API Key** (Obtenla en [console.groq.com](https://console.groq.com))

### Pasos Rápidos

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la plataforma:**
   ```bash
   streamlit run app.py
   ```

3. **Configuración Inicial:**
   - Entra como `admin` para configurar la API Key global o como `usuario` para usar tu propia clave.
   - Crea tu primera carpeta en el panel de carga antes de procesar documentos.

---

## 👥 Cuentas de Demostración

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| **Administrador** | `admin` | `Admin123!` |
| **Funcionario Judicial** | `usuario` | `User123!` |

---

## 🛡️ Aviso Legal

Justicia IA es un **Asistente de Soporte a la Decisión**. Los borradores generados por la IA no son vinculantes. El funcionario judicial humano debe validar, corregir y firmar toda providencia de acuerdo con la ley vigente.
