# Sistema de Apoyo al Diagnóstico Clínico de Trastornos Mentales

Sistema web de análisis predictivo de trastornos mentales mediante procesamiento de lenguaje natural (NLP) utilizando BERT, XGBoost y Random Forest, desarrollado para centros de atención psicológica.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características Principales](#características-principales)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Desarrollo](#desarrollo)
- [Testing](#testing)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Descripción

Este proyecto implementa un sistema de apoyo al diagnóstico clínico que analiza notas psicológicas de pacientes utilizando técnicas avanzadas de Machine Learning y Deep Learning. El sistema procesa texto libre de sesiones clínicas para identificar potenciales indicadores de trastornos mentales, proporcionando apoyo a profesionales de la salud mental en su proceso diagnóstico.

### Objetivo

Proporcionar una herramienta de apoyo que permita a los profesionales de la salud mental:
- Analizar notas clínicas de forma automatizada
- Identificar patrones indicativos de trastornos mentales
- Obtener predicciones basadas en modelos de IA entrenados
- Gestionar información de pacientes y especialistas de manera segura

## Características Principales

- **Análisis de Texto con BERT**: Procesamiento avanzado de lenguaje natural para comprensión contextual
- **Modelos Predictivos**: Implementación de XGBoost y Random Forest para clasificación robusta
- **Interfaz Intuitiva**: Dashboard desarrollado con SvelteKit para gestión y visualización
- **Gestión Completa CRUD**: Administración de pacientes, especialistas, sesiones y notas clínicas
- **API de Predicción**: Microservicio Python especializado en inferencia de modelos ML
- **Seguridad**: Implementación de buenas prácticas de seguridad y privacidad de datos

## Tecnologías Utilizadas

### Frontend y Backend CRUD
- **SvelteKit**: Framework full-stack para la aplicación web
- **JavaScript**: Lenguaje principal del desarrollo
- **SvelteKit Server Routes**: API routes nativas para operaciones CRUD
- **Prisma/Drizzle ORM**: Gestión de base de datos (opcional)
- **TailwindCSS**: Framework de estilos
- **Zod**: Validación de esquemas

### Backend ML (Microservicio de Predicción)
- **Python 3.9+**: Lenguaje para modelos de ML
- **FastAPI**: Framework web ligero para API de predicción
- **BERT (Transformers)**: Modelo de lenguaje pre-entrenado
- **XGBoost**: Algoritmo de gradient boosting
- **Random Forest**: Algoritmo de ensemble learning
- **scikit-learn**: Librería de machine learning
- **pandas/numpy**: Procesamiento de datos
- **uvicorn**: Servidor ASGI

### Base de Datos
- **SQLite/PostgreSQL**: Base de datos relacional
- **Better-SQLite3**: Driver para SvelteKit (si se usa SQLite)

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación multi-contenedor
- **Git**: Control de versiones

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                    │
│                     SvelteKit Pages                      │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         │ Internal API Calls            │ HTTP Requests
         │                               │
┌────────▼────────────┐         ┌────────▼──────────────┐
│   SvelteKit Server  │         │  Python ML Service    │
│   (Backend CRUD)    │         │     (FastAPI)         │
│                     │         │                       │
│  - Pacientes        │         │  - Predicción BERT    │
│  - Especialistas    │         │  - Predicción XGBoost │
│  - Sesiones         │         │  - Predicción RF      │
│  - Notas Clínicas   │◄────────┤  - Ensemble Models    │
│  - Autenticación    │  Fetch  │                       │
└────────┬────────────┘         └───────────────────────┘
         │
         │
┌────────▼────────────┐
│   Base de Datos     │
│  SQLite/PostgreSQL  │
│                     │
│  - users            │
│  - patients         │
│  - specialists      │
│  - sessions         │
│  - clinical_notes   │
│  - predictions      │
└─────────────────────┘
```

### Flujo de Trabajo

1. **Usuario** interactúa con la interfaz SvelteKit
2. **Operaciones CRUD** se manejan directamente en SvelteKit server routes
3. **Predicciones ML** se envían al microservicio Python FastAPI
4. **Resultados** se almacenan en la BD y se muestran al usuario

## Estructura del Proyecto

```
upc_mental-health-predictor/
│
├── frontend/                           # Aplicación SvelteKit (Frontend + Backend CRUD)
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/            # Componentes Svelte
│   │   │   │   ├── ui/               # Componentes UI reutilizables
│   │   │   │   │   ├── Button.svelte
│   │   │   │   │   ├── Card.svelte
│   │   │   │   │   ├── Table.svelte
│   │   │   │   │   └── Modal.svelte
│   │   │   │   └── forms/            # Formularios específicos
│   │   │   │       ├── PatientForm.svelte
│   │   │   │       ├── SpecialistForm.svelte
│   │   │   │       └── NoteForm.svelte
│   │   │   ├── stores/               # Svelte stores (estado global)
│   │   │   │   ├── auth.js
│   │   │   │   ├── patients.js
│   │   │   │   └── predictions.js
│   │   │   ├── server/               # Código del servidor
│   │   │   │   ├── db/              # Configuración de base de datos
│   │   │   │   │   ├── schema.js    # Esquema de BD
│   │   │   │   │   └── client.js    # Cliente de BD
│   │   │   │   ├── services/        # Lógica de negocio
│   │   │   │   │   ├── patients.js
│   │   │   │   │   ├── specialists.js
│   │   │   │   │   ├── sessions.js
│   │   │   │   │   └── predictions.js
│   │   │   │   └── validators/      # Validadores Zod
│   │   │   │       ├── patient.js
│   │   │   │       └── note.js
│   │   │   └── utils/               # Utilidades
│   │   │       ├── formatters.js
│   │   │       ├── validators.js
│   │   │       └── constants.js
│   │   │
│   │   ├── routes/                   # Rutas y páginas
│   │   │   ├── (app)/               # Grupo de rutas autenticadas
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── +page.svelte
│   │   │   │   ├── pacientes/
│   │   │   │   │   ├── +page.svelte           # Lista
│   │   │   │   │   ├── nuevo/
│   │   │   │   │   │   └── +page.svelte       # Crear
│   │   │   │   │   └── [id]/
│   │   │   │   │       ├── +page.svelte       # Ver/Editar
│   │   │   │   │       └── +page.server.js    # Server load
│   │   │   │   ├── especialistas/
│   │   │   │   │   ├── +page.svelte
│   │   │   │   │   ├── nuevo/
│   │   │   │   │   │   └── +page.svelte
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── +page.svelte
│   │   │   │   ├── sesiones/
│   │   │   │   │   └── +page.svelte
│   │   │   │   └── predicciones/
│   │   │   │       ├── +page.svelte
│   │   │   │       └── nueva/
│   │   │   │           └── +page.svelte
│   │   │   │
│   │   │   ├── api/                 # API Routes (SvelteKit)
│   │   │   │   ├── pacientes/
│   │   │   │   │   ├── +server.js           # GET, POST
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── +server.js       # GET, PUT, DELETE
│   │   │   │   ├── especialistas/
│   │   │   │   │   ├── +server.js
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── +server.js
│   │   │   │   ├── sesiones/
│   │   │   │   │   └── +server.js
│   │   │   │   ├── notas/
│   │   │   │   │   └── +server.js
│   │   │   │   └── predict/         # Proxy a Python API
│   │   │   │       └── +server.js
│   │   │   │
│   │   │   ├── auth/                # Autenticación
│   │   │   │   ├── login/
│   │   │   │   │   └── +page.svelte
│   │   │   │   └── register/
│   │   │   │       └── +page.svelte
│   │   │   │
│   │   │   ├── +layout.svelte       # Layout principal
│   │   │   ├── +layout.js
│   │   │   └── +page.svelte         # Página de inicio
│   │   │
│   │   └── app.html                 # Template HTML base
│   │
│   ├── static/                       # Archivos estáticos
│   │   ├── images/
│   │   ├── icons/
│   │   └── favicon.png
│   │
│   ├── tests/                        # Tests del frontend
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env.example
│   └── Dockerfile
│
├── backend/                          # Microservicio Python (Solo ML/Predicciones)
│   ├── app/
│   │   ├── api/                     # Endpoints FastAPI
│   │   │   ├── __init__.py
│   │   │   ├── predict.py          # Endpoint de predicción
│   │   │   └── health.py           # Health check
│   │   │
│   │   ├── models/                  # Modelos de ML
│   │   │   ├── __init__.py
│   │   │   ├── bert_model.py       # Implementación BERT
│   │   │   ├── xgboost_model.py    # Implementación XGBoost
│   │   │   ├── random_forest_model.py  # Implementación Random Forest
│   │   │   └── ensemble.py         # Modelo ensemble
│   │   │
│   │   ├── services/                # Lógica de negocio ML
│   │   │   ├── __init__.py
│   │   │   ├── predictor.py        # Servicio de predicción
│   │   │   └── preprocessor.py     # Preprocesamiento de texto
│   │   │
│   │   ├── utils/                   # Utilidades
│   │   │   ├── __init__.py
│   │   │   ├── text_processing.py  # Procesamiento de texto
│   │   │   └── model_loader.py     # Carga de modelos
│   │   │
│   │   ├── config/                  # Configuraciones
│   │   │   ├── __init__.py
│   │   │   └── settings.py         # Variables de entorno
│   │   │
│   │   └── main.py                  # Punto de entrada FastAPI
│   │
│   ├── data/                        # Datos y modelos
│   │   ├── trained_models/         # Modelos entrenados (.pkl, .h5, etc.)
│   │   └── datasets/               # Datasets de entrenamiento
│   │
│   ├── tests/                       # Tests del backend
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_api.py
│   │
│   ├── scripts/                     # Scripts auxiliares
│   │   ├── train_models.py         # Entrenamiento de modelos
│   │   └── download_models.py      # Descarga de modelos pre-entrenados
│   │
│   ├── requirements.txt             # Dependencias Python
│   ├── .env.example
│   └── Dockerfile
│
├── docs/                            # Documentación
│   ├── architecture/
│   │   ├── system-design.md
│   │   └── data-flow.md
│   ├── api/                        # Documentación de APIs
│   │   ├── crud/                   # APIs CRUD (SvelteKit)
│   │   │   ├── pacientes.md       # API de gestión de pacientes
│   │   │   ├── especialistas.md   # API de gestión de especialistas
│   │   │   └── historias.md       # API de historias clínicas
│   │   └── ml/                     # APIs ML (Python FastAPI)
│   │       └── predicciones.md    # API de predicciones con BERT/XGBoost/RF
│   ├── database/
│   │   └── schema.md               # Esquema de BD
│   └── guides/
│       ├── setup.md
│       ├── deployment.md
│       └── ml-models.md
│
├── assets/                          # Recursos del proyecto
│   ├── images/                     # Diagramas e imágenes
│   └── mockups/                    # Diseños UI
│
├── .gitignore
├── docker-compose.yml              # Orquestación de contenedores
├── README.md
└── LICENSE
```

## Requisitos Previos

- **Node.js**: v18.0 o superior
- **npm** o **pnpm**: Gestor de paquetes
- **Python**: 3.9 o superior
- **pip**: Gestor de paquetes de Python
- **Docker** (opcional): Para containerización
- **Git**: Control de versiones

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/upc_mental-health-predictor.git
cd upc_mental-health-predictor
```

### 2. Configurar PostgreSQL (Base de Datos)

Tu base de datos PostgreSQL debe estar corriendo con:
- **Nombre de BD**: `salud_mental_app`
- **Puerto**: `5432` (default)
- **Host**: `localhost`

Si aún no la has creado:
```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE salud_mental_app;

# Salir
\q
```

### 3. Configurar el Backend Python (Microservicio ML)

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita backend/.env si necesitas cambiar algo
```

**Variables importantes del backend (.env)**:
```env
PORT=8000
DEVICE=cpu  # o "cuda" si tienes GPU NVIDIA, "mps" para Mac M1/M2
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=DEBUG
```

### 4. Configurar el Frontend SvelteKit

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
```

**Edita `frontend/.env` con tus credenciales de PostgreSQL**:
```env
# IMPORTANTE: Ajusta usuario y contraseña según tu instalación de PostgreSQL
PUBLIC_ML_API_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/salud_mental_app
AUTH_SECRET=dev-secret-change-in-production-min-32-characters
```

### 5. Inicializar Base de Datos

```bash
# Ejecutar script SQL para crear las tablas
psql -U postgres -d salud_mental_app -f docs/database/schema.sql

# O si usas un ORM como Prisma
cd frontend
npx prisma migrate dev
```

### 6. Descargar Modelos Pre-entrenados (Opcional)

```bash
cd backend
python scripts/download_models.py
```

**Nota**: Los modelos BERT pueden ser grandes (>400MB). Si no tienes modelos entrenados, el sistema los descargará automáticamente en el primer uso.

## Uso

### Desarrollo Local (Recomendado)

#### Opción 1: Script Automático (Más Rápido)

```bash
# En Mac/Linux
./dev-start.sh

# En Windows
dev-start.bat
```

Este script:
- Verifica que tengas Node.js, Python y PostgreSQL instalados
- Crea los archivos `.env` si no existen
- Instala las dependencias automáticamente
- Inicia ambos servicios (Backend ML + Frontend)

#### Opción 2: Manual (Más Control)

**Terminal 1 - Backend ML API (Puerto 8000)**
```bash
cd backend

# Crear y activar entorno virtual (solo primera vez)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# Copiar variables de entorno (solo primera vez)
cp .env.example .env
# Edita .env con tus credenciales de PostgreSQL

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend SvelteKit (Puerto 5173)**
```bash
cd frontend

# Instalar dependencias (solo primera vez)
npm install

# Copiar variables de entorno (solo primera vez)
cp .env.example .env
# Edita .env con tu DATABASE_URL de PostgreSQL

# Iniciar servidor de desarrollo
npm run dev
# o para abrir el navegador automáticamente:
npm run dev -- --open
```

**URLs de Desarrollo:**
- 🌐 Aplicación Web: `http://localhost:5173`
- 🤖 API ML: `http://localhost:8000`
- 📚 Documentación API: `http://localhost:8000/docs`
- 🗃️ PostgreSQL: `localhost:5432` (ya corriendo en tu PC)

### Producción con Docker

```bash
# Construir y levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir después de cambios
docker-compose up -d --build
```

### Scripts Disponibles

#### Frontend
```bash
npm run dev          # Modo desarrollo
npm run build        # Build para producción
npm run preview      # Preview del build
npm run test         # Ejecutar tests
npm run lint         # Linter
npm run format       # Formatear código
```

#### Backend
```bash
python -m pytest                    # Ejecutar tests
python -m pytest --cov             # Tests con cobertura
python scripts/train_models.py     # Entrenar modelos
uvicorn app.main:app --reload      # Servidor desarrollo
```

## API Endpoints

### API SvelteKit (CRUD)

#### Pacientes
```http
GET    /api/pacientes              # Listar todos los pacientes activos
POST   /api/pacientes              # Crear nuevo paciente
GET    /api/pacientes/[id]         # Obtener paciente por ID
PUT    /api/pacientes/[id]         # Actualizar paciente
DELETE /api/pacientes/[id]         # Desactivar paciente (soft delete)
GET    /api/pacientes/buscar-dni/[dni]  # Buscar paciente por DNI
```

**Ejemplo Request POST /api/pacientes**:
```json
{
  "dni": "12345678",
  "nombres": "María Rosa",
  "apellidos": "Sánchez López",
  "fecha_nacimiento": "1990-05-15",
  "sexo": "F",
  "direccion": "Av. Principal 123, San Isidro",
  "telefono": "987654321",
  "correo": "maria.sanchez@email.com",
  "contacto_emergencia": "Carlos Sánchez (hermano)",
  "telefono_emergencia": "923456789"
}
```

**Ejemplo Response GET /api/pacientes/[id]**:
```json
{
  "success": true,
  "data": {
    "id_paciente": 1,
    "dni": "12345678",
    "nombres": "María Rosa",
    "apellidos": "Sánchez López",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "F",
    "direccion": "Av. Principal 123, San Isidro",
    "telefono": "987654321",
    "correo": "maria.sanchez@email.com",
    "contacto_emergencia": "Carlos Sánchez (hermano)",
    "telefono_emergencia": "923456789",
    "fecha_registro": "2024-01-15T10:30:00Z",
    "flg_activo": true
  }
}
```

#### Especialistas
```http
GET    /api/especialistas          # Listar todos los especialistas activos
POST   /api/especialistas          # Crear nuevo especialista
GET    /api/especialistas/[id]     # Obtener especialista por ID
PUT    /api/especialistas/[id]     # Actualizar especialista
DELETE /api/especialistas/[id]     # Desactivar especialista (soft delete)
```

**Ejemplo Request POST /api/especialistas**:
```json
{
  "dni": "87654321",
  "nombres": "María Elena",
  "apellidos": "González Pérez",
  "especialidad": "Psicóloga Clínica",
  "colegiatura": "CPsP12345",
  "correo": "mgonzalez@centro.com",
  "telefono": "987654321",
  "cargo": "Psicóloga Senior",
  "usuario": "mgonzalez",
  "password": "Password123!",
  "rol": "especialista"
}
```

**Ejemplo Response GET /api/especialistas**:
```json
{
  "success": true,
  "data": [
    {
      "id_especialista": 1,
      "dni": "87654321",
      "nombres": "María Elena",
      "apellidos": "González Pérez",
      "especialidad": "Psicóloga Clínica",
      "colegiatura": "CPsP12345",
      "correo": "mgonzalez@centro.com",
      "telefono": "987654321",
      "cargo": "Psicóloga Senior",
      "usuario": "mgonzalez",
      "rol": "especialista",
      "flg_activo": true
    }
  ],
  "count": 1
}
```

#### Historias Clínicas
```http
GET    /api/historias              # Listar todas las historias clínicas
POST   /api/historias              # Crear nueva historia clínica
GET    /api/historias/[id]         # Obtener historia clínica por ID
PUT    /api/historias/[id]         # Actualizar historia clínica
POST   /api/historias/[id]/cerrar  # Cerrar historia clínica
GET    /api/pacientes/buscar-dni/[dni]  # Buscar paciente por DNI (incluye si tiene historia activa)
```

**Ejemplo Request POST /api/historias**:
```json
{
  "id_paciente": 4,
  "servicio_origen": "Consulta Externa",
  "antecedentes_personales": "Sin antecedentes médicos relevantes. No hospitalizaciones previas.",
  "antecedentes_familiares": "{\"depresion\":true,\"ansiedad\":true,\"bipolaridad\":false,\"esquizofrenia\":false,\"tdah\":false,\"toc\":false,\"adicciones\":true,\"suicidio\":false,\"otros\":\"Madre con trastorno de ansiedad generalizada\"}",
  "antecedentes_psicosociales": "Nivel socioeconómico bajo. Educación secundaria completa.",
  "habitos_personales": "{\"alcohol\":\"Ocasional\",\"alcohol_frecuencia\":\"1-2 veces/semana\",\"tabaco\":\"No\",\"tabaco_frecuencia\":\"\",\"drogas\":\"No\",\"drogas_frecuencia\":\"\",\"sueño_horas\":\"6-7h\",\"sueño_calidad\":\"Regular\",\"alimentacion\":\"Adecuada\",\"ejercicio\":\"No realiza\",\"otros\":\"\"}",
  "situacion_familiar": "Vive sola con dos hijos menores. Separada hace 1 año.",
  "situacion_laboral": "Desempleada actualmente. Situación económica precaria.",
  "evaluacion_inicial": "Paciente presenta estado de ánimo deprimido persistente por más de 6 meses.",
  "diagnostico_inicial": "Impresión diagnóstica: Episodio Depresivo Mayor Moderado (F32.1)",
  "tratamientos_previos": "Tratamiento previo con sertralina 50mg por 3 meses."
}
```

**Nota**: Los campos `antecedentes_familiares` y `habitos_personales` se almacenan en formato JSON string. El frontend proporciona controles visuales (checkboxes, radios, selects) que automáticamente convierten a/desde JSON.

**Ejemplo Response GET /api/historias/[id]**:
```json
{
  "success": true,
  "data": {
    "id_historia": 1,
    "id_paciente": 4,
    "paciente_nombre": "María Rosa Sánchez López",
    "especialista_nombre": "Dra. María Elena González Pérez",
    "fecha_apertura": "2024-01-15T14:30:00Z",
    "especialista_apertura": 1,
    "servicio_origen": "Consulta Externa",
    "antecedentes_personales": "Sin antecedentes médicos relevantes.",
    "antecedentes_familiares": "{\"depresion\":true,\"ansiedad\":true,...}",
    "habitos_personales": "{\"alcohol\":\"Ocasional\",...}",
    "diagnostico_inicial": "Episodio Depresivo Mayor Moderado (F32.1)",
    "situacion_historia": "abierta",
    "fecha_actualizacion": "2024-01-20T10:15:00Z",
    "especialista_actualizacion": 1
  }
}
```

**Ejemplo Request POST /api/historias/[id]/cerrar**:
```json
{
  "motivo_cierre": "Alta médica por mejoría significativa tras 6 meses de tratamiento"
}
```

### API Python (Predicción ML)

#### Predicción de Trastornos
```http
POST /api/v1/predict
Content-Type: application/json

{
  "text": "Texto de la nota clínica del paciente...",
  "model": "bert" | "xgboost" | "random_forest" | "ensemble"
}
```

**Respuesta exitosa**:
```json
{
  "success": true,
  "prediction": {
    "disorder": "depresión",
    "confidence": 0.87,
    "probabilities": {
      "depresión": 0.87,
      "ansiedad": 0.10,
      "normal": 0.03
    },
    "model_used": "bert"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time_ms": 245
}
```

#### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "models_loaded": ["bert", "xgboost", "random_forest"],
  "version": "1.0.0"
}
```

Para documentación completa de la API, visita:

**APIs CRUD (SvelteKit):**
- Pacientes: [docs/api/crud/pacientes.md](docs/api/crud/pacientes.md)
- Especialistas: [docs/api/crud/especialistas.md](docs/api/crud/especialistas.md)
- Historias Clínicas: [docs/api/crud/historias.md](docs/api/crud/historias.md)

**API ML (Python FastAPI):**
- Predicciones: [docs/api/ml/predicciones.md](docs/api/ml/predicciones.md)
- Swagger UI: `http://localhost:8000/docs` (cuando esté implementado)

## Desarrollo

### Estructura de Ramas Git

- `main`: Rama principal de producción
- `develop`: Rama de desarrollo
- `feature/*`: Nuevas funcionalidades
- `bugfix/*`: Corrección de errores
- `hotfix/*`: Correcciones urgentes en producción

### Workflow de Desarrollo

```bash
# Crear nueva feature
git checkout -b feature/nombre-feature develop

# Hacer commits
git add .
git commit -m "feat: descripción del cambio"

# Actualizar con develop
git pull origin develop

# Push de la rama
git push origin feature/nombre-feature

# Crear Pull Request a develop
```

### Convenciones de Código

#### JavaScript/Svelte (Frontend)
- Usar ESLint y Prettier
- Nombres de componentes en PascalCase: `PatientForm.svelte`
- Nombres de archivos de rutas: `+page.svelte`, `+server.js`
- Usar `const` y `let`, evitar `var`
- Comentarios JSDoc para funciones complejas

```javascript
/**
 * Obtiene todos los pacientes con filtros opcionales
 * @param {Object} filters - Filtros de búsqueda
 * @returns {Promise<Array>} Lista de pacientes
 */
export async function getPatients(filters = {}) {
  // implementación
}
```

#### Python (Backend ML)
- Seguir [PEP 8](https://pep8.org/)
- Usar type hints
- Docstrings en formato Google
- Black para formateo (88 caracteres)
- isort para ordenar imports

```python
def predict_disorder(text: str, model_name: str = "bert") -> dict:
    """
    Predice el trastorno mental basado en texto clínico.

    Args:
        text: Texto de la nota clínica
        model_name: Nombre del modelo a utilizar

    Returns:
        Diccionario con predicción y confianza

    Raises:
        ValueError: Si el modelo no existe
    """
    pass
```

### Comandos Útiles de Desarrollo

```bash
# Frontend - Formatear
npm run format

# Frontend - Linter
npm run lint

# Frontend - Type check (si usas TypeScript)
npm run check

# Backend - Formatear
black backend/

# Backend - Linter
flake8 backend/

# Backend - Type check
mypy backend/
```

## Testing

### Tests Frontend (SvelteKit)

```bash
cd frontend

# Ejecutar todos los tests
npm run test

# Tests en modo watch
npm run test:watch

# Tests con cobertura
npm run test:coverage

# Tests de componentes específicos
npm run test -- PatientForm
```

### Tests Backend (Python)

```bash
cd backend

# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_models.py

# Tests con output verbose
pytest -v

# Tests de un módulo específico
pytest tests/test_api.py::test_predict_endpoint
```

### Tests de Integración

```bash
# Desde la raíz del proyecto
npm run test:integration
```

## Base de Datos

Base de datos: **salud_mental_app** (PostgreSQL)

### Tablas Actuales

**paciente**
- id_paciente, dni, nombres, apellidos, fecha_nacimiento, sexo, direccion, telefono, correo, contacto_emergencia, telefono_emergencia, fecha_registro, flg_activo

**especialista**
- id_especialista, dni, nombres, apellidos, especialidad, colegiatura, correo, telefono, cargo, usuario, password_hash, rol, ultimo_acceso, intentos_fallidos, bloqueado_hasta, flg_activo

**historia_clinica**
- id_historia, id_paciente (FK), fecha_apertura, especialista_apertura (FK), servicio_origen, antecedentes_personales, antecedentes_familiares, antecedentes_psicosociales, habitos_personales, situacion_familiar, situacion_laboral, evaluacion_inicial, diagnostico_inicial, tratamientos_previos, situacion_historia, fecha_actualizacion, especialista_actualizacion (FK), fecha_cierre, motivo_cierre

### Inicializar Base de Datos

```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE salud_mental_app;"

# Ejecutar script SQL
psql -U postgres -d salud_mental_app -f docs/database/schema.sql
```

Ver esquema completo con tipos de datos y relaciones en [docs/database/schema.md](docs/database/schema.md)

## Despliegue

### Con Docker Compose (Recomendado)

```bash
# Producción
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f

# Escalar servicios
docker-compose up -d --scale ml-api=3
```

### Despliegue Manual

#### Frontend (Vercel, Netlify, etc.)
```bash
cd frontend
npm run build
# Desplegar la carpeta build/
```

#### Backend ML (Railway, Render, AWS, etc.)
```bash
cd backend
# Configurar variables de entorno en el servicio
# Usar Dockerfile para el deploy
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Checklist de Pull Request

- [ ] El código sigue las convenciones del proyecto
- [ ] Se agregaron tests para nuevas funcionalidades
- [ ] Todos los tests pasan (`npm test` y `pytest`)
- [ ] Se actualizó la documentación si es necesario
- [ ] No hay conflictos con la rama develop
- [ ] El código está formateado correctamente

## Seguridad y Privacidad

Este sistema maneja información sensible de salud. Se deben seguir:

- **HIPAA** (si aplica en EE.UU.)
- **Ley de Protección de Datos Personales** del Perú
- Encriptación de datos sensibles
- Autenticación y autorización robusta
- Auditoría de accesos
- Backups regulares encriptados

Ver [docs/guides/security.md](docs/guides/security.md) para más información.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autores

**Universidad Peruana de Ciencias Aplicadas (UPC)**
- Proyecto de investigación en sistemas de salud mental
- Facultad de Ingeniería de Sistemas

### Equipo de Desarrollo
- [Nombre del líder del proyecto]
- [Nombres de colaboradores]

## Contacto

Para preguntas, sugerencias o colaboraciones:
- **Email**: contacto@example.com
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/upc_mental-health-predictor/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/upc_mental-health-predictor/wiki)

## Agradecimientos

- Centro de atención psicológica colaborador
- Profesionales de salud mental que brindaron su expertise
- Comunidad open source de SvelteKit, FastAPI y Transformers
- UPC por el apoyo institucional

## Roadmap

- [x] Diseño de arquitectura del sistema
- [ ] Implementación de CRUD de pacientes y especialistas
- [ ] Integración de modelo BERT
- [ ] Implementación de XGBoost y Random Forest
- [ ] Sistema de autenticación y autorización
- [ ] Dashboard con métricas y visualizaciones
- [ ] Exportación de reportes en PDF
- [ ] Notificaciones por email
- [ ] App móvil (futuro)

---

**Nota Importante**: Este sistema es una herramienta de **apoyo al diagnóstico** y **NO reemplaza** el criterio clínico de profesionales de la salud mental. Debe ser utilizado exclusivamente como complemento a la evaluación profesional por personal calificado.

**Advertencia**: Los datos de pacientes son confidenciales. Asegúrate de cumplir con todas las regulaciones de privacidad y seguridad aplicables en tu jurisdicción.
