# Sistema de Predicción de Trastornos Mentales

Sistema web de análisis predictivo de depresión y ansiedad mediante NLP con BERT + XGBoost, diseñado para centros de atención psicológica.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características Principales](#características-principales)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Instalación Rápida](#instalación-rápida)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Desarrollo](#desarrollo)
- [Base de Datos](#base-de-datos)
- [Seguridad y Privacidad](#seguridad-y-privacidad)
- [Licencia](#licencia)
- [Autores](#autores)
- [Contacto](#contacto)

## Descripción

Plataforma que permite a pacientes registrar notas diarias sobre su estado emocional y a especialistas monitorear evaluaciones automáticas de salud mental generadas por modelos de Machine Learning.

### Componentes Principales

- **Portal de Pacientes**: Cuestionario diario de 4 preguntas + transcripción de audio
- **Portal de Especialistas**: Gestión de pacientes, historias clínicas y visualización de evaluaciones ML
- **API de Predicción ML**: Microservicio Python con modelos BERT + XGBoost para detección de depresión/ansiedad

## Características Principales

### Sistema de Usuarios
- ✅ **Autenticación dual**: Login separado para pacientes (DNI) y especialistas (usuario/contraseña)
- ✅ **Roles**: Administrador, Especialista, Paciente
- ✅ **Seguridad**: Bcrypt para passwords, sesiones con cookies, bloqueo por intentos fallidos

### Portal de Pacientes
- ✅ **Cuestionario diario**: 4 preguntas de texto libre con validación (mínimo 10 palabras)
- ✅ **Transcripción de audio**: Whisper AI para convertir notas de voz a texto
- ✅ **Límite diario**: Máximo 2 respuestas por día (zona horaria GMT-5 Lima)
- ✅ **Historial personal**: Ver respuestas sin acceso a evaluaciones ML (confidencial)
- ✅ **Cambio de contraseña**: Autogestión de credenciales

### Portal de Especialistas
- ✅ **Gestión de pacientes**: CRUD completo con validaciones en tiempo real
- ✅ **Historias clínicas**: Apertura, edición, cierre con antecedentes familiares (JSONB) y medicaciones
- ✅ **Evaluaciones ML**: Visualización detallada de predicciones con probabilidades, nivel de riesgo y palabras clave
- ✅ **Reprocesamiento**: Botón para reenviar respuestas al modelo ML (síncrono con auditoría)
- ✅ **Dashboard**: Métricas y gráficos de seguimiento

### Análisis ML
- ✅ **Modelo híbrido**: BERT (español) para embeddings + XGBoost para clasificación multi-etiqueta
- ✅ **Detección**: Depresión y Ansiedad con probabilidades individuales
- ✅ **Nivel de riesgo**: Bajo / Moderado / Alto basado en umbral de probabilidad
- ✅ **Palabras clave**: Extracción de términos relevantes por trastorno
- ✅ **Procesamiento asíncrono**: Las respuestas se procesan en segundo plano sin bloquear al paciente

## Tecnologías

### Frontend + Backend CRUD
- **SvelteKit 2.0**: Framework full-stack con server-side rendering
- **PostgreSQL 17**: Base de datos relacional
- **TailwindCSS**: Framework de estilos
- **Zod**: Validación de esquemas

### Backend ML (Microservicio)
- **FastAPI**: Framework web async
- **BERT**: `dccuchile/bert-base-spanish-wwm-uncased` (transformers)
- **XGBoost**: Clasificación multi-label
- **Faster-Whisper**: Transcripción de audio (modelo small)
- **PyTorch**: Framework de deep learning

### Base de Datos
- **PostgreSQL 17.6**: Ver esquema completo en [`docs/database/schema.md`](docs/database/schema.md)
- **Tablas principales**: `paciente`, `especialista`, `historia_clinica`, `paciente_respuesta`, `evaluacion_ml`

## Arquitectura

```
┌──────────────────────┐
│   Navegador Web      │
│  (Cliente Svelte)    │
└──────────┬───────────┘
           │
┌──────────▼────────────────────────────────────────┐
│         SvelteKit Server (Puerto 5173)            │
│  ┌─────────────────────────────────────────────┐  │
│  │ Frontend SSR + API Routes (CRUD)            │  │
│  │ • /login/paciente, /login/especialista      │  │
│  │ • /paciente/notas (cuestionario diario)     │  │
│  │ • /pacientes, /especialistas, /historias    │  │
│  │ • API: /api/pacientes, /api/respuestas, etc│  │
│  └─────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────┬────────┘
            │                              │
            │ Consultas SQL                │ HTTP POST
            │                              │ (evaluación)
┌───────────▼────────────┐    ┌───────────▼─────────────┐
│  PostgreSQL Database   │    │  Python ML API (8000)   │
│  (Puerto 5432)         │    │  ┌───────────────────┐  │
│                        │    │  │ BERT Embeddings   │  │
│ • paciente             │    │  │ XGBoost Predict   │  │
│ • especialista         │    │  │ Whisper Transcrib │  │
│ • historia_clinica     │    │  └───────────────────┘  │
│ • paciente_respuesta   │◄───┤  Guarda evaluación_ml   │
│ • evaluacion_ml        │    └─────────────────────────┘
└────────────────────────┘
```

## Instalación Rápida

### Requisitos
- **Node.js 18+** y **npm/pnpm**
- **Python 3.9+** y **pip**
- **PostgreSQL 17+** (corriendo en puerto 5432)

### 1. Base de Datos

```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE salud_mental_app;"

# Ejecutar schema
psql -U postgres -d salud_mental_app -f docs/database/schema.sql
```

### 2. Backend ML (Python)

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

✅ API ML disponible en: `http://localhost:8000`
📚 Docs: `http://localhost:8000/docs`

### 3. Frontend + CRUD (SvelteKit)

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar frontend/.env con tu DATABASE_URL de PostgreSQL
```

**Edita `frontend/.env`:**
```env
PUBLIC_ML_API_URL=http://localhost:8000
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/salud_mental_app
AUTH_SECRET=dev-secret-change-in-production-min-32-characters
```

```bash
# Iniciar servidor de desarrollo
npm run dev
```

✅ Aplicación disponible en: `http://localhost:5173`

## Uso

### Credenciales de Prueba

**Especialista Admin:**
- Usuario: `mgonzalez`
- Contraseña: (ver docs/database/schema.md para datos de prueba)

**Paciente:**
- DNI: `12345678`
- Contraseña: (definir al registrar paciente)

### Flujo de Trabajo

1. **Especialista** crea un nuevo paciente con DNI y datos personales
2. **Especialista** crea historia clínica con antecedentes y medicaciones
3. **Paciente** ingresa con DNI/password y completa cuestionario diario
4. **Sistema ML** procesa respuestas en segundo plano (async)
5. **Especialista** revisa evaluaciones ML con probabilidades y nivel de riesgo
6. **Especialista** puede reprocesar respuestas si actualiza el modelo

### Características por Usuario

**Paciente:**
- ✅ Completar cuestionario 2 veces al día
- ✅ Grabar notas de audio (transcritas automáticamente)
- ✅ Ver historial de respuestas (sin evaluaciones)
- ✅ Cambiar contraseña

**Especialista:**
- ✅ Gestionar pacientes y sus historias clínicas
- ✅ Ver evaluaciones ML con detalles completos
- ✅ Reprocesar respuestas con nuevos modelos
- ✅ Visualizar métricas y gráficos

## Estructura del Proyecto

```
upc_mental-health-predictor/
├── frontend/              # SvelteKit (Frontend + Backend CRUD)
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/      # Componentes Svelte
│   │   │   └── server/          # Servicios, validadores, DB client
│   │   └── routes/
│   │       ├── (app)/           # Rutas protegidas (especialistas)
│   │       ├── paciente/        # Portal de pacientes
│   │       ├── login/           # Autenticación
│   │       └── api/             # API endpoints
│   └── README.md          # 📖 Documentación detallada del frontend
│
├── backend/               # Python FastAPI (Solo ML/Predicción)
│   ├── app/
│   │   ├── api/           # Endpoints de predicción
│   │   ├── ml/            # Modelos BERT + XGBoost
│   │   └── main.py
│   ├── scripts/
│   │   ├── train.py       # Entrenar modelos
│   │   └── test.py        # Validar modelos
│   └── README.md          # 📖 Documentación detallada del backend
│
├── docs/
│   ├── database/
│   │   └── schema.md      # 📖 Esquema completo de PostgreSQL
│   └── guides/            # Guías adicionales
│
├── docker-compose.yml     # Orquestación (desarrollo)
└── README.md             # 📄 Este archivo
```

**Ver documentación detallada:**
- Frontend + CRUD: [`frontend/README.md`](frontend/README.md)
- Backend ML: [`backend/README.md`](backend/README.md)
- Base de Datos: [`docs/database/schema.md`](docs/database/schema.md)

## Desarrollo

### Scripts Disponibles

**Frontend:**
```bash
npm run dev          # Desarrollo (hot reload)
npm run build        # Build producción
npm run preview      # Preview del build
npm run test         # Tests
npm run lint         # Linter
npm run format       # Formatear código
```

**Backend ML:**
```bash
uvicorn app.main:app --reload      # Desarrollo
python scripts/train.py            # Entrenar modelo
python scripts/test.py --random 5  # Validar modelo
pytest                             # Tests
ruff format .                      # Formatear
ruff check .                       # Linter
```

### Docker (Desarrollo)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Workflow de Git

```bash
# Crear feature branch
git checkout -b feature/nombre-feature develop

# Commits
git commit -m "feat: descripción del cambio"

# Push y PR a develop
git push origin feature/nombre-feature
```

## Base de Datos

- **Motor**: PostgreSQL 17.6
- **Timezone**: Timestamps en UTC, frontend maneja GMT-5 Lima
- **Esquema completo**: Ver [`docs/database/schema.md`](docs/database/schema.md)

**Tablas principales:**
- `paciente` (11 campos + auth)
- `especialista` (13 campos + auth + roles)
- `historia_clinica` (17 campos + JSONB)
- `paciente_respuesta` (respuestas diarias)
- `evaluacion_ml` (resultados de modelos)
- `paciente_medicacion` (medicamentos preexistentes)

## Seguridad y Privacidad

- ✅ **Encriptación**: Bcrypt (salt rounds = 10) para passwords
- ✅ **Sesiones**: Cookies con expiración de 30 minutos
- ✅ **Validación**: Zod en backend, validación en tiempo real en frontend
- ✅ **Autorización**: Roles (admin, especialista, paciente)
- ✅ **Auditoría**: Registro de reprocesamiento de evaluaciones
- ✅ **Confidencialidad**: Pacientes NO ven resultados de evaluaciones ML
- ✅ **Soft delete**: Desactivación con `flg_activo` en lugar de eliminación física

**⚠️ Cumplimiento**: Ley de Protección de Datos Personales del Perú

## Licencia

MIT License - Ver [LICENSE](LICENSE)

## Autores

**Universidad Peruana de Ciencias Aplicadas (UPC)**
Proyecto de investigación en sistemas de salud mental

## Contacto

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/upc_mental-health-predictor/issues)
- **Email**: contacto@example.com

---

**⚠️ Nota Importante**: Este sistema es una herramienta de **apoyo al diagnóstico** y **NO reemplaza** el criterio clínico de profesionales de la salud mental.
