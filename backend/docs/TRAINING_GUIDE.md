# 🎓 Guía de Entrenamiento - Modelo BERT + XGBoost

Guía paso a paso para entrenar el modelo de detección de depresión.

## 📋 Prerrequisitos

### 1. Verificar datos

```bash
# Ver estructura del dataset
python read_parquet.py --rows 5
```

Debe tener:
- ✅ 1,000 conversaciones
- ✅ Columna `chat` con formato JSON
- ✅ Roles: system, user, assistant

### 2. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias incluyendo:
- `torch` - PyTorch para BERT
- `transformers` - Modelos BERT de Hugging Face
- `xgboost` - Algoritmo de clasificación
- `scikit-learn` - Métricas y utilidades ML
- `pandas`, `numpy`, `pyarrow` - Procesamiento de datos
- `tqdm`, `matplotlib`, `seaborn` - Utilidades y visualización

## 🚀 Entrenamiento Rápido

### ⚠️ IMPORTANTE: Fix para macOS (OpenMP)

Si estás en macOS, el script **ya incluye el fix automático** para evitar crashes. Sin embargo, si experimentas que el script se queda colgado al finalizar, ejecuta esto antes:

```bash
# Cargar variables de entorno (solo para macOS)
source .envrc
```

O instala `direnv` para que se carguen automáticamente:
```bash
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
direnv allow
```

### Opción 1: Entrenamiento Básico (Recomendado para empezar)

```bash
cd backend
source .venv/bin/activate
python train_model.py
```

Esto usará configuración por defecto:
- Modelo BERT: `dccuchile/bert-base-spanish-wwm-cased`
- Dataset: `data/datasets/train-00000-of-00001.parquet`
- Train/Val/Test split: 70%/10%/20%
- XGBoost: 100 estimators, depth 6

**Tiempo estimado**: 15-30 minutos (depende del hardware)

**⚠️ Si el script se queda colgado al final**: Presiona `Ctrl+C`. El modelo ya fue guardado correctamente. Este es un bug conocido de OpenMP en macOS.

### Opción 2: Entrenamiento Personalizado

```bash
cd backend
python train_model.py \
    --bert-model dccuchile/bert-base-spanish-wwm-cased \
    --n-estimators 200 \
    --max-depth 8 \
    --batch-size 32 \
    --learning-rate 0.05
```

## ⚙️ Configuración Avanzada

### Parámetros disponibles

| Parámetro | Descripción | Default | Rango recomendado |
|-----------|-------------|---------|-------------------|
| `--data-path` | Ruta al parquet | `data/datasets/train-00000...` | - |
| `--bert-model` | Modelo BERT | `dccuchile/bert-base-spanish...` | Ver modelos abajo |
| `--batch-size` | Tamaño de batch | 16 | 8-32 (según RAM/GPU) |
| `--max-length` | Max tokens BERT | 512 | 128-512 |
| `--n-estimators` | Árboles XGBoost | 100 | 50-300 |
| `--max-depth` | Profundidad árboles | 6 | 3-10 |
| `--learning-rate` | Tasa aprendizaje | 0.1 | 0.01-0.3 |
| `--test-size` | % test | 0.2 | 0.1-0.3 |
| `--val-size` | % validación | 0.1 | 0.05-0.15 |

### Modelos BERT recomendados

**Para español:**
```bash
# BETO - BERT español (recomendado)
--bert-model dccuchile/bert-base-spanish-wwm-cased

# RoBERTa español
--bert-model PlanTL-GOB-ES/roberta-base-bne

# mBERT - Multilingüe
--bert-model bert-base-multilingual-cased
```

**Para mejor rendimiento (pero más lento):**
```bash
# BERT large español
--bert-model dccuchile/bert-large-spanish-wwm-cased
```

**Para hardware limitado:**
```bash
# DistilBERT - Más rápido y ligero
--bert-model distilbert-base-multilingual-cased
```

## 📊 Proceso de Entrenamiento

El script ejecuta 6 pasos:

### PASO 1: Preparación de datos (30 seg)
```
📦 PASO 1: Preparación de datos
✅ Cargadas 1,000 conversaciones
Procesadas 100/1000 conversaciones...
Procesadas 200/1000 conversaciones...
...
✅ Total procesado: 1,000 conversaciones
   • Con indicadores de depresión: 450
   • Sin indicadores: 550
```

### PASO 2: Generación de embeddings (5-15 min)
```
🧠 PASO 2: Generación de embeddings BERT
🔧 Inicializando BERT Encoder...
   • Modelo: dccuchile/bert-base-spanish-wwm-cased
   • Dispositivo: cuda / cpu
Generando embeddings BERT: 100%|████████| 63/63 [05:23<00:00]
✅ Generados 1,000 embeddings
   • Dimensión: 768
```

### PASO 3: División de datos (1 seg)
```
✂️  PASO 3: División de datos
   • Training set:   700 samples
   • Validation set: 100 samples
   • Test set:       200 samples
```

### PASO 4: Entrenamiento XGBoost (1-3 min)
```
🚀 PASO 4: Entrenamiento del clasificador XGBoost
[0] validation_0-logloss:0.65432
[10] validation_0-logloss:0.54321
...
[99] validation_0-logloss:0.42156
```

### PASO 5: Evaluación (5 seg)
```
📊 PASO 5: Evaluación en conjunto de prueba
📊 Métricas en Test:
   • Accuracy:  0.7850
   • Precision: 0.7421
   • Recall:    0.7234
   • F1-Score:  0.7326

   Matriz de Confusión:
   [[85 15]
    [28 72]]
```

### PASO 6: Guardando modelo (1 seg)
```
💾 PASO 6: Guardando modelo
💾 Modelo guardado en: data/trained_models/depression_bert_xgboost_20241118_143052.pkl
   • Modelo: .../depression_bert_xgboost_20241118_143052.pkl
   • Metadata: .../depression_bert_xgboost_20241118_143052_metadata.json
```

## 📁 Archivos Generados

Después del entrenamiento encontrarás en `backend/data/trained_models/`:

```
depression_bert_xgboost_TIMESTAMP.pkl          # Modelo XGBoost
depression_bert_xgboost_TIMESTAMP_metadata.json # Metadatos y métricas
```

### Contenido del metadata.json

```json
{
  "model_name": "depression_bert_xgboost_20241118_143052",
  "created_at": "2024-11-18T14:30:52",
  "bert_model": "dccuchile/bert-base-spanish-wwm-cased",
  "embedding_dim": 768,
  "n_samples": 1000,
  "n_train": 700,
  "n_val": 100,
  "n_test": 200,
  "metrics": {
    "train": {
      "accuracy": 0.9571,
      "precision": 0.9523,
      "recall": 0.9621,
      "f1_score": 0.9572
    },
    "val": {
      "accuracy": 0.8200,
      "precision": 0.8056,
      "recall": 0.7907,
      "f1_score": 0.7981
    },
    "test": {
      "accuracy": 0.7850,
      "precision": 0.7421,
      "recall": 0.7234,
      "f1_score": 0.7326,
      "confusion_matrix": [[85, 15], [28, 72]]
    }
  },
  "xgboost_params": {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1
  }
}
```

## 🎯 Interpretación de Métricas

### Accuracy (Exactitud)
- **Qué es**: % de predicciones correctas
- **Bueno**: > 75%
- **Excelente**: > 85%

### Precision (Precisión)
- **Qué es**: De los casos predichos como depresión, cuántos realmente lo son
- **Bueno**: > 70%
- **Importante**: Minimiza falsos positivos

### Recall (Sensibilidad)
- **Qué es**: De los casos reales de depresión, cuántos detectamos
- **Bueno**: > 70%
- **Importante**: Minimiza falsos negativos

### F1-Score
- **Qué es**: Balance entre Precision y Recall
- **Bueno**: > 70%
- **Ideal**: Cercano a ambas métricas

### Matriz de Confusión

```
              Predicho: No    Predicho: Sí
Real: No      [[TN=85         FP=15]
Real: Sí       [FN=28         TP=72]]
```

- **TN (True Negative)**: Correctamente identificó NO depresión
- **TP (True Positive)**: Correctamente identificó depresión
- **FP (False Positive)**: Falsa alarma (predijo depresión cuando no había)
- **FN (False Negative)**: Caso perdido (no detectó depresión cuando sí había)

## ⚠️ Troubleshooting

### Error: Out of Memory

```bash
# Solución 1: Reducir batch size
python train_model.py --batch-size 8

# Solución 2: Reducir max_length
python train_model.py --max-length 256

# Solución 3: Usar modelo más pequeño
python train_model.py --bert-model distilbert-base-multilingual-cased
```

### Error: CUDA not available

```bash
# El modelo automáticamente usa CPU
# Si quieres forzar CPU:
export CUDA_VISIBLE_DEVICES=""
python train_model.py
```

### Error: Segmentation Fault / Crash en macOS

```bash
# Si experimentas crashes con SIGSEGV en macOS, es un conflicto OpenMP
# El script train_model.py ya incluye el fix automático
# Pero si usas otros scripts, establece:
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=4

# O carga las variables desde .envrc:
source .envrc
python train_model.py
```

### Dataset muy desbalanceado

```bash
# El preprocessor usa keywords para etiquetado inicial
# Para mejorar, puedes:
# 1. Ajustar keywords en preprocessor.py
# 2. Usar etiquetas manuales (mejora significativa)
```

## ✅ Validación y Testing del Modelo

Después de entrenar, es crucial validar que el modelo funciona correctamente. Usa el script `test_model.py`:

### Testear conversaciones aleatorias

```bash
cd backend

# Testear 5 conversaciones aleatorias (default)
python test_model.py

# Testear 10 conversaciones aleatorias
python test_model.py --random 10
```

**Salida esperada:**
```
📝 ANÁLISIS DE CONVERSACIÓN
================================================================================

💬 Texto analizado (245 caracteres):
   me he sentido muy triste últimamente y abrumada. tengo mucho estrés...

🎯 Resultado: DEPRESIÓN DETECTADA ⚠️

📊 Probabilidades:
   • Sin depresión: 23.45%
   • Con depresión: 76.55%
   • Confianza:     76.55%

🔍 Comparación:
   • Modelo predice:     Depresión
   • Heurística detecta: Depresión
   • Coinciden:          ✅ Sí
```

### Testear conversaciones específicas

```bash
# Testear conversaciones en índices específicos del dataset
python test_model.py --indices 0 5 10 15 20
```

Útil para:
- Verificar casos específicos que conoces
- Debuggear predicciones incorrectas
- Analizar tipos de conversaciones

### Testear texto personalizado

```bash
# Analizar un texto directo
python test_model.py --text "Me siento muy triste y sin energía para hacer nada"

# Analizar conversación más compleja
python test_model.py --text "Últimamente he tenido insomnio y ansiedad constante"
```

### Evaluación completa del dataset

```bash
# Evaluar el modelo en TODAS las conversaciones del dataset
python test_model.py --full-test
```

**Salida esperada:**
```
📊 EVALUACIÓN COMPLETA DEL DATASET
================================================================================

📈 Métricas generales:
   • Total de conversaciones: 1000
   • Accuracy:  78.50%
   • Precision: 74.21%
   • Recall:    72.34%
   • F1-Score:  73.26%

📋 Matriz de Confusión:
                 Predicho: No    Predicho: Sí
   Real: No            450              50
   Real: Sí             65             435

⚠️  Análisis de errores:
   • Falsos positivos: 50 (modelo predice depresión pero no hay)
   • Falsos negativos: 65 (modelo NO predice depresión pero sí hay)
```

### Usar modelo específico

```bash
# Testear con un modelo entrenado específico
python test_model.py --model-path data/trained_models/depression_bert_xgboost_20241118.pkl

# Combinado con otras opciones
python test_model.py --model-path data/trained_models/modelo_antiguo.pkl --random 20
```

### Casos de uso comunes

**1. Verificación rápida después de entrenar:**
```bash
python test_model.py --random 10
```

**2. Validación exhaustiva:**
```bash
python test_model.py --full-test
```

**3. Testing de casos edge:**
```bash
python test_model.py --indices 0 100 200 500 999
```

**4. Demo para stakeholders:**
```bash
python test_model.py --text "Texto de ejemplo que quieres mostrar"
```

## 🔄 Próximos Pasos

1. **Validar el modelo entrenado**
   ```bash
   # Testear conversaciones aleatorias
   python test_model.py --random 10

   # Evaluación completa
   python test_model.py --full-test
   ```

2. **Analizar resultados**
   ```bash
   # Ver métricas guardadas
   cat data/trained_models/*_metadata.json | jq .metrics
   ```

3. **Usar el modelo para predicciones**
   ```python
   # Ver app/ml/README.md para ejemplos de integración
   ```

4. **Integrar con la API**
   ```python
   # Crear endpoint en FastAPI/Flask
   # Ver documentación en docs/api/ml/
   ```

5. **Mejorar el modelo**
   - Obtener etiquetas manuales de profesionales
   - Aumentar tamaño del dataset
   - Probar diferentes hiperparámetros
   - Fine-tune BERT en el dominio
   - Analizar falsos positivos/negativos para mejorar

## 📚 Recursos Adicionales

- [Documentación del módulo ML](../app/ml/README.md)
- [Script de lectura de parquet](../data/datasets/README_PARQUET.md)
- [Documentación de datasets](../data/datasets/README.md)
- [Backend API](../README.md)
