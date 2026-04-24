# Módulo ML — Mental Health Predictor

Pipeline de predicción de depresión y ansiedad basado en **RoBERTa Biomedical + Logistic Regression**.

## Arquitectura

El pipeline tiene dos fases: **entrenamiento** (offline) e **inferencia** (en cada request).

### Fase de entrenamiento (`scripts/train.py`)

```
Dataset .parquet
       ↓
cluster_and_label.py    asigna etiquetas por keyword score
       ↓                → genera labeled_dataset.csv
       ↓
TransformerEncoder      tokeniza y codifica cada texto con RoBERTa
       ↓                → embeddings L2-normalizados de 768 dimensiones
       ↓
build_features()        concatena embeddings + 2 keyword scores normalizados
       ↓                → feature vector final de 770 dimensiones
       ↓
LogisticRegression ×2   entrena un clasificador binario por condición
  clf_depression         calibrado con CalibratedClassifierCV (isotonic, cv=5)
  clf_anxiety            idem
       ↓
  mental_health_lr_FECHA.pkl   guardado en data/trained_models/
```

### Fase de inferencia (`prediction_pipeline.py`)

```
4 respuestas del paciente
       ↓
  clean_text()          normaliza unicode, elimina ruido
       ↓
TransformerEncoder      tokeniza + forward pass RoBERTa + CLS pooling
  .encode_texts()       → embedding 768-dim, normalizado L2
       ↓
_build_features()       embedding + dep_score/max + anx_score/max
       ↓                → vector 770-dim  (mismo formato que entrenamiento)
       ↓
clf_depression          predict_proba → sem_dep  (señal semántica)
clf_anxiety             predict_proba → sem_anx
       ↓
_keyword_score()        cuenta frases/palabras del texto contra keywords.py
                        pesos: frases exactas = 2 · palabras sueltas = 1
       ↓
_score_to_prob()        combina ambas señales:
                          sigmoid(keyword_score) × 0.75
                        + sem_prob              × 0.25
       ↓
  prob_depression ≥ 0.38  →  "Depresión detectada"
  prob_anxiety    ≥ 0.38  →  "Ansiedad detectada"
  (condiciones independientes — ambas pueden ser True)
```

### Por qué dos clasificadores independientes

Depresión y ansiedad no son mutuamente excluyentes — un paciente puede presentar ambas simultáneamente. Entrenar un clasificador binario por condición (en lugar de uno multi-clase) permite que cada uno optimice su propia curva de decisión sin que las clases compitan entre sí.

## Archivos

| Archivo | Rol |
|---|---|
| `keywords.py` | Fuente única de keywords con pesos (depresión y ansiedad) |
| `prediction_pipeline.py` | Pipeline de inferencia (carga modelo, predice) |
| `transformer_encoder.py` | Embeddings con RoBERTa via `AutoTokenizer` + `AutoModel` |
| `preprocessor.py` | Limpieza de texto y detección de keywords para la UI |
| `text_processing.py` | Función `clean_text` (normalización básica) |
| `multi_label_classifier.py` | Clasificador multi-etiqueta (usado como referencia) |
| `data_loaders/` | Loaders para Parquet y CSV |

## Cómo funciona el score de probabilidad

La probabilidad final combina dos señales:

- **75% keyword score**: suma ponderada de frases/palabras encontradas en el texto (pesos en `keywords.py`)
- **25% señal semántica**: probabilidad del clasificador RoBERTa + Logistic Regression

```
score=0  → ~8-12%   (sin keywords)
score=2  → ~38-42%  (una frase de peso 2)
score=4  → ~62-68%
score=6  → ~78-83%
score=10 → ~88-92%
```

Umbral de detección: `≥ 0.38` para ambas condiciones.

## Modificar keywords

Edita únicamente `keywords.py`. Todos los módulos (pipeline, entrenamiento, etiquetado) importan desde ahí. Después de cambiar keywords, re-entrena el modelo:

```bash
python scripts/cluster_and_label.py
python scripts/train.py
```

## Cambiar el modelo de embeddings

En `keywords.py` no hay modelo definido — el modelo está en `prediction_pipeline.py` y `scripts/train.py`:

```python
BERT_MODEL = 'PlanTL-GOB-ES/roberta-base-biomedical-es'
```

Cambia la constante en ambos archivos y re-entrena.
