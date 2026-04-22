# Mental Health Predictor

Sistema web de análisis predictivo de depresión y ansiedad mediante NLP, diseñado para centros de atención psicológica.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura](#estructura)
- [Base de Datos](#base-de-datos)
- [Documentación](#documentación)
- [Autores](#autores)

## Descripción

Plataforma que permite a pacientes registrar notas diarias sobre su estado emocional y a especialistas monitorear evaluaciones automáticas generadas por modelos de Machine Learning.

**Componentes:**
- **Portal de Pacientes**: cuestionario diario de 4 preguntas + transcripción de audio
- **Portal de Especialistas**: gestión de pacientes, historias clínicas y evaluaciones ML con auditoría
- **ML API**: microservicio Python con RoBERTa Biomedical + Logistic Regression para detección de depresión y ansiedad

## Tecnologías

### Frontend + CRUD
- SvelteKit 2.0, Svelte 4, TailwindCSS
- postgres.js, Bcrypt, Zod
- PostgreSQL 17.6 (GMT-5 Lima)

### ML API (microservicio Python)
- FastAPI
- RoBERTa Biomedical (`PlanTL-GOB-ES/roberta-base-biomedical-es`) + Logistic Regression
- Faster-Whisper (transcripción de audio)
- PyTorch, scikit-learn

## Arquitectura

```
┌──────────────────────┐
│   Navegador Web      │
│  (Cliente Svelte)    │
└──────────┬───────────┘
           │
┌──────────▼────────────────────────────────────────┐
│         SvelteKit Server (Puerto 5173)            │
│  Frontend SSR + API Routes (CRUD)                 │
│  • /login, /paciente/notas, /pacientes, ...       │
│  • API: /api/pacientes, /api/respuestas, ...      │
└───────────┬──────────────────────────────┬────────┘
            │                              │
            │ Consultas SQL                │ HTTP POST
            │                              │ (evaluación)
┌───────────▼────────────┐    ┌───────────▼─────────────┐
│  PostgreSQL Database   │    │  Python ML API (8000)   │
│  (Puerto 5432)         │    │  RoBERTa Embeddings     │
│                        │    │  Logistic Regression    │
│ • paciente             │    │  Whisper Transcripción  │
│ • especialista         │    │                         │
│ • historia_clinica     │◄───┤  Guarda evaluacion_ml   │
│ • paciente_respuesta   │    └─────────────────────────┘
│ • evaluacion_ml        │
└────────────────────────┘
```

## Instalación

### Requisitos

- Node.js 18+
- Python 3.11 o 3.12
- PostgreSQL 17+ (corriendo en puerto 5432)

### 1. Base de datos

```bash
psql -U postgres -c "CREATE DATABASE salud_mental_app;"
psql -U postgres -d salud_mental_app -f docs/database/schema.sql
```

### 2. ML API (Python)

```bash
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Entrenar el modelo (requerido antes de iniciar la API)
python scripts/cluster_and_label.py
python scripts/train.py       # ~20-60 min en CPU, descarga RoBERTa ~500 MB

# Iniciar
run_api.bat                   # Windows
```

API disponible en `http://localhost:8000` · Docs en `/docs`

### 3. Frontend (SvelteKit)

```bash
cd frontend
npm install
cp .env.example .env
# Configurar DATABASE_URL, PUBLIC_ML_API_URL y AUTH_SECRET en .env
npm run dev
```

Aplicación disponible en `http://localhost:5173`

## Uso

### Flujo de trabajo

1. Especialista crea paciente con DNI y datos personales
2. Especialista crea historia clínica con antecedentes y medicaciones
3. Paciente ingresa con DNI/password y completa cuestionario diario (máx. 2 por día)
4. Sistema ML procesa respuestas en segundo plano (asíncrono)
5. Especialista revisa evaluaciones con probabilidades y palabras clave detectadas
6. Especialista puede reprocesar respuestas si se actualiza el modelo

## Estructura

```
upc_mental-health-predictor/
├── frontend/              # SvelteKit — Frontend + API CRUD
│   └── README.md
├── backend/               # Python FastAPI — ML API
│   └── README.md
└── docs/
    └── database/
        └── schema.md      # Esquema completo de PostgreSQL
```

## Base de Datos

PostgreSQL 17.6 · Timezone: GMT-5 (America/Lima) · Esquema completo en [`docs/database/schema.md`](docs/database/schema.md)

Tablas principales: `paciente`, `especialista`, `historia_clinica`, `paciente_respuesta`, `evaluacion_ml`

## Documentación

- [Frontend](frontend/README.md) — SvelteKit, instalación, rutas, autenticación, tecnologías
- [Backend ML](backend/README.md) — FastAPI, entrenamiento del modelo, endpoints

## Autores

Universidad Peruana de Ciencias Aplicadas (UPC) — Proyecto de investigación en sistemas de salud mental

---

> Este sistema es una herramienta de apoyo al diagnóstico y NO reemplaza el criterio clínico de profesionales de la salud mental.
