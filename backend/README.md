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
│   ├── models/         # Implementación de modelos ML
│   ├── services/       # Lógica de negocio
│   ├── utils/          # Utilidades
│   ├── config/         # Configuración
│   └── main.py         # Punto de entrada
├── data/
│   ├── trained_models/ # Modelos entrenados
│   └── datasets/       # Datasets
├── scripts/            # Scripts auxiliares
└── tests/              # Tests
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

## Scripts Disponibles

```bash
# Entrenar modelos
python scripts/train_models.py

# Descargar modelos pre-entrenados
python scripts/download_models.py

# Evaluar modelos
python scripts/evaluate_models.py
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
