# Backend ML API - Mental Health Predictor

Microservicio Python especializado en predicción de trastornos mentales usando modelos de Machine Learning y Deep Learning.

## Modelos Implementados

- **BERT**: Modelo de lenguaje pre-entrenado para análisis contextual
- **XGBoost**: Gradient boosting para clasificación
- **Random Forest**: Ensemble de árboles de decisión
- **Ensemble**: Combinación de modelos para mejor precisión

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

### Health Check
```http
GET /health
```

### Predicción
```http
POST /api/v1/predict
Content-Type: application/json

{
  "text": "Nota clínica del paciente...",
  "model": "bert"  // "xgboost" | "random_forest" | "ensemble"
}
```

### Información del Modelo
```http
GET /api/v1/models
```

## Variables de Entorno

Ver `.env.example` para configuración completa.

Principales variables:
- `PORT`: Puerto del servidor (default: 8000)
- `BERT_MODEL_PATH`: Ruta al modelo BERT
- `XGBOOST_MODEL_PATH`: Ruta al modelo XGBoost
- `RF_MODEL_PATH`: Ruta al modelo Random Forest
- `MAX_LENGTH`: Longitud máxima de tokens
- `DEVICE`: cpu, cuda o mps

## Dependencias Principales

- FastAPI: Framework web
- Transformers: Modelos BERT
- XGBoost: Gradient boosting
- scikit-learn: ML tradicional
- PyTorch: Deep learning
- Uvicorn: Servidor ASGI

## Deployment

Ver [docs/guides/deployment.md](../docs/guides/deployment.md) para instrucciones de despliegue.
