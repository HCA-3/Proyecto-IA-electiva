#!/usr/bin/env bash
# render-build.sh
# Script para preparar el entorno en Render

# Crear carpetas de almacenamiento (en el plan gratuito estas son efímeras)
mkdir -p data/raw_documents
mkdir -p data/organized/Civil
mkdir -p data/organized/Familia
mkdir -p data/organized/Laboral
mkdir -p data/organized/Penal
mkdir -p data/organized/Administrativo
mkdir -p data/organized/Otros

echo "----------------------------------------"
echo "✅ Estructura de carpetas creada con éxito"
echo "----------------------------------------"
