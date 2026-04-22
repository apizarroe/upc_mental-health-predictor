# Backend ML API — Mental Health Predictor

Microservicio FastAPI para predicción de depresión y ansiedad usando RoBERTa Biomedical + Logistic Regression, con transcripción de audio vía Faster-Whisper.

## Requisitos

- Python 3.11 o 3.12
- ~2 GB de espacio (modelo RoBERTa ~500 MB)

## Instalación

```bash
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Entrenamiento del modelo

Debe ejecutarse una vez antes de iniciar la API. Los modelos se guardan en `data/trained_models/`.

```bash
# Paso 1: etiquetar el dataset
python scripts/cluster_and_label.py

# Paso 2: entrenar (descarga RoBERTa ~500 MB la primera vez, ~20-60 min en CPU)
python scripts/train.py
```

## Iniciar la API

```bash
run_api.bat              # Windows
./run_api.sh             # Linux / Git Bash
```

Disponible en `http://localhost:8000` · Docs en `/docs`

## Validar el modelo

```bash
# Texto libre
python scripts/test.py --text "Me siento muy triste y sin energía"

# Conversaciones aleatorias del dataset
python scripts/test.py --random 10

# Evaluación completa
python scripts/test.py --full-test
```

## Estructura

```
backend/
├── app/
│   ├── main.py                    # FastAPI + middleware
│   ├── api/routes/                # Endpoints (prediction, health, transcription)
│   ├── api/schemas/               # Pydantic models
│   ├── core/dependencies.py       # Inyección del pipeline (singleton)
│   ├── ml/                        # Módulo ML (ver app/ml/README.md)
│   └── services/transcription.py  # Lógica de Faster-Whisper
├── scripts/
│   ├── cluster_and_label.py       # Etiquetado del dataset
│   ├── train.py                   # Entrenamiento
│   └── test.py                    # Validación
├── data/
│   ├── datasets/                  # Dataset fuente (.parquet)
│   └── trained_models/            # Modelos entrenados (.pkl + metadata .json)
└── requirements.txt
```

## Documentación

- [API Reference](app/api/docs/README.md) — endpoints, request/response, ejemplos
- [Módulo ML](app/ml/docs/README.md) — arquitectura, pipeline, keywords, modelo
- [Guía de Entrenamiento](scripts/docs/README.md) — pasos, parámetros, métricas, troubleshooting

## Variables de entorno

Ver `.env.example`. Las principales:

| Variable | Default | Descripción |
|---|---|---|
| `API_PORT` | `8000` | Puerto del servidor |
| `WHISPER_MODEL` | `small` | Modelo de transcripción |
| `DEVICE` | auto | `cpu` o `cuda` |
