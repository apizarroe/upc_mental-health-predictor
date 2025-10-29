# API ML - Predicciones de Trastornos Mentales

Documentación de los endpoints de Machine Learning para predicción de trastornos mentales usando BERT, XGBoost y Random Forest.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

```bash
GET /health
```

Verifica que el servicio de ML esté funcionando correctamente.

**Ejemplo:**
```bash
curl http://localhost:8000/health
```

**Respuesta exitosa (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true
}
```

---

### 2. Predicción de Trastorno Mental

```bash
POST /predict
```

Realiza una predicción de trastorno mental basada en el texto de las notas clínicas.

**Body (JSON):**
```json
{
  "texto": "El paciente presenta síntomas de ansiedad constante, dificultad para concentrarse...",
  "modelo": "bert",
  "incluir_probabilidades": true
}
```

**Parámetros:**
- `texto` (string, requerido): Notas clínicas del paciente
- `modelo` (string, opcional): Modelo a usar. Valores: `"bert"`, `"xgboost"`, `"random_forest"`. Default: `"bert"`
- `incluir_probabilidades` (boolean, opcional): Si incluir probabilidades de todas las clases. Default: `false`

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "El paciente presenta síntomas de ansiedad constante, dificultad para concentrarse y problemas de sueño desde hace varios meses.",
    "modelo": "bert",
    "incluir_probabilidades": true
  }'
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "prediccion": {
    "trastorno": "Trastorno de Ansiedad Generalizada",
    "codigo": "F41.1",
    "confianza": 0.87,
    "modelo_usado": "bert"
  },
  "probabilidades": {
    "F41.1": 0.87,
    "F32.0": 0.08,
    "F43.1": 0.03,
    "F33.0": 0.02
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "longitud_texto": 145,
    "tiempo_procesamiento_ms": 234
  }
}
```

**Respuesta error (400):**
```json
{
  "success": false,
  "error": "Texto vacío o inválido"
}
```

---

### 3. Predicción por Lote (Batch)

```bash
POST /predict/batch
```

Realiza predicciones para múltiples textos en una sola petición.

**Body (JSON):**
```json
{
  "textos": [
    "Texto de nota clínica 1...",
    "Texto de nota clínica 2...",
    "Texto de nota clínica 3..."
  ],
  "modelo": "bert",
  "incluir_probabilidades": false
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "textos": [
      "Paciente con ansiedad constante...",
      "Presenta síntomas depresivos..."
    ],
    "modelo": "xgboost"
  }'
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "predicciones": [
    {
      "id": 0,
      "trastorno": "Trastorno de Ansiedad Generalizada",
      "codigo": "F41.1",
      "confianza": 0.87
    },
    {
      "id": 1,
      "trastorno": "Episodio Depresivo Leve",
      "codigo": "F32.0",
      "confianza": 0.82
    }
  ],
  "metadata": {
    "total_procesados": 2,
    "modelo_usado": "xgboost",
    "tiempo_total_ms": 456
  }
}
```

---

### 4. Comparar Modelos

```bash
POST /predict/compare
```

Obtiene predicciones de los 3 modelos (BERT, XGBoost, Random Forest) para el mismo texto y compara resultados.

**Body (JSON):**
```json
{
  "texto": "El paciente presenta síntomas de ansiedad constante..."
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8000/predict/compare \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "El paciente presenta síntomas de ansiedad constante, dificultad para concentrarse."
  }'
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "texto_original": "El paciente presenta síntomas de ansiedad...",
  "predicciones": {
    "bert": {
      "trastorno": "Trastorno de Ansiedad Generalizada",
      "codigo": "F41.1",
      "confianza": 0.87
    },
    "xgboost": {
      "trastorno": "Trastorno de Ansiedad Generalizada",
      "codigo": "F41.1",
      "confianza": 0.84
    },
    "random_forest": {
      "trastorno": "Trastorno de Ansiedad Generalizada",
      "codigo": "F41.1",
      "confianza": 0.81
    }
  },
  "consenso": {
    "trastorno": "Trastorno de Ansiedad Generalizada",
    "codigo": "F41.1",
    "acuerdo": "unanime",
    "confianza_promedio": 0.84
  }
}
```

---

### 5. Información de Modelos

```bash
GET /models/info
```

Obtiene información sobre los modelos cargados en el servidor.

**Ejemplo:**
```bash
curl http://localhost:8000/models/info
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "modelos": {
    "bert": {
      "nombre": "BERT base multilingual",
      "version": "1.0.0",
      "accuracy": 0.89,
      "f1_score": 0.87,
      "cargado": true,
      "ultima_actualizacion": "2024-01-01"
    },
    "xgboost": {
      "nombre": "XGBoost Classifier",
      "version": "1.0.0",
      "accuracy": 0.85,
      "f1_score": 0.83,
      "cargado": true,
      "ultima_actualizacion": "2024-01-01"
    },
    "random_forest": {
      "nombre": "Random Forest Classifier",
      "version": "1.0.0",
      "accuracy": 0.83,
      "f1_score": 0.81,
      "cargado": true,
      "ultima_actualizacion": "2024-01-01"
    }
  },
  "clases_disponibles": [
    "F32.0 - Episodio Depresivo Leve",
    "F33.0 - Trastorno Depresivo Recurrente",
    "F41.1 - Trastorno de Ansiedad Generalizada",
    "F43.1 - Trastorno de Estrés Postraumático"
  ]
}
```

---

## Códigos CIE-10 Soportados

El sistema puede predecir los siguientes trastornos mentales según la clasificación CIE-10:

| Código | Trastorno |
|--------|-----------|
| F32.0  | Episodio Depresivo Leve |
| F32.1  | Episodio Depresivo Moderado |
| F32.2  | Episodio Depresivo Grave |
| F33.0  | Trastorno Depresivo Recurrente |
| F41.0  | Trastorno de Pánico |
| F41.1  | Trastorno de Ansiedad Generalizada |
| F43.1  | Trastorno de Estrés Postraumático |
| F43.2  | Trastorno de Adaptación |

---

## Códigos de Estado HTTP

- `200` - OK: Operación exitosa
- `400` - Bad Request: Datos inválidos o texto vacío
- `404` - Not Found: Modelo no encontrado
- `500` - Internal Server Error: Error en el procesamiento del modelo
- `503` - Service Unavailable: Modelos no cargados

---

## Notas de Implementación

### Modelos

1. **BERT (Bidirectional Encoder Representations from Transformers)**
   - Modelo de deep learning basado en transformers
   - Mejor precisión general
   - Mayor tiempo de procesamiento
   - Recomendado para análisis detallado

2. **XGBoost**
   - Modelo de gradient boosting
   - Balance entre precisión y velocidad
   - Bueno para predicciones en tiempo real
   - Recomendado para uso en producción

3. **Random Forest**
   - Modelo de ensamble de árboles de decisión
   - Más rápido pero menos preciso
   - Útil como validación cruzada
   - Recomendado para predicciones masivas

### Consideraciones de Uso

- **Longitud del texto**: Mínimo 50 caracteres, máximo 5000 caracteres
- **Idioma**: Los modelos están entrenados para español
- **Timeout**: Las peticiones tienen un timeout de 30 segundos
- **Rate limiting**: Máximo 100 peticiones por minuto
- **Batch size**: Máximo 50 textos por petición batch

### Interpretación de Resultados

- **Confianza >= 0.80**: Alta confianza en la predicción
- **Confianza 0.60-0.79**: Confianza moderada, revisar manualmente
- **Confianza < 0.60**: Baja confianza, requiere evaluación clínica completa

---

## Ejemplo de Integración desde SvelteKit

```javascript
// frontend/src/lib/services/ml-api.js
import { PUBLIC_ML_API_URL } from '$env/static/public';

export async function predecirTrastorno(texto, modelo = 'bert') {
  const response = await fetch(`${PUBLIC_ML_API_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      texto,
      modelo,
      incluir_probabilidades: true
    })
  });

  if (!response.ok) {
    throw new Error('Error al realizar predicción');
  }

  return await response.json();
}
```

---

## Seguridad

- Todas las peticiones deben incluir autenticación (pendiente implementación)
- Los datos sensibles deben enviarse sobre HTTPS
- Los resultados de predicción no deben sustituir el diagnóstico clínico profesional
- Cumplir con regulaciones de privacidad de datos de salud

---

## Estado de Implementación

⚠️ **Esta documentación describe la API planificada. La implementación en Python FastAPI está pendiente.**

### Pendiente:
- [ ] Implementar endpoints en FastAPI
- [ ] Entrenar/cargar modelos BERT, XGBoost y Random Forest
- [ ] Implementar sistema de autenticación
- [ ] Configurar rate limiting
- [ ] Agregar logging y monitoreo
- [ ] Pruebas de carga y optimización
