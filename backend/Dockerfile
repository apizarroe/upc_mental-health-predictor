FROM python:3.11-slim

WORKDIR /app

# libgomp1: OpenMP requerido por PyTorch en Linux
# ffmpeg: para procesar audio .webm en el servicio de transcripción
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Instalar PyTorch CPU-only antes que el resto (evita descargar la versión CUDA de ~3 GB)
RUN pip install --no-cache-dir \
    "torch>=2.1.2" \
    --index-url https://download.pytorch.org/whl/cpu

# Instalar el resto de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar el modelo de transformers para eliminar cold start en producción
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
AutoTokenizer.from_pretrained('PlanTL-GOB-ES/roberta-base-biomedical-es'); \
AutoModel.from_pretrained('PlanTL-GOB-ES/roberta-base-biomedical-es')"

# Copiar código fuente y modelo entrenado
COPY app/ ./app/
COPY data/trained_models/ ./data/trained_models/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# 1 worker: el modelo ML es un singleton en memoria; múltiples workers duplicarían la RAM
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
