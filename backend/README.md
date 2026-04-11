# Backend ML API - Mental Health Predictor

Microservicio Python especializado en predicción de trastornos mentales (depresión y ansiedad) usando modelos de Machine Learning y Deep Learning. Implementa un modelo multi-etiqueta con BERT + XGBoost y transcripción de audio con Faster-Whisper.

## Tabla de Contenidos

- [Modelos Implementados](#modelos-implementados)
- [Estructura](#estructura)
- [Instalación](#instalación)
- [Desarrollo](#desarrollo)
- [Testing](#testing)
- [Linting y Formato](#linting-y-formato)
- [Entrenamiento de Modelos](#-entrenamiento-de-modelos)
- [Validación de Modelos](#-validación-de-modelos)
- [Scripts CLI Disponibles](#scripts-cli-disponibles)
- [Endpoints Principales](#endpoints-principales)
- [Variables de Entorno](#variables-de-entorno)
- [Dependencias Principales](#dependencias-principales)
- [Deployment](#deployment)

## Modelos Implementados

- **BERT Multi-label**: `dccuchile/bert-base-spanish-wwm-cased` para embeddings contextuales en español
- **XGBoost Multi-Output**: Clasificador multi-etiqueta para predicción simultánea de depresión y ansiedad
- **Faster-Whisper**: Modelo `small` para transcripción de audio a texto en español
- **PyTorch**: Framework para procesamiento con BERT

## Estructura

```
backend/
├── app/
│   ├── api/            # Endpoints FastAPI
│   ├── models/         # Modelos de base de datos (SQLAlchemy, Pydantic)
│   ├── ml/             # Código de Machine Learning (BERT, XGBoost, pipelines)
│   ├── services/       # Lógica de negocio
│   ├── utils/          # Utilidades
│   ├── config/         # Configuración
│   └── main.py         # Punto de entrada FastAPI
├── scripts/            # Scripts CLI ejecutables
│   ├── train.py        # Entrenamiento de modelos
│   └── test.py         # Validación de modelos
├── data/
│   ├── trained_models/ # Modelos entrenados (.pkl, .json)
│   └── datasets/       # Datasets (parquet, csv)
└── tests/              # Tests unitarios
```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Desarrollo

```bash
# Iniciar servidor de desarrollo
uvicorn app.main:app --reload

# O con configuración personalizada
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- Aplicación: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

## Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con verbose
pytest -v

# Tests con cobertura
pytest --cov=app --cov-report=html

# Test específico
pytest tests/test_models.py::test_bert_prediction
```

## Linting y Formato

```bash
# Formatear código con Ruff
ruff format .

# Linter
ruff check .

# Fix automático de problemas
ruff check --fix .

# Type checking con mypy
mypy app/
```

## 🧠 Entrenamiento de Modelos

Para entrenar nuevos modelos BERT + XGBoost desde cero, consulta la guía detallada:

👉 **[Guía de Entrenamiento](docs/TRAINING_GUIDE.md)**

### Opción recomendada: Scripts wrapper (configuran todo automáticamente)

```bash
cd backend

# Entrenamiento básico (configura variables de entorno automáticamente)
./run_training.sh

# Con parámetros personalizados
./run_training.sh --bert-model bert-base-multilingual-cased --n-estimators 200
```

### Opción manual: Ejecutar directamente

```bash
cd backend
source .venv/bin/activate

# Entrenamiento básico
python scripts/train.py

# Ver todas las opciones
python scripts/train.py --help
```

Una vez entrenados, los modelos se guardan en `data/trained_models/` y están disponibles automáticamente para la API.

**⚠️ Nota para macOS**: Si el script se queda colgado al finalizar, presiona `Ctrl+C`. El modelo ya fue guardado correctamente.

## ✅ Validación de Modelos

Después de entrenar, valida que el modelo funciona correctamente:

### Opción recomendada: Script wrapper

```bash
cd backend

# Testear 5 conversaciones aleatorias (default)
./run_testing.sh

# Testear 10 conversaciones aleatorias
./run_testing.sh --random 10

# Evaluación completa del dataset por defecto
./run_testing.sh --full-test

# Evaluación completa de un dataset específico
./run_testing.sh --full-test --data-path data/datasets/mi_dataset.parquet

# Testear conversaciones específicas
./run_testing.sh --indices 0 5 10 15
```

### Opción manual: Ejecutar directamente

```bash
cd backend
source .venv/bin/activate

# Testear conversaciones aleatorias desde Parquet (usa dataset por defecto)
python scripts/test.py --random 10

# Testear desde archivo CSV
python scripts/test.py --csv --data-path data/datasets/example_patient_messages.csv

# Testear texto personalizado
python scripts/test.py --text "Me siento muy triste y sin energía"

# Evaluación completa del dataset por defecto (data/datasets/train-00000-of-00001.parquet)
python scripts/test.py --full-test

# Evaluación completa de un dataset específico
python scripts/test.py --full-test --data-path data/datasets/mi_dataset.parquet

# Testear conversaciones específicas por índice
python scripts/test.py --indices 0 5 10 15

# Ver todas las opciones
python scripts/test.py --help
```

**Formatos soportados:**
- **Parquet**: Dataset original con conversaciones JSON
- **CSV**: Archivos CSV con columna de sesión (ver `data/datasets/example_patient_messages.csv`)

El script muestra:
- 📊 Probabilidades de depresión
- 🎯 Predicción del modelo
- 🔍 Comparación con heurística de keywords
- 📈 Métricas (accuracy, precision, recall, F1)
- ⚠️ Análisis de falsos positivos/negativos

## Scripts CLI Disponibles

```bash
# Entrenar modelo BERT + XGBoost
python scripts/train.py

# Validar modelo entrenado
python scripts/test.py

# Wrappers automáticos (recomendado)
./run_training.sh  # Configura entorno y entrena
./run_testing.sh   # Configura entorno y valida
```

## Endpoints Principales

Para documentación detallada de cada endpoint, ver [API_README.md](API_README.md).

### Predicción de Salud Mental (Multi-Etiqueta)
```http
POST /api/v1/predict/mental-health
Content-Type: application/json

{
  "patient_id": "PAT-001",
  "answers": {
    "question1": "Respuesta del paciente...",
    "question2": "Respuesta del paciente...",
    "question3": "Respuesta del paciente...",
    "question4": "Respuesta del paciente..."
  }
}
```

**Retorna**: Predicciones para depresión y ansiedad con probabilidades, keywords detectadas y nivel de riesgo.

### Transcripción de Audio
```http
POST /api/v1/audio/transcribe
Content-Type: multipart/form-data

{
  "audio": archivo.wav
}
```

**Retorna**: Texto transcrito del audio usando Faster-Whisper.

### Health Check
```http
GET /api/v1/health
```

### Información del Modelo
```http
GET /api/v1/model/info
```

## Variables de Entorno

Ver `.env.example` para configuración completa.

Principales variables:
- `API_PORT`: Puerto del servidor (default: 8000)
- `API_HOST`: Host del servidor (default: 0.0.0.0)
- `MODEL_PATH`: Ruta al modelo entrenado (default: `data/trained_models/`)
- `WHISPER_MODEL`: Modelo de Whisper (default: `small`)
- `MAX_LENGTH`: Longitud máxima de tokens BERT (default: 512)
- `DEVICE`: Dispositivo de cómputo (cpu, cuda o mps)
- `CORS_ORIGINS`: Orígenes CORS permitidos
- `OMP_NUM_THREADS`: Threading para OpenMP (1 en macOS para evitar crashes)

## Dependencias Principales

- **FastAPI**: Framework web asíncrono (v0.104.1)
- **Transformers**: Modelos BERT de Hugging Face (v4.35.2)
- **XGBoost**: Gradient boosting para clasificación multi-label (v2.0.3)
- **PyTorch**: Deep learning framework (v2.1.1)
- **Faster-Whisper**: Transcripción de audio optimizada (v0.10.0)
- **scikit-learn**: Herramientas ML (v1.3.2)
- **Uvicorn**: Servidor ASGI de alto rendimiento (v0.24.0)
- **Pydantic**: Validación de datos (v2.5.0)

## Notas Importantes

### macOS - Fix OpenMP Crash
Si experimentas segmentation faults en macOS, el proyecto ya incluye la configuración necesaria en `app/main.py`:

```python
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

Esto previene conflictos entre `libomp.dylib` (Faster-Whisper) y `libiomp5.dylib` (PyTorch).

### Métricas del Modelo
El modelo multi-etiqueta actual tiene las siguientes métricas en el test set:
- **Depresión**: Accuracy 72.5%, F1-Score 76.0%
- **Ansiedad**: Accuracy 68.0%, F1-Score 61.9%
- **Overall**: Avg Accuracy 70.25%, Avg F1-Score 68.9%

## Deployment

Ver [docs/guides/deployment.md](../docs/guides/deployment.md) para instrucciones de despliegue.
