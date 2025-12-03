# 🧠 Módulo de Machine Learning - Detección de Trastornos Mentales

Sistema de detección de **depresión y ansiedad** basado en **RoBERTa Biomedical + XGBoost Multi-Label** que analiza conversaciones de pacientes.

> **💡 Para entrenar modelos desde cero:** Ver [Guía de Entrenamiento](../../docs/TRAINING_GUIDE.md)

## 📋 Descripción

Este módulo implementa un pipeline completo de ML **multi-etiqueta** que:

1. **Preprocesa** conversaciones de chat terapéuticas
2. **Codifica** el texto usando embeddings RoBERTa Biomedical (español)
3. **Clasifica** usando XGBoost Multi-Output para detectar **depresión Y ansiedad** simultáneamente

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Conversación   │
│   (texto raw)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TextPreprocessor│  ← Limpieza y extracción de mensajes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RoBERTa Encoder │  ← Embeddings de 768 dimensiones
│   (Biomedical)  │    PlanTL-GOB-ES/roberta-base-biomedical-es
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ XGBoost Multi-  │  ← Clasificación multi-etiqueta
│ OutputClassifier│
└────────┬────────┘
         │
         ▼
  ┌──────────────────┐
  │   Predicción     │
  │ ┌──────┬───────┐ │
  │ │Depre-│Ansie- │ │
  │ │sión  │dad    │ │
  │ └──────┴───────┘ │
  └──────────────────┘
```

## 📁 Estructura de Archivos

```
app/ml/
├── __init__.py                # Exports principales
├── training_pipeline.py       # 🚀 Pipeline completo de entrenamiento
├── prediction_pipeline.py     # 🚀 Pipeline completo de predicción/inferencia
├── data_loaders/              # 🆕 Loaders por formato de datos
│   ├── __init__.py
│   ├── parquet_loader.py      # Loader para Parquet + conversaciones JSON
│   └── csv_loader.py          # Loader para CSV (simple y agrupado)
├── text_processing.py         # 🆕 Limpieza de texto (REUTILIZABLE)
├── labeling.py                # 🆕 Detección de condiciones (REUTILIZABLE)
├── bert_encoder.py            # Encoder BERT para embeddings
├── classifier.py              # Clasificador XGBoost
├── preprocessor.py            # LEGACY - mantener por compatibilidad
├── examples/                  # 🆕 Ejemplos de uso
│   └── example_usage.py
└── README.md                  # Esta documentación
```

### 🆕 Nueva Arquitectura Modular

Los módulos están separados por **responsabilidad única** para maximizar **reutilización**:

| Módulo | Responsabilidad | Reutilizable |
|--------|-----------------|--------------|
| `training_pipeline` | Orquestar entrenamiento completo | ⚠️ (uso: scripts/train.py) |
| `prediction_pipeline` | Orquestar predicción/inferencia | ✅ (API, scripts, apps) |
| `data_loaders/` | Solo cargar textos crudos | ❌ (específico por formato) |
| `text_processing` | Solo limpiar textos | ✅ (funciona con cualquier fuente) |
| `labeling` | Solo etiquetar textos | ✅ (funciona con cualquier fuente) |
| `bert_encoder` | Generar embeddings | ✅ |
| `classifier` | Entrenar/predecir | ✅ |

## 🚀 Uso Rápido

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Entrenar el modelo

```bash
# Entrenamiento básico (multi-label: depresión + ansiedad)
python scripts/train.py

# Con configuración personalizada
python scripts/train.py \
    --data-path data/datasets/train-00000-of-00001.parquet \
    --bert-model PlanTL-GOB-ES/roberta-base-biomedical-es \
    --n-estimators 150 \
    --max-depth 5 \
    --learning-rate 0.08 \
    --batch-size 32
```

### 3. Evaluar el modelo

```bash
# Evaluación multi-label completa (depresión + ansiedad)
python scripts/test.py --full-test

# Evaluar solo depresión
python scripts/test.py --full-test --condition depression

# Evaluar solo ansiedad
python scripts/test.py --full-test --condition anxiety

# Evaluar ambas condiciones por separado
python scripts/test.py --full-test --condition depression anxiety

# Testear texto personalizado
python scripts/test.py --text "Me siento muy triste y nervioso últimamente"

# Testear conversaciones aleatorias
python scripts/test.py --random 10
```

| Comando | Descripción |
|---------|-------------|
| `--full-test` | Evalúa en todo el dataset |
| `--condition all` | Multi-label (default) |
| `--condition depression` | Solo depresión |
| `--condition anxiety` | Solo ansiedad |
| `--text "..."` | Texto personalizado |
| `--random N` | N conversaciones aleatorias |

### 4. Usar el modelo entrenado

```python
from app.ml.prediction_pipeline import PredictionPipeline

# Cargar modelo (automáticamente el más reciente)
pipeline = PredictionPipeline()

# Hacer predicción individual (multi-label)
result = pipeline.predict_text("Me siento muy triste y nervioso últimamente...")

# Resultado multi-etiqueta
print(f"Depresión: {result['predictions']['depression']['label']}")
print(f"  Probabilidad: {result['predictions']['depression']['probability']:.2%}")

print(f"Ansiedad: {result['predictions']['anxiety']['label']}")
print(f"  Probabilidad: {result['predictions']['anxiety']['probability']:.2%}")

print(f"Condiciones detectadas: {result['summary']['conditions_detected']}")

# Predicción en batch (eficiente para múltiples textos)
texts = ["Texto 1", "Texto 2", "Texto 3"]
results = pipeline.predict_batch(texts)
```

## 🔄 Usando Diferentes Formatos de Entrada

### Opción 1: Datos desde Parquet (actual)

```python
from app.ml.data_loaders import ParquetChatLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# 1. Cargar conversaciones del Parquet
loader = ParquetChatLoader("data/datasets/train-00000-of-00001.parquet")
texts = loader.extract_all_texts()

# 2. Limpiar textos
clean_texts = [clean_text(t) for t in texts]

# 3. Etiquetar
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]

# Ahora tienes texts y labels listos para entrenar
```

### Opción 2: Datos desde CSV simple

```python
from app.ml.data_loaders import CSVTextLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# CSV con estructura:
# text
# "Me siento muy triste"
# "Estoy emocionado"

# 1. Cargar textos del CSV
loader = CSVTextLoader("patient_notes.csv", text_column="text")
texts = loader.extract_texts()

# 2-3. Mismo código que con Parquet (REUTILIZABLE)
clean_texts = [clean_text(t) for t in texts]
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]
```

### Opción 3: CSV con múltiples mensajes por paciente

```python
from app.ml.data_loaders import CSVPatientLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# CSV con estructura:
# patient_id,message,timestamp
# PAC001,"Me siento triste",2025-01-01
# PAC001,"No tengo energía",2025-01-02

# 1. Cargar y agrupar por paciente
loader = CSVPatientLoader(
    "patient_messages.csv",
    patient_id_column="patient_id",
    message_column="message",
    timestamp_column="timestamp"
)
patient_texts = loader.load_grouped_by_patient()

# 2-3. Mismo código (REUTILIZABLE)
clean_texts = [clean_text(t) for t in patient_texts]
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]
```

### Opción 4: Datos desde API o memoria

```python
import requests
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# 1. Obtener de API
response = requests.get("https://api.hospital.com/patient_notes")
texts = [note['content'] for note in response.json()]

# 2-3. Mismo código (REUTILIZABLE)
clean_texts = [clean_text(t) for t in texts]
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]
```

**💡 Ventaja**: Los módulos `text_processing` y `labeling` funcionan con **cualquier fuente de datos**.

### ¿Cuándo usar cada enfoque?

| Enfoque | Cuándo usar |
|---------|-------------|
| **Módulos nuevos** (recomendado) | • Datos de CSV<br>• Datos de API<br>• Múltiples fuentes<br>• Código nuevo |
| **TextPreprocessor** (legacy) | • Mantener compatibilidad<br>• Código existente que ya lo usa |

**Ver ejemplos completos**: `app/ml/examples/example_usage.py`

## 🔧 Componentes

### TextPreprocessor (LEGACY)

Preprocesa conversaciones para análisis:
- Extrae mensajes del usuario (ignora system y assistant)
- Limpia texto (URLs, emails, espacios)
- Detecta keywords de depresión para etiquetado inicial

```python
from app.ml.preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()
texts, labels = preprocessor.create_dataset('data.parquet')
```

### BERTEncoder

Convierte texto a embeddings vectoriales:
- Usa modelo BERT multilingüe español
- Embeddings de 768 dimensiones
- Procesa en batches para eficiencia
- Soporte GPU/CPU automático

```python
from app.ml.bert_encoder import BERTEncoder

encoder = BERTEncoder(
    model_name='dccuchile/bert-base-spanish-wwm-cased',
    batch_size=16
)
embeddings = encoder.encode_texts(texts)
```

### DepressionClassifier

Clasificador XGBoost para detección:
- Clasificación binaria (depresión/no depresión)
- Métricas: accuracy, precision, recall, F1
- Matriz de confusión
- Feature importance

```python
from app.ml.classifier import DepressionClassifier

classifier = DepressionClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)
classifier.train(X_train, y_train, X_val, y_val)
classifier.save('model.pkl')
```

### TrainingPipeline

Pipeline completo de entrenamiento:
- Ejecuta todos los pasos automáticamente
- Guarda modelo y metadatos
- Genera reportes de evaluación

```python
from app.ml.training_pipeline import TrainingPipeline

pipeline = TrainingPipeline(data_path='data.parquet')
metrics = pipeline.run_complete_pipeline()
```

### PredictionPipeline

Pipeline completo de predicción/inferencia:
- Carga modelo entrenado automáticamente
- Maneja preprocesamiento de texto
- Retorna predicciones estructuradas

```python
from app.ml.prediction_pipeline import PredictionPipeline

# Cargar pipeline (automáticamente usa el modelo más reciente)
pipeline = PredictionPipeline()

# Predicción individual
result = pipeline.predict_text("Texto a analizar")
# → {'text': '...', 'prediction': 1, 'label': 'Depresión', 'probability': 0.85, 'confidence': 0.92}

# Predicción en batch (eficiente)
results = pipeline.predict_batch(["texto1", "texto2", "texto3"])

# Usar modelo específico
pipeline = PredictionPipeline(model_path="data/trained_models/mi_modelo.pkl")
```

## 📊 Datos de Entrada

### Formato del Parquet

```json
{
  "chat": [
    {
      "role": "system",
      "content": "Actúa como psicólogo..."
    },
    {
      "role": "user",
      "content": "Me siento muy triste..."
    },
    {
      "role": "assistant",
      "content": "Entiendo cómo te sientes..."
    }
  ]
}
```

## 📈 Métricas y Evaluación

El modelo multi-etiqueta genera métricas **por condición**:

### Métricas por Condición (Depresión / Ansiedad)
- **Accuracy**: Precisión general
- **Precision**: Predicciones positivas correctas
- **Recall**: Casos positivos detectados
- **F1-Score**: Media armónica precision/recall
- **Confusion Matrix**: Matriz de confusión

### Métricas Globales Multi-Label
- **Exact Match**: Ambas predicciones correctas
- **Hamming Loss**: Proporción de etiquetas incorrectas
- **F1-Score Promedio**: Media de F1 por condición

## 🎯 Resultados Esperados

Con el dataset de 1,000 conversaciones (multi-label):

| Condición | Accuracy | Precision | Recall | F1-Score |
|-----------|----------|-----------|--------|----------|
| Depresión | ~75-85%  | ~70-80%   | ~65-75%| ~70-77%  |
| Ansiedad  | ~70-80%  | ~65-75%   | ~60-70%| ~65-72%  |

| Métrica Global | Valor Esperado |
|----------------|----------------|
| Exact Match    | ~60-70%        |
| Hamming Loss   | ~0.15-0.25     |
| F1 Promedio    | ~68-75%        |

*Nota: Resultados varían según calidad de etiquetas heurísticas*

## 🔬 Mejoras Futuras

1. **Mejor etiquetado**: Usar anotaciones manuales de profesionales
2. ~~**Multi-clase**: Detectar múltiples trastornos~~ ✅ Implementado (depresión + ansiedad)
3. **Más trastornos**: Agregar PTSD, bipolar, etc. (arquitectura escalable)
4. **Fine-tuning**: Ajustar RoBERTa al dominio de salud mental
5. **Ensemble**: Combinar múltiples modelos
6. **Explicabilidad**: SHAP values, LIME para interpretar predicciones

## 📝 Notas Importantes

- El modelo usa **detección automática de keywords** para etiquetas iniciales
- Se recomienda validar con profesionales de salud mental
- Los resultados NO reemplazan diagnóstico profesional
- Cumple con ética y privacidad de datos médicos

## 🛠️ Troubleshooting

### Error de memoria

```bash
# Reducir batch size
python train_model.py --batch-size 8
```

### CUDA no disponible

```bash
# El modelo detecta automáticamente y usa CPU
# Para forzar CPU:
export CUDA_VISIBLE_DEVICES=""
```

### Modelo muy grande

```bash
# Usar modelo BERT más pequeño
python train_model.py --bert-model distilbert-base-multilingual-cased
```

### Crash en macOS (Segmentation Fault)

```bash
# El script train_model.py ya incluye el fix
# Si usas el modelo directamente en otros scripts:
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

## 📚 Referencias

- [BERT Paper](https://arxiv.org/abs/1810.04805)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Transformers Library](https://huggingface.co/docs/transformers)
