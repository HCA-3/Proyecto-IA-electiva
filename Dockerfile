# Utilizar una imagen base de Python oficial
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y asegurar que los logs se muestren en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema (Tesseract OCR y librerías para Pillow/PDF)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto que usará Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación respetando el puerto de Render
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
