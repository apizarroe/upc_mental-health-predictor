# Mental Health Predictor — API Reference

Base URL: `http://localhost:8000`  
Docs interactivos: `/docs` (Swagger) · `/redoc`

> **Prerequisito:** tener el modelo entrenado. Ver `README.md`.

---

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/v1/predict/mental-health` | Predicción de depresión y ansiedad |
| `POST` | `/api/v1/audio/transcribe` | Transcripción de audio a texto |
| `GET` | `/api/v1/health` | Estado del servicio |
| `GET` | `/api/v1/model/info` | Información del modelo cargado |

---

## POST `/api/v1/predict/mental-health`

**Request**
```json
{
  "patient_id": "PAT-001",
  "answers": {
    "question1": "Mi día fue tenso, todo me generaba preocupación.",
    "question2": "Ahora me siento inquieto y con la mente acelerada.",
    "question3": "Estoy nervioso, algo agotado emocionalmente.",
    "question4": "Tuve varias situaciones inesperadas que aumentaron mi ansiedad."
  }
}
```

- `patient_id`: opcional
- `answers`: exactamente 4 respuestas, mínimo 5 caracteres cada una

**Response `200`**
```json
{
  "status": "success",
  "patient_id": "PAT-001",
  "predictions": {
    "depression": { "has_condition": true, "probability": 0.42, "confidence": 0.42, "label": "Depresión" },
    "anxiety":    { "has_condition": true, "probability": 0.77, "confidence": 0.77, "label": "Ansiedad" }
  },
  "summary": {
    "has_depression": true,
    "has_anxiety": true,
    "conditions_detected": ["depression", "anxiety"],
    "interpretation": "Se detectaron indicadores de depresión (42%) y ansiedad (77%). Se recomienda evaluación profesional."
  },
  "analysis": {
    "combined_text_length": 312,
    "depression_keywords": ["agotado"],
    "anxiety_keywords": ["inquieto", "nervioso", "tensión", "ansiedad"]
  },
  "model_info": {
    "model_name": "mental_health_lr_20260421_120000",
    "model_type": "logistic_regression_binary_pair",
    "bert_model": "PlanTL-GOB-ES/roberta-base-biomedical-es"
  },
  "timestamp": "2026-04-21T12:00:00Z"
}
```

**Errores**

| Código | Causa |
|---|---|
| `400` | Respuestas faltantes, vacías o menores a 5 caracteres |
| `500` | Error interno del servidor |
| `503` | Modelo no entrenado o no encontrado |

---

## POST `/api/v1/audio/transcribe`

**Request:** `multipart/form-data` con campo `audio` (wav, mp3, m4a, ogg, webm)

```bash
curl -X POST http://localhost:8000/api/v1/audio/transcribe \
  -F "audio=@recording.wav"
```

**Response `200`**
```json
{
  "status": "success",
  "transcription": "Me siento muy cansado y sin energía últimamente",
  "language": "es",
  "duration": 3.5,
  "model_used": "small"
}
```

---

## GET `/api/v1/health`

```json
{ "status": "healthy", "service": "Mental Health Predictor API", "version": "1.0.0" }
```

---

## Ejemplo rápido

```bash
curl -X POST http://localhost:8000/api/v1/predict/mental-health \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "question1": "Me siento muy triste y sin esperanza",
      "question2": "Estoy nervioso y preocupado todo el tiempo",
      "question3": "No puedo dormir bien",
      "question4": "Me siento solo y con miedo del futuro"
    }
  }'
```
