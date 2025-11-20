# Dataset de Entrevistas para Entrenamiento BERT + XGBoost

## 📄 Descripción

Este directorio contiene los datasets utilizados para el entrenamiento del modelo BERT + XGBoost para análisis de salud mental basado en entrevistas de pacientes.

## 📁 Archivos Disponibles

### Formato Parquet (Principal)

- **train-00000-of-00001.parquet**: Dataset principal de entrenamiento
  - Formato: Apache Parquet
  - Registros: 1,000 conversaciones
  - Columnas: 1 columna (`chat`) con conversaciones anidadas

### 📄 Ejemplos CSV (Para Testing)

- **example_simple.csv**: CSV simple con una columna de texto
  - Formato: CSV con columna `text`
  - Registros: 10 conversaciones
  - Uso: Probar `CSVTextLoader`

- **example_patient_messages.csv**: CSV con múltiples mensajes por paciente
  - Formato: CSV con columnas `patient_id`, `message`, `timestamp`
  - Registros: 13 mensajes de 5 pacientes
  - Uso: Probar `CSVPatientLoader`

## 📊 Estructura de Datos

Cada registro en el dataset contiene:

```json
{
  "chat": [
    {
      "role": "system",
      "content": "Actúa como un psicólogo especializado..."
    },
    {
      "role": "user",
      "content": "Últimamente me he sentido muy triste..."
    },
    {
      "role": "assistant",
      "content": "Hola, estoy aquí para escucharte..."
    },
    ...
  ]
}
```

### Roles en las conversaciones:
- **system**: Instrucciones/contexto del sistema (prompt inicial)
- **user**: Mensajes del paciente
- **assistant**: Respuestas del psicólogo/terapeuta

## 🔧 Uso del Script de Lectura

Desde la raíz del proyecto, puedes usar el script `read_parquet.py` para explorar el dataset.

### 🚀 Inicio Rápido

**1. Activar entorno virtual (si aún no está activado)**

```bash
source .venv/bin/activate
```

**2. Leer el dataset**

```bash
# Ver primeras 5 conversaciones (recomendado para inicio)
python read_parquet.py --rows 5

# Ver primeras 10 conversaciones
python read_parquet.py --rows 10

# Ver TODAS las conversaciones (1000 total)
python read_parquet.py --rows 0
```

### 📋 Ejemplos Avanzados

```bash
# Especificar archivo diferente
python read_parquet.py --file backend/data/datasets/otro_archivo.parquet

# Exportar todo el dataset a CSV
python read_parquet.py --rows 0 --export-csv datos_exportados.csv

# Ver columnas específicas
python read_parquet.py --columns chat
```

### ⚙️ Opciones Disponibles

- `--file`: Ruta al archivo parquet (default: backend/data/datasets/train-00000-of-00001.parquet)
- `--rows`: Número de filas a mostrar (0 = todas, default: 10)
- `--columns`: Columnas específicas separadas por comas
- `--export-csv`: Exportar a CSV

### 🎯 Estructura de cada Conversación

```
📝 CONVERSACIÓN #1:
================================================================================

   ⚙️  SYSTEM:
      Actúa como un psicólogo especializado en consejos breves...

   👤 USER:
      Últimamente me he sentido muy triste y abrumada...

   🤖 ASSISTANT:
      Hola, estoy aquí para escucharte y apoyarte...

   👤 USER:
      Recientemente obtuve un ascenso en el trabajo...

   🤖 ASSISTANT:
      Puedo entender cómo puede ser abrumador...
```

### 🛠️ Troubleshooting

Si obtienes error `ModuleNotFoundError: No module named 'pandas'`:

```bash
source .venv/bin/activate
pip install pandas pyarrow
```

### 📖 Ejemplo de Salida

El script muestra:

1. ✅ **Información del Dataset**: Filas, columnas, tamaño en memoria
2. ✅ **Columnas Disponibles**: Tipos de datos y valores nulos
3. ✅ **Estadísticas Descriptivas**: Resumen estadístico
4. ✅ **Conversaciones Expandidas**: Formato legible con emojis por rol
5. ✅ **Valores Únicos**: Análisis de columnas categóricas
6. ✅ **Valores Nulos**: Detección de datos faltantes

## 📈 Información del Dataset

- **Total de conversaciones**: 1,000
- **Idiomas**: Español e Inglés (mixto)
- **Tamaño en memoria**: ~0.11 MB
- **Valores nulos**: 0 (dataset completo)

## 🎯 Propósito

Este dataset se utiliza para:

1. **Entrenamiento de BERT**: Comprensión del contexto emocional en conversaciones
2. **Entrenamiento de XGBoost**: Clasificación de estados emocionales/psicológicos
3. **Análisis de patrones**: Identificación de temas comunes en salud mental

## 🔒 Seguridad

⚠️ **IMPORTANTE**:
- Este directorio está en `.gitignore` para proteger datos sensibles
- NO subir archivos `.parquet`, `.csv` o `.json` al repositorio
- Los datos son para uso interno de entrenamiento solamente

## 📝 Notas

- Las conversaciones siguen un formato de terapia psicológica breve
- Cada conversación incluye múltiples turnos de interacción
- El contexto del sistema define el comportamiento esperado del asistente

## 🧪 Cómo Usar los Archivos CSV de Ejemplo

### Ejemplo 1: CSV Simple

```python
from app.ml.data_loaders import CSVTextLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# Cargar datos del CSV simple
loader = CSVTextLoader("data/datasets/example_simple.csv", text_column="text")
texts = loader.extract_texts()

# Procesar
clean_texts = [clean_text(t) for t in texts]

# Etiquetar
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]

print(f"Total de conversaciones: {len(texts)}")
print(f"Con indicadores de depresión: {sum(labels)}")
```

### Ejemplo 2: CSV con Mensajes por Paciente

```python
from app.ml.data_loaders import CSVPatientLoader
from app.ml.text_processing import clean_text
from app.ml.labeling import DepressionDetector

# Cargar y agrupar por paciente
loader = CSVPatientLoader(
    "data/datasets/example_patient_messages.csv",
    patient_id_column="patient_id",
    message_column="message",
    timestamp_column="timestamp"
)
patient_texts = loader.load_grouped_by_patient()

# Procesar
clean_texts = [clean_text(t) for t in patient_texts]

# Etiquetar
detector = DepressionDetector()
labels = [detector.detect(t) for t in clean_texts]

print(f"Total de pacientes: {len(patient_texts)}")
print(f"Pacientes con indicadores: {sum(labels)}")
```

## 📋 Formato Esperado para CSVs Propios

### CSV Simple
```csv
text
"Tu conversación completa aquí..."
"Otra conversación..."
```

### CSV con Múltiples Mensajes
```csv
patient_id,message,timestamp
PAC001,"Primer mensaje",2025-01-01 10:00:00
PAC001,"Segundo mensaje",2025-01-01 10:05:00
PAC002,"Mensaje de otro paciente",2025-01-02 14:00:00
```

## 🛠️ Requisitos

Para leer los archivos necesitas:

```bash
pip install pandas pyarrow
```

O activar el entorno virtual del proyecto:

```bash
source .venv/bin/activate
```
