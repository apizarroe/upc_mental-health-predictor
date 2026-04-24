# Frontend — Mental Health Predictor

Aplicación SvelteKit con SSR + CSR. Implementa dos portales (especialistas y pacientes), API REST server-side, integración con el ML API y PostgreSQL.

## Instalación

```bash
cd frontend
npm install
```

## Desarrollo

```bash
# Servidor de desarrollo
npm run dev

# Build y preview de producción
npm run build
npm run preview

# Tests
npm run test
npm run test:watch
npm run test:coverage

# Linting y formato
npm run lint
npm run format
npm run check
```

## Variables de entorno

Copiar `.env.example` a `.env`:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión PostgreSQL (timezone GMT-5 Lima) |
| `PUBLIC_ML_API_URL` | URL del ML API (default: `http://localhost:8000`) |
| `AUTH_SECRET` | Secret para firmar cookies de sesión |

## Estructura

```
frontend/src/
├── lib/
│   ├── components/          # Componentes reutilizables (forms, ui)
│   ├── server/
│   │   ├── db/              # postgres.js
│   │   ├── services/        # Lógica de negocio (pacientes, especialistas, historias, ML)
│   │   └── validators/      # Schemas Zod
│   └── utils/
└── routes/
    ├── (app)/               # Portal especialistas/admin
    │   ├── dashboard/       # Métricas y estadísticas
    │   ├── pacientes/       # CRUD + historial de respuestas
    │   ├── especialistas/   # CRUD
    │   └── historias/       # Historias clínicas
    ├── paciente/            # Portal pacientes
    │   ├── notas/           # Cuestionario diario + historial
    │   └── perfil/
    └── api/                 # API REST (ver API_README.md)
```

## Rutas

### Portal Especialistas/Admin

| Ruta | Descripción |
|---|---|
| `/(app)/inicio` | Página de inicio |
| `/(app)/dashboard` | Métricas y estadísticas |
| `/(app)/pacientes` | Lista de pacientes |
| `/(app)/pacientes/[id]/notas` | Historial de respuestas |
| `/(app)/pacientes/[id]/notas/[idRespuesta]` | Detalle + reprocesar con ML |
| `/(app)/especialistas` | Gestión de especialistas |
| `/(app)/historias` | Historias clínicas |
| `/login/especialista` | Login especialistas/admin |

### Portal Pacientes

| Ruta | Descripción |
|---|---|
| `/paciente/inicio` | Inicio del paciente |
| `/paciente/notas` | Cuestionario diario (4 preguntas + audio opcional) |
| `/paciente/notas/historial` | Historial personal (sin evaluaciones ML) |
| `/paciente/perfil` | Perfil y cambio de contraseña |

## Autenticación

El sistema mantiene dos sesiones separadas:

| Sesión | Cookie | Roles | Login |
|---|---|---|---|
| Especialistas/Admin | `session` | `admin`, `especialista` | `/login/especialista` |
| Pacientes | `session_paciente` | `paciente` | `/` |

Ambas expiran en 30 minutos. El primer login fuerza cambio de contraseña.

## Integración con ML

**Asíncrono (fire-and-forget)** — `POST /api/pacientes/respuestas`: guarda la respuesta y dispara la evaluación ML sin bloquear. El paciente no ve los resultados; solo especialistas/admin.

**Síncrono** — `POST /api/respuestas/[id]/reprocesar`: espera el resultado del ML antes de responder. Genera auditoría (quién reprocesó y cuándo).

## Tecnologías

### Frontend
- **SvelteKit 2.0+**: Framework full-stack con SSR + CSR
- **Svelte 4**: Framework reactivo
- **TailwindCSS**: Estilos utility-first

### Servidor (SvelteKit server-side)
- **Node.js**: Runtime
- **postgres.js**: Cliente PostgreSQL ligero, sin ORM
- **Bcrypt**: Hashing de contraseñas
- **Zod**: Validación de schemas en endpoints

### Base de datos
- **PostgreSQL 17.6**: Relacional con JSONB para campos complejos (antecedentes, hábitos, evaluaciones)
- **Timezone**: GMT-5 (America/Lima)

## Documentación

- [API Reference](API_README.md) — endpoints, autenticación, request/response, seguridad
