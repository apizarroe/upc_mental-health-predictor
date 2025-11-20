# Frontend - Mental Health Predictor

Aplicación web SvelteKit que maneja tanto el frontend como el backend CRUD para la gestión de pacientes, especialistas e historias clínicas.

## Estructura

```
frontend/
├── src/
│   ├── lib/
│   │   ├── assets/                 # Recursos estáticos (imágenes, iconos)
│   │   ├── components/             # Componentes Svelte reutilizables
│   │   │   ├── forms/              # Componentes de formularios
│   │   │   └── ui/                 # Componentes de interfaz de usuario
│   │   ├── server/                 # Código del servidor
│   │   │   ├── db/                 # Configuración de base de datos (PostgreSQL)
│   │   │   ├── services/           # Lógica de negocio y acceso a datos
│   │   │   │   ├── pacientes.js
│   │   │   │   ├── especialistas.js
│   │   │   │   └── historias.js
│   │   │   └── validators/         # Validación de datos
│   │   ├── stores/                 # Estado global (Svelte stores)
│   │   └── utils/                  # Funciones auxiliares
│   └── routes/                     # Páginas y API routes (SvelteKit)
│       ├── (app)/                  # Rutas de la aplicación (layout con sidebar)
│       │   ├── +page.svelte        # Página de inicio
│       │   ├── +layout.svelte      # Layout principal con navegación
│       │   ├── dashboard/          # Dashboard con métricas
│       │   ├── pacientes/          # Gestión de pacientes
│       │   │   ├── +page.svelte    # Lista de pacientes
│       │   │   ├── nuevo/          # Crear nuevo paciente
│       │   │   └── [id]/           # Detalle y edición de paciente
│       │   ├── especialistas/      # Gestión de especialistas
│       │   │   ├── +page.svelte    # Lista de especialistas
│       │   │   ├── nuevo/          # Crear nuevo especialista
│       │   │   └── [id]/           # Detalle y edición de especialista
│       │   └── historias/          # Gestión de historias clínicas
│       │       ├── +page.svelte    # Lista de historias
│       │       ├── nuevo/          # Crear nueva historia
│       │       └── [id]/           # Detalle y edición de historia
│       ├── login/                  # Página de inicio de sesión
│       ├── api/                    # API endpoints (backend)
│       │   ├── auth/               # Autenticación
│       │   ├── pacientes/          # CRUD de pacientes
│       │   ├── especialistas/      # CRUD de especialistas
│       │   └── historias/          # CRUD de historias clínicas
│       ├── dashboard/              # Proxy para dashboard (redirige a /app/dashboard)
│       ├── pacientes/              # Proxy para pacientes (redirige a /app/pacientes)
│       ├── especialistas/          # Proxy para especialistas (redirige a /app/especialistas)
│       └── predicciones/           # Página de predicciones ML
├── static/                         # Archivos estáticos públicos
└── tests/                          # Tests unitarios y de integración
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

- `PUBLIC_ML_API_URL`: URL del microservicio Python ML (default: `http://localhost:8000`)
- `DATABASE_URL`: Conexión a PostgreSQL (ej: `postgresql://postgres:password@localhost:5432/salud_mental_app`)
- `AUTH_SECRET`: Secret para autenticación
- `NODE_ENV`: Entorno de ejecución (development/production)

## Rutas Principales

- `/` - Página de inicio
- `/dashboard` - Dashboard principal
- `/pacientes` - Gestión de pacientes
- `/especialistas` - Gestión de especialistas
- `/historias` - Gestión de historias clínicas
- `/predicciones` - Realizar predicciones de ML

## API Routes

Endpoints disponibles en `/api/*`:

### CRUD de Entidades
- `/api/pacientes` - CRUD completo de pacientes
  - `GET /api/pacientes` - Listar todos
  - `POST /api/pacientes` - Crear nuevo
  - `GET /api/pacientes/[id]` - Obtener uno
  - `PUT /api/pacientes/[id]` - Actualizar
  - `DELETE /api/pacientes/[id]` - Eliminar

- `/api/especialistas` - CRUD completo de especialistas
  - `GET /api/especialistas` - Listar todos
  - `POST /api/especialistas` - Crear nuevo
  - `GET /api/especialistas/[id]` - Obtener uno
  - `PUT /api/especialistas/[id]` - Actualizar
  - `DELETE /api/especialistas/[id]` - Eliminar

- `/api/historias` - CRUD completo de historias clínicas
  - `GET /api/historias` - Listar todas
  - `POST /api/historias` - Crear nueva
  - `GET /api/historias/[id]` - Obtener una
  - `PUT /api/historias/[id]` - Actualizar
  - `GET /api/historias/paciente/[id_paciente]` - Historias de un paciente

### Integración ML
- `/api/predict` - Proxy a la API de ML de Python para predicciones
