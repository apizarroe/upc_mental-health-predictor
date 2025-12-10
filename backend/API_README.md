# Mental Health Predictor API

API REST para predicción de trastornos mentales (depresión y ansiedad) usando modelo BERT + XGBoost Multi-Etiqueta.

## 🚀 Inicio Rápido

### Requisitos previos

1. Tener el modelo entrenado (ejecutar primero `python scripts/train.py`)
2. Python 3.8+ con entorno virtual activado
3. Dependencias instaladas (`pip install -r requirements.txt`)

### Iniciar el servidor

```bash
cd backend

# Opción 1: Usar el script wrapper (recomendado)
./run_api.sh

# Opción 2: Iniciar en puerto específico
./run_api.sh 8080

# Opción 3: Manual
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

---

## 📡 Endpoints

### Resumen de Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/predict/mental-health` | Predicción multi-etiqueta (depresión + ansiedad) |
| POST | `/api/v1/predict/depression` | Predicción legacy (deprecado, usar mental-health) |
| POST | `/api/v1/audio/transcribe` | Transcripción de audio a texto |
| GET | `/api/v1/health` | Health check del servicio |
| GET | `/api/v1/model/info` | Información del modelo ML cargado |

---

### 1. Predicción de Salud Mental (Multi-Etiqueta)

**POST** `/api/v1/predict/mental-health`

Predice depresión Y ansiedad basándose en 4 respuestas del paciente.

#### Request Body

```json
{
  "patient_id": "PAT-001",
  "answers": {
    "question1": "Me siento cansado todo el tiempo y sin energía",
    "question2": "No tengo motivación para hacer las cosas que antes disfrutaba",
    "question3": "Duermo mal y me despierto varias veces en la noche",
    "question4": "Me siento solo aunque esté rodeado de gente"
  }
}
```

**Campos:**
- `patient_id` (opcional): ID del paciente para tracking
- `answers` (requerido): Diccionario con exactamente 4 respuestas
  - Cada respuesta debe tener al menos 5 caracteres
  - Las claves deben ser: `question1`, `question2`, `question3`, `question4`

#### Response (200 OK)

```json
{
  "status": "success",
  "patient_id": "PAT-001",
  "predictions": {
    "depression": {
      "has_condition": true,
      "probability": 0.7823,
      "confidence": 0.8234,
      "label": "Depresión"
    },
    "anxiety": {
      "has_condition": true,
      "probability": 0.6512,
      "confidence": 0.7105,
      "label": "Ansiedad"
    }
  },
  "summary": {
    "has_depression": true,
    "has_anxiety": true,
    "conditions_detected": ["depression", "anxiety"],
    "interpretation": "Se detectaron indicadores de depresión (78%) y ansiedad (65%). Se recomienda evaluación profesional."
  },
  "analysis": {
    "combined_text_length": 234,
    "depression_keywords": ["cansado", "energía", "solo", "motivación"],
    "anxiety_keywords": ["nervioso", "preocupado"]
  },
  "model_info": {
    "model_name": "mental_health_multilabel_20251123_171033",
    "model_type": "multi_label",
    "labels": ["depression", "anxiety"],
    "bert_model": "dccuchile/bert-base-spanish-wwm-cased",
    "created_at": "2025-11-23T17:10:33",
    "metrics": {
      "depression": {
        "accuracy": 0.725,
        "precision": 0.725,
        "recall": 0.798,
        "f1_score": 0.760
      },
      "anxiety": {
        "accuracy": 0.680,
        "precision": 0.693,
        "recall": 0.559,
        "f1_score": 0.619
      },
      "overall": {
        "avg_accuracy": 0.7025,
        "avg_f1_score": 0.6894
      }
    }
  },
  "timestamp": "2025-11-23T17:15:00Z"
}
```

**Campos de respuesta:**

- `status`: Estado de la operación ("success" o "error")
- `patient_id`: ID del paciente (si se proporcionó)
- `predictions`: Predicciones para cada condición
  - `depression`: Predicción de depresión
    - `has_condition`: Boolean indicando si se detectó
    - `probability`: Probabilidad (0.0 a 1.0)
    - `confidence`: Confianza del modelo
    - `label`: "Depresión" o "Sin depresión"
  - `anxiety`: Predicción de ansiedad (misma estructura)
- `summary`: Resumen de las predicciones
  - `has_depression`: Boolean
  - `has_anxiety`: Boolean
  - `conditions_detected`: Lista de condiciones detectadas
  - `interpretation`: Explicación en lenguaje natural
- `analysis`:
  - `combined_text_length`: Longitud del texto analizado
  - `depression_keywords`: Keywords de depresión encontradas
  - `anxiety_keywords`: Keywords de ansiedad encontradas
- `model_info`: Información del modelo con métricas por condición
- `timestamp`: Timestamp de la predicción

#### Errores posibles

**400 Bad Request** - Request inválido
```json
{
  "detail": "Se requieren exactamente 4 respuestas"
}
```

**503 Service Unavailable** - Modelo no disponible
```json
{
  "detail": "Modelo no disponible: No se encontró el modelo entrenado"
}
```

**500 Internal Server Error** - Error interno
```json
{
  "detail": "Error interno en predicción: ..."
}
```

---

### 2. Predicción de Depresión (Legacy)

**POST** `/api/v1/predict/depression`

> ⚠️ **DEPRECADO**: Usar `/api/v1/predict/mental-health` en su lugar.

Este endpoint se mantiene por retrocompatibilidad y retorna la misma estructura que el endpoint multi-etiqueta.

---

### 3. Transcripción de Audio

**POST** `/api/v1/audio/transcribe`

Transcribe audio a texto usando Faster-Whisper (modelo `small` optimizado para español).

#### Request Body

**Content-Type**: `multipart/form-data`

```
audio: archivo de audio (formatos soportados: wav, mp3, m4a, ogg, webm)
```

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/audio/transcribe" \
  -H "accept: application/json" \
  -F "audio=@recording.wav"
```

#### Response (200 OK)

```json
{
  "status": "success",
  "transcription": "Me siento muy cansado y sin energía últimamente",
  "language": "es",
  "duration": 3.5,
  "model_used": "small",
  "timestamp": "2025-12-09T10:30:00Z"
}
```

**Campos de respuesta:**
- `status`: Estado de la operación ("success" o "error")
- `transcription`: Texto transcrito del audio
- `language`: Idioma detectado (ISO 639-1)
- `duration`: Duración del audio en segundos
- `model_used`: Modelo de Whisper utilizado
- `timestamp`: Timestamp de la transcripción

#### Errores posibles

**400 Bad Request** - No se proporcionó archivo
```json
{
  "detail": "No se proporcionó archivo de audio"
}
```

**415 Unsupported Media Type** - Formato no soportado
```json
{
  "detail": "Formato de audio no soportado. Use: wav, mp3, m4a, ogg, webm"
}
```

**500 Internal Server Error** - Error en transcripción
```json
{
  "detail": "Error al transcribir el audio: ..."
}
```

---

### 4. Health Check

**GET** `/api/v1/health`

Verifica que el servicio esté funcionando.

#### Response (200 OK)

```json
{
  "status": "healthy",
  "service": "Mental Health Predictor API",
  "version": "2.0.0",
  "timestamp": "2025-12-09T10:30:00Z"
}
```

---

### 5. Información del Modelo

**GET** `/api/v1/model/info`

Obtiene información del modelo de ML cargado.

#### Response (200 OK)

```json
{
  "status": "success",
  "model": {
    "name": "mental_health_multilabel_20251123_171033",
    "model_type": "multi_label",
    "labels": ["depression", "anxiety"],
    "bert_model": "dccuchile/bert-base-spanish-wwm-cased",
    "created_at": "2025-11-23T17:10:33",
    "metrics": {
      "depression": {"accuracy": 0.725, "f1_score": 0.760},
      "anxiety": {"accuracy": 0.680, "f1_score": 0.619},
      "overall": {"avg_accuracy": 0.7025, "avg_f1_score": 0.6894}
    }
  },
  "timestamp": "2025-11-23T17:15:00Z"
}
```

---

## 💻 Ejemplos de Uso

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/predict/mental-health" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PAT-001",
    "answers": {
      "question1": "Me siento cansado todo el tiempo",
      "question2": "No tengo motivación para nada",
      "question3": "Duermo muy mal",
      "question4": "Me siento muy solo"
    }
  }'
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/predict/mental-health"

payload = {
    "patient_id": "PAT-001",
    "answers": {
        "question1": "Me siento cansado todo el tiempo",
        "question2": "No tengo motivación para nada",
        "question3": "Duermo muy mal",
        "question4": "Me siento muy solo"
    }
}

response = requests.post(url, json=payload)
result = response.json()

# Acceder a predicciones
print(f"Depresión detectada: {result['predictions']['depression']['has_condition']}")
print(f"Probabilidad depresión: {result['predictions']['depression']['probability']:.2%}")
print(f"Ansiedad detectada: {result['predictions']['anxiety']['has_condition']}")
print(f"Probabilidad ansiedad: {result['predictions']['anxiety']['probability']:.2%}")
print(f"Interpretación: {result['summary']['interpretation']}")
```

### JavaScript (fetch)

```javascript
const url = 'http://localhost:8000/api/v1/predict/mental-health';

const payload = {
  patient_id: 'PAT-001',
  answers: {
    question1: 'Me siento cansado todo el tiempo',
    question2: 'No tengo motivación para nada',
    question3: 'Duermo muy mal',
    question4: 'Me siento muy solo'
  }
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log('Depresión:', data.predictions.depression.has_condition);
    console.log('Prob. Depresión:', data.predictions.depression.probability);
    console.log('Ansiedad:', data.predictions.anxiety.has_condition);
    console.log('Prob. Ansiedad:', data.predictions.anxiety.probability);
    console.log('Interpretación:', data.summary.interpretation);
  })
  .catch(error => console.error('Error:', error));
```

### JavaScript - Transcripción de Audio

```javascript
const url = 'http://localhost:8000/api/v1/audio/transcribe';

// Usando FormData para enviar archivo
const formData = new FormData();
formData.append('audio', audioFile); // audioFile es un File object del input

fetch(url, {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log('Transcripción:', data.transcription);
    console.log('Idioma:', data.language);
    console.log('Duración:', data.duration, 'segundos');
  })
  .catch(error => console.error('Error:', error));
```

---

## 🔧 Configuración

### Variables de entorno

El API puede configurarse mediante variables de entorno (crear archivo `.env`):

```bash
# Puerto del servidor
API_PORT=8000

# Host
API_HOST=0.0.0.0

# Modo de desarrollo
DEBUG=True

# CORS origins permitidos (separados por coma)
CORS_ORIGINS=http://localhost:3000,https://tu-dominio.com
```

### CORS

Por defecto, el API permite requests desde cualquier origen (`allow_origins=["*"]`).

**Para producción**, edita [app/main.py](app/main.py) y especifica los orígenes permitidos:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Dominios específicos
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 🏗️ Arquitectura

```
backend/
├── app/
│   ├── main.py                    # FastAPI app principal
│   ├── api/
│   │   ├── routes/
│   │   │   ├── prediction.py      # Endpoint de predicción (multi-etiqueta)
│   │   │   └── health.py          # Health check
│   │   └── schemas/
│   │       └── prediction.py      # Pydantic models (multi-etiqueta)
│   ├── core/
│   │   └── dependencies.py        # Dependency injection
│   └── ml/                        # Modelos ML
│       ├── prediction_pipeline.py # Pipeline de predicción
│       ├── training_pipeline.py   # Pipeline de entrenamiento
│       ├── bert_encoder.py        # Encoder BERT
│       ├── multi_label_classifier.py  # Clasificador XGBoost multi-etiqueta
│       └── preprocessor.py        # Preprocesador de texto
├── scripts/
│   ├── train.py                   # Script de entrenamiento
│   └── test.py                    # Script de validación
├── run_api.sh                     # Script para iniciar servidor
└── API_README.md                  # Esta documentación
```

---

## 🧪 Testing

### Health check

```bash
curl http://localhost:8000/api/v1/health
```

### Predicción de ejemplo (caso con indicadores)

```bash
curl -X POST "http://localhost:8000/api/v1/predict/mental-health" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "question1": "Me siento muy triste y sin esperanza",
      "question2": "Estoy nervioso y preocupado todo el tiempo",
      "question3": "No puedo dormir bien, tengo insomnio",
      "question4": "Me siento solo y con miedo del futuro"
    }
  }'
```

### Predicción de ejemplo (caso sin indicadores)

```bash
curl -X POST "http://localhost:8000/api/v1/predict/mental-health" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "question1": "Me siento bien y con energía",
      "question2": "Disfruto de mis actividades diarias",
      "question3": "Duermo bien toda la noche",
      "question4": "Me siento acompañado y feliz"
    }
  }'
```

### Validar modelo con CSV

```bash
python scripts/test.py --csv --data-path data/datasets/example_patient_messages.csv
```

---

## 📊 Modelo de ML

- **Tipo**: Multi-Etiqueta (predice depresión Y ansiedad simultáneamente)
- **BERT**: `dccuchile/bert-base-spanish-wwm-cased`
- **Clasificador**: XGBoost con MultiOutputClassifier
- **Input**: 4 respuestas de texto concatenadas
- **Output**: Probabilidades de depresión y ansiedad (0-1 cada una)
- **Métricas (Test Set)**:
  - **Depresión**: Accuracy 72.5%, F1-Score 76.0%
  - **Ansiedad**: Accuracy 68.0%, F1-Score 61.9%
  - **Overall**: Avg Accuracy 70.25%, Avg F1-Score 68.9%

### Entrenamiento

```bash
# Entrenar modelo multi-etiqueta (default)
python scripts/train.py

# Entrenar modelo binario (solo depresión)
python scripts/train.py --binary
```

---

## 🚨 Notas Importantes

1. **Este modelo es solo para screening, NO reemplaza diagnóstico profesional**
2. Las 4 respuestas se concatenan para mantener contexto completo
3. El modelo predice **ambos trastornos simultáneamente** (no son excluyentes)
4. El modelo se carga una vez al iniciar (singleton) para mejor performance
5. Se recomienda usar HTTPS en producción
6. Configurar CORS apropiadamente para producción

---

## 🐛 Troubleshooting

### Error: "Modelo no disponible"

Entrenar el modelo primero:
```bash
python scripts/train.py
```

### Error: "ModuleNotFoundError: No module named 'app'"

Asegurarse de estar en el directorio `backend`:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Error: "ModuleNotFoundError" (dependencias)

Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Puerto 8000 ya en uso

Usar un puerto diferente:
```bash
./run_api.sh 8080
```

O matar el proceso existente:
```bash
pkill -f "uvicorn app.main:app"
```

---

## 📝 Changelog

### v2.0.0 (2025-11-23)
- 🎯 **NUEVO**: Modelo Multi-Etiqueta (depresión + ansiedad)
- 🔄 Nuevo endpoint `/api/v1/predict/mental-health`
- 📊 Predicciones separadas para cada condición
- 📈 Keywords separadas por trastorno
- 🔙 Retrocompatibilidad con endpoint `/api/v1/predict/depression`

### v1.0.0 (2025-11-21)
- ✨ Implementación inicial del API
- 🎯 Endpoint de predicción de depresión
- 📊 Análisis de 4 respuestas del paciente
- 🔍 Health check y model info endpoints
- 📚 Documentación Swagger/ReDoc
