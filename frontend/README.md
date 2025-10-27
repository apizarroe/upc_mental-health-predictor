# Frontend - Mental Health Predictor

Aplicación web SvelteKit que maneja tanto el frontend como el backend CRUD para la gestión de pacientes, especialistas e historias clínicas.

## Estructura

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/     # Componentes Svelte reutilizables
│   │   ├── stores/         # Estado global (Svelte stores)
│   │   ├── server/         # Código del servidor (DB, servicios)
│   │   └── utils/          # Funciones auxiliares
│   └── routes/             # Páginas y API routes
│       ├── (app)/          # Rutas autenticadas
│       ├── api/            # API endpoints
│       └── auth/           # Autenticación
├── static/                 # Archivos estáticos
└── tests/                  # Tests
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
