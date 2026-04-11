# Frontend - Mental Health Predictor

Aplicación web full-stack con SvelteKit que implementa tanto el frontend (SSR + CSR) como el backend (API REST) para la gestión integral de pacientes, especialistas, historias clínicas y evaluaciones de salud mental con ML.

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Desarrollo](#desarrollo)
- [Build](#build)
- [Testing](#testing)
- [Linting y Formato](#linting-y-formato)
- [Variables de Entorno](#variables-de-entorno)
- [Rutas Principales](#rutas-principales)
- [API Routes](#api-routes)
- [Autenticación y Sesiones](#autenticación-y-sesiones)
- [Integración con ML](#integración-con-ml)
- [Tecnologías](#tecnologías)

## Características Principales

### Sistema Dual de Portales

**Portal de Especialistas/Admin** (rutas `/` y `/(app)/*`):
- ✅ Gestión completa de pacientes (CRUD)
- ✅ Gestión de especialistas (CRUD, cambio de contraseña)
- ✅ Historias clínicas con campos JSONB (antecedentes, hábitos)
- ✅ Visualización de evaluaciones ML con trastornos detectados
- ✅ **Reprocesar respuestas** con auditoría (quién/cuándo)
- ✅ Dashboard con métricas y estadísticas
- ✅ Búsqueda y filtrado de pacientes

**Portal de Pacientes** (rutas `/paciente/*`):
- ✅ Cuestionario diario de 4 preguntas
- ✅ **Grabación de audio** con transcripción automática (Faster-Whisper)
- ✅ **Límite de 2 respuestas por día** (timezone GMT-5 Lima)
- ✅ Historial personal de respuestas
- ✅ **Confidencialidad**: Pacientes NO ven evaluaciones ML
- ✅ Cambio de contraseña en primer login
- ✅ Perfil personal editable

### Características Técnicas
- ✅ **Autenticación dual**: Sesiones separadas para pacientes y especialistas (cookies, 30 min)
- ✅ **Roles**: Admin, Especialista, Paciente con control de acceso (RBAC)
- ✅ **Validación**: Zod para schemas, mínimo 10 palabras por respuesta
- ✅ **Seguridad**: Bcrypt (10 salt rounds), sanitización de inputs
- ✅ **Timezone handling**: GMT-5 Lima con conversiones correctas
- ✅ **Soft delete**: Flag `flg_activo` en lugar de DELETE físico
- ✅ **Procesamiento asíncrono**: Fire-and-forget para evaluaciones ML
- ✅ **Procesamiento síncrono**: Reprocesar espera resultado para feedback inmediato

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/             # Componentes Svelte reutilizables
│   │   │   ├── forms/              # Formularios (PacienteForm, EspecialistaForm)
│   │   │   └── ui/                 # UI components
│   │   ├── server/                 # Código del servidor (SvelteKit)
│   │   │   ├── db/                 # Configuración PostgreSQL (postgres.js)
│   │   │   ├── services/           # Lógica de negocio
│   │   │   │   ├── auth.js         # Autenticación especialistas
│   │   │   │   ├── auth-paciente.js # Autenticación pacientes
│   │   │   │   ├── pacientes.js    # CRUD pacientes
│   │   │   │   ├── especialistas.js # CRUD especialistas
│   │   │   │   ├── historias.js    # Historias clínicas
│   │   │   │   ├── respuestas.js   # Respuestas de pacientes
│   │   │   │   └── ml-prediccion.js # Integración con ML API
│   │   │   └── validators/         # Schemas Zod
│   │   └── utils/                  # Utilidades
│   └── routes/                     # Páginas y API routes
│       ├── (app)/                  # Portal Especialistas/Admin
│       │   ├── dashboard/          # Dashboard con métricas
│       │   ├── inicio/             # Página de inicio
│       │   ├── pacientes/          # Gestión de pacientes
│       │   │   ├── +page.svelte    # Lista de pacientes
│       │   │   ├── nuevo/          # Crear paciente
│       │   │   └── [id]/           # Detalle, editar, notas
│       │   │       ├── ver/        # Vista detallada
│       │   │       └── notas/      # Historial respuestas
│       │   │           └── [idRespuesta]/ # Detalle respuesta con reprocesar
│       │   ├── especialistas/      # Gestión de especialistas
│       │   └── historias/          # Gestión de historias clínicas
│       ├── paciente/               # Portal Pacientes
│       │   ├── inicio/             # Inicio paciente
│       │   ├── notas/              # Cuestionario diario
│       │   │   └── historial/      # Historial personal (sin evaluaciones ML)
│       │   └── perfil/             # Perfil y cambio contraseña
│       ├── login/
│       │   └── especialista/       # Login especialistas/admin
│       └── api/                    # API REST endpoints
│           ├── auth/               # Login/logout (dual)
│           ├── pacientes/          # CRUD pacientes + respuestas + transcribir
│           ├── especialistas/      # CRUD especialistas
│           ├── historias/          # CRUD historias clínicas
│           └── respuestas/         # Reprocesar respuestas
│               └── [idRespuesta]/reprocesar/
├── static/                         # Archivos estáticos
└── package.json
```

## Instalación

```bash
npm install
```

## Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Abrir navegador automáticamente
npm run dev -- --open
```

## Build

```bash
# Crear build de producción
npm run build

# Preview del build
npm run preview
```

## Testing

```bash
# Ejecutar tests
npm run test

# Tests en modo watch
npm run test:watch

# Coverage
npm run test:coverage
```

## Linting y Formato

```bash
# Linter
npm run lint

# Formatear código
npm run format

# Type checking
npm run check
```

## Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/salud_mental_app

# API de Machine Learning
PUBLIC_ML_API_URL=http://localhost:8000

# Autenticación
AUTH_SECRET=your-secret-key-here

# Entorno
NODE_ENV=development
```

**Variables importantes:**
- `DATABASE_URL`: Conexión a PostgreSQL 17.6+ (timezone GMT-5 Lima)
- `PUBLIC_ML_API_URL`: URL del backend Python para predicciones y transcripción
- `AUTH_SECRET`: Secret para firmar cookies de sesión (cambiar en producción)

## Rutas Principales

### Portal Especialistas/Admin
- `/` - Redirección a login o inicio
- `/(app)/inicio` - Página de inicio del portal
- `/(app)/dashboard` - Dashboard con métricas
- `/(app)/pacientes` - Lista de pacientes
- `/(app)/pacientes/nuevo` - Crear nuevo paciente
- `/(app)/pacientes/[id]/ver` - Ver detalle de paciente
- `/(app)/pacientes/[id]/notas` - Historial de respuestas del paciente
- `/(app)/pacientes/[id]/notas/[idRespuesta]` - Detalle de respuesta con **botón reprocesar**
- `/(app)/especialistas` - Gestión de especialistas
- `/(app)/historias` - Gestión de historias clínicas
- `/login/especialista` - Login especialistas/admin

### Portal Pacientes
- `/paciente/inicio` - Inicio del paciente
- `/paciente/notas` - **Cuestionario diario** (4 preguntas + audio opcional)
- `/paciente/notas/historial` - Historial personal (sin evaluaciones ML)
- `/paciente/perfil` - Perfil y cambio de contraseña

## API Routes

Para documentación detallada de los endpoints, considerar crear un [API_README.md](API_README.md) similar al del backend.

### Autenticación (Dual)
- `POST /api/auth/login` - Login especialistas/admin
- `POST /api/auth/login-paciente` - Login pacientes
- `POST /api/auth/logout` - Logout especialistas/admin
- `POST /api/auth/logout-paciente` - Logout pacientes
- `GET /api/auth/session` - Verificar sesión activa

### Pacientes
- `GET /api/pacientes` - Listar todos (con filtros)
- `POST /api/pacientes` - Crear nuevo
- `GET /api/pacientes/[id]` - Obtener uno
- `PUT /api/pacientes/[id]` - Actualizar
- `DELETE /api/pacientes/[id]` - Soft delete
- `GET /api/pacientes/buscar-dni/[dni]` - Buscar por DNI
- `GET /api/pacientes/perfil` - Perfil del paciente autenticado
- `POST /api/pacientes/cambiar-password` - Cambiar contraseña
- `POST /api/pacientes/cambiar-password-primer-login` - Cambiar contraseña inicial
- `POST /api/pacientes/respuestas` - Crear respuesta (cuestionario + ML)
- `POST /api/pacientes/transcribir` - **Transcribir audio** a texto

### Especialistas
- `GET /api/especialistas` - Listar todos
- `POST /api/especialistas` - Crear nuevo
- `GET /api/especialistas/[id]` - Obtener uno
- `PUT /api/especialistas/[id]` - Actualizar
- `DELETE /api/especialistas/[id]` - Soft delete
- `POST /api/especialistas/cambiar-password-primer-login` - Cambiar contraseña inicial

### Historias Clínicas
- `GET /api/historias` - Listar todas
- `POST /api/historias` - Crear nueva
- `GET /api/historias/[id]` - Obtener una
- `PUT /api/historias/[id]` - Actualizar
- `POST /api/historias/[id]/cerrar` - Cerrar historia
- `GET /api/historias/paciente/[id]` - Historias de un paciente

### Respuestas y Evaluaciones
- `POST /api/respuestas/[idRespuesta]/reprocesar` - **Reprocesar respuesta con ML** (síncrono)
  - Solo admin/especialista
  - Guarda auditoría (quién/cuándo)
  - Retorna nueva evaluación

## Autenticación y Sesiones

### Sistema Dual de Autenticación
El sistema implementa **dos flujos de autenticación separados**:

1. **Especialistas/Admin**:
   - Cookie: `session`
   - Duración: 30 minutos
   - Roles: `admin`, `especialista`
   - Login: `/login/especialista`

2. **Pacientes**:
   - Cookie: `session_paciente`
   - Duración: 30 minutos
   - Rol: `paciente`
   - Login: `/` (redirección automática)

### Seguridad
- Contraseñas hasheadas con **Bcrypt** (10 salt rounds)
- Cookies HttpOnly para prevenir XSS
- Validación de sesiones en cada request protegido
- Primer login fuerza cambio de contraseña
- Validación de inputs con **Zod schemas**

## Integración con ML

### Flujo Asíncrono (Fire-and-Forget)
Cuando un paciente envía respuestas:
1. Frontend guarda respuesta en BD con estado `pendiente`
2. Frontend envía a ML API (POST `/api/v1/predict/mental-health`)
3. **No espera respuesta** - continúa inmediatamente
4. ML procesa en background y guarda evaluación
5. Especialista ve evaluación cuando esté lista

### Flujo Síncrono (Reprocesar)
Cuando un especialista reprocesa:
1. Frontend llama `/api/respuestas/[id]/reprocesar`
2. **Espera respuesta** del ML
3. Muestra spinner durante procesamiento
4. Actualiza evaluación en BD
5. Guarda auditoría: usuario, timestamp
6. Recarga página con nueva evaluación

### Endpoints ML Utilizados
- `POST /api/v1/predict/mental-health` - Predicción multi-etiqueta
- `POST /api/v1/audio/transcribe` - Transcripción de audio

## Tecnologías

### Frontend
- **SvelteKit 2.0+**: Framework full-stack con SSR + CSR
- **Svelte 4**: Framework reactivo
- **TailwindCSS**: Estilos utility-first
- **Zod**: Validación de schemas

### Backend (SvelteKit Server)
- **Node.js**: Runtime del servidor
- **postgres.js**: Cliente PostgreSQL ligero y rápido
- **Bcrypt**: Hashing de contraseñas
- **Cookie-based sessions**: Manejo de sesiones

### Base de Datos
- **PostgreSQL 17.6**: Base de datos relacional
- **JSONB**: Para campos complejos (antecedentes, respuestas, evaluaciones)
- **Timezone**: GMT-5 (America/Lima)

### Integración
- **Fetch API**: Para comunicación con ML API
- **FormData**: Para subida de archivos de audio
