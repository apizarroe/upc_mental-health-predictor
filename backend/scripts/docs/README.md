# Guía de Entrenamiento — Mental Health Predictor

Pipeline: **RoBERTa Biomedical + Logistic Regression**.

## Prerrequisitos

### 1. Verificar datos

El dataset debe estar en `data/datasets/train-00000-of-00001.parquet`. Debe contener:

- Al menos 1 000 conversaciones
- Columna `chat` con formato JSON (roles: `system`, `user`, `assistant`)

### 2. Dependencias

```bash
cd backend
pip install -r requirements.txt
```

## Entrenamiento

### Paso 1: Etiquetar el dataset

```bash
python scripts/cluster_and_label.py
```

Asigna etiquetas (`depression`, `anxiety`, `neutral`) a cada conversación según el keyword score ponderado. Genera `data/datasets/labeled_dataset.csv`.

| Argumento | Default | Descripción |
|---|---|---|
| `--data-path` | `data/datasets/train-00000-of-00001.parquet` | Dataset fuente |
| `--output` | `data/datasets/labeled_dataset.csv` | CSV etiquetado |
| `--threshold` | `2.0` | Score mínimo para activar una condición |

Si más del 70% queda como `neutral`, baja `--threshold` a `1`. Si menos del 10%, súbelo a `3`.

### Paso 2: Entrenar el modelo

```bash
python scripts/train.py
```

Descarga RoBERTa Biomedical (~500 MB la primera vez). En CPU tarda entre 20 y 60 minutos.

| Argumento | Default | Descripción |
|---|---|---|
| `--data-path` | `data/datasets/labeled_dataset.csv` | Dataset etiquetado |
| `--output-dir` | `data/trained_models` | Directorio de salida |
| `--test-size` | `0.2` | Proporción del conjunto de test |
| `--C` | `1.0` | Regularización Logistic Regression |

## Proceso de entrenamiento

El script ejecuta 5 pasos:

### Paso 1 — Carga el dataset etiquetado

```
[1/5] Cargando dataset: data/datasets/labeled_dataset.csv
      1000 ejemplos cargados
      Distribución:
        depression  : 320 (32.0%)
        anxiety     : 280 (28.0%)
        neutral     : 400 (40.0%)
```

### Paso 2 — Genera embeddings con RoBERTa (~5–15 min)

```
[2/5] Generando embeddings con PlanTL-GOB-ES/roberta-base-biomedical-es
      Shape: (1000, 768)
```

### Paso 3 — Construye features combinadas

```
[3/5] Construyendo features combinadas
      Shape features: (1000, 770)  (embeddings=768, keyword_scores=2)
```

Los 770 valores corresponden a: 768 dimensiones de embedding RoBERTa + score de depresión normalizado + score de ansiedad normalizado.

### Paso 4 — Entrena dos clasificadores binarios independientes

```
[4/5] Entrenando clasificadores binarios (C=1.0)
      Train: 800  |  Test: 200
  depression: accuracy=0.8400  F1=0.8123
  anxiety:    accuracy=0.8150  F1=0.7891
```

Cada clasificador es un `LogisticRegression` calibrado con `CalibratedClassifierCV` (isotonic, cv=5). Se entrenan de forma independiente porque ambas condiciones pueden coexistir.

### Paso 5 — Guarda el modelo

```
[5/5] Guardando modelo
  Modelo:   data/trained_models/mental_health_lr_20260421_120000.pkl
  Metadata: data/trained_models/mental_health_lr_20260421_120000_metadata.json
```

## Archivos generados

```
data/trained_models/
├── mental_health_lr_TIMESTAMP.pkl           # Clasificadores (dict: depression + anxiety)
└── mental_health_lr_TIMESTAMP_metadata.json # Métricas e hiperparámetros
```

Estructura del metadata:

```json
{
  "model_type": "logistic_regression_binary_pair",
  "bert_model": "PlanTL-GOB-ES/roberta-base-biomedical-es",
  "feature_dim": 770,
  "embedding_dim": 768,
  "training_samples": 800,
  "test_samples": 200,
  "hyperparams": { "C": 1.0, "class_weight": "balanced", "solver": "lbfgs" },
  "metrics": {
    "f1_depression": 0.8123,
    "f1_anxiety": 0.7891,
    "f1_weighted": 0.8007,
    "accuracy_depression": 0.8400,
    "accuracy_anxiety": 0.8150
  }
}
```

La API carga automáticamente el `.pkl` más reciente por timestamp al iniciar.

## Interpretar las métricas

### Accuracy (Exactitud)

Porcentaje de predicciones correctas sobre el total.

- Aceptable: > 75%
- Bueno: > 85%

### Precision (Precisión)

De los casos que el modelo predice como positivos, cuántos realmente lo son. Alta precisión minimiza falsos positivos (alarmas innecesarias).

- Aceptable: > 70%

### Recall (Sensibilidad)

De los casos realmente positivos, cuántos detecta el modelo. Alto recall minimiza falsos negativos (casos perdidos). En salud mental, este es el indicador más crítico.

- Aceptable: > 70%

### F1-Score

Media armónica entre Precision y Recall. Es la métrica principal cuando las clases están desbalanceadas.

- Aceptable: > 70%

### Matriz de Confusión

```
                  Predicho: No    Predicho: Sí
Real: No          TN              FP
Real: Sí          FN              TP
```

- **FP (Falso Positivo)**: predice condición cuando no la hay
- **FN (Falso Negativo)**: no detecta condición cuando sí la hay — el error más costoso en este dominio

## Validar el modelo

```bash
# Texto libre
python scripts/test.py --text "Me siento muy triste y sin energía"

# Conversaciones aleatorias del dataset
python scripts/test.py --random 10

# Evaluación completa (depresión + ansiedad)
python scripts/test.py --full-test

# Solo una condición
python scripts/test.py --full-test --condition depression
python scripts/test.py --full-test --condition anxiety

# Modelo específico
python scripts/test.py --model-path data/trained_models/mental_health_lr_20260421_120000.pkl
```

## Troubleshooting

**`No se encontró labeled_dataset.csv`** — ejecutar `cluster_and_label.py` antes de `train.py`.

**Más del 70% neutral en la distribución** — bajar `--threshold` a `1` en `cluster_and_label.py` y repetir el paso 1.

**Memoria insuficiente al generar embeddings** — reducir `batch_size` en la llamada a `TransformerEncoder` dentro de `scripts/train.py` (default: 8).

**La API sigue usando el modelo anterior tras reentrenar** — reiniciar la API. Carga el modelo más reciente al iniciar, no en caliente.

**F1 muy bajo (< 0.60)** — revisar la distribución de labels. Si hay muy pocos positivos, bajar `--threshold` para generar más ejemplos etiquetados o ajustar las keywords en `app/ml/keywords.py`.
