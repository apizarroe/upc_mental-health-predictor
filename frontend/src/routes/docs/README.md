# Frontend API Reference — Mental Health Predictor

Base URL: `http://localhost:5173/api`

Endpoints del servidor SvelteKit. Autenticación por cookies HttpOnly (30 min).

---

## Endpoints

| Categoría | Método | Endpoint | Descripción |
|---|---|---|---|
| Auth | POST | `/api/auth/login` | Login especialistas/admin |
| | POST | `/api/auth/login-paciente` | Login pacientes |
| | POST | `/api/auth/logout` | Logout especialistas/admin |
| | POST | `/api/auth/logout-paciente` | Logout pacientes |
| | GET | `/api/auth/session` | Verificar sesión activa |
| Pacientes | GET | `/api/pacientes` | Listar pacientes |
| | POST | `/api/pacientes` | Crear paciente |
| | GET | `/api/pacientes/[id]` | Obtener paciente |
| | PUT | `/api/pacientes/[id]` | Actualizar paciente |
| | DELETE | `/api/pacientes/[id]` | Soft delete (`flg_activo = false`) |
| | GET | `/api/pacientes/buscar-dni/[dni]` | Buscar por DNI |
| | GET | `/api/pacientes/perfil` | Perfil del paciente autenticado |
| | POST | `/api/pacientes/cambiar-password` | Cambiar contraseña |
| | POST | `/api/pacientes/respuestas` | Registrar respuesta + predicción ML |
| | POST | `/api/pacientes/transcribir` | Transcribir audio a texto |
| Especialistas | GET | `/api/especialistas` | Listar especialistas |
| | POST | `/api/especialistas` | Crear especialista |
| | GET | `/api/especialistas/[id]` | Obtener especialista |
| | PUT | `/api/especialistas/[id]` | Actualizar especialista |
| | DELETE | `/api/especialistas/[id]` | Soft delete |
| Historias | GET | `/api/historias` | Listar historias clínicas |
| | POST | `/api/historias` | Crear historia |
| | GET | `/api/historias/[id]` | Obtener historia |
| | PUT | `/api/historias/[id]` | Actualizar historia |
| | POST | `/api/historias/[id]/cerrar` | Cerrar historia |
| | GET | `/api/historias/paciente/[id]` | Historias de un paciente |
| Evaluaciones | POST | `/api/respuestas/[id]/reprocesar` | Reprocesar evaluación ML (síncrono) |
| | POST | `/api/respuestas/[id]/validacion` | Guardar validación clínica del diagnóstico |

---

## Autenticación

### POST `/api/auth/login`

**Requiere**: —

```json
{ "email": "especialista@hospital.com", "password": "password123" }
```

**Response 200** — crea cookie `session` (HttpOnly, 30 min)
```json
{
  "message": "Login exitoso",
  "usuario": {
    "id_especialista": 1,
    "nombres": "Dr. Juan",
    "apellidos": "Pérez",
    "email": "especialista@hospital.com",
    "rol": "especialista"
  }
}
```

---

### POST `/api/auth/login-paciente`

**Requiere**: —

```json
{ "dni": "12345678", "password": "password123" }
```

**Response 200** — crea cookie `session_paciente` (HttpOnly, 30 min)
```json
{
  "message": "Login exitoso",
  "paciente": { "id_paciente": 1, "nombres": "María", "apellidos": "García", "dni": "12345678" },
  "requiresPasswordChange": false
}
```

Si `requiresPasswordChange` es `true`, el frontend redirige al flujo de cambio de contraseña obligatorio en el primer login.

---

## Pacientes

### POST `/api/pacientes`

**Requiere**: sesión especialista/admin

```json
{
  "dni": "12345678",
  "nombres": "María",
  "apellidos": "García",
  "email": "maria@example.com",
  "password": "temporal123",
  "fecha_nacimiento": "1990-05-15",
  "genero": "F",
  "telefono": "987654321",
  "direccion": "Av. Principal 123",
  "estado_civil": "Soltero",
  "ocupacion": "Ingeniera",
  "nivel_educativo": "Universitario",
  "contacto_emergencia_nombre": "Pedro García",
  "contacto_emergencia_telefono": "912345678"
}
```

Validaciones:
- DNI: 8 dígitos
- Email: formato válido
- Teléfono: 9 dígitos
- Password: mínimo 8 caracteres

**Response 201**
```json
{ "id_paciente": 1, "dni": "12345678", "nombres": "María", "apellidos": "García" }
```

---

### POST `/api/pacientes/cambiar-password`

**Requiere**: sesión paciente

```json
{ "password_actual": "temporal123", "password_nueva": "nuevaPassword123" }
```

**Response 200**
```json
{ "message": "Contraseña actualizada exitosamente" }
```

---

### POST `/api/pacientes/respuestas`

**Requiere**: sesión paciente

```json
{
  "respuestas": {
    "question1": "Me siento cansado y sin energía últimamente",
    "question2": "He perdido interés en actividades que antes disfrutaba",
    "question3": "Tengo dificultad para dormir bien",
    "question4": "Me preocupo constantemente por muchas cosas"
  }
}
```

Validaciones:
- Exactamente 4 respuestas
- Mínimo 10 palabras por respuesta
- Máximo 2 respuestas por día (GMT-5 Lima)

**Response 201**
```json
{
  "message": "Respuesta registrada exitosamente. Procesando evaluación...",
  "id_respuesta": 42,
  "fecha_respuesta": "2025-12-09T14:30:00Z"
}
```

La evaluación ML se procesa **asíncronamente** (fire-and-forget). Los pacientes no tienen acceso a los resultados — solo especialistas/admin.

---

### POST `/api/pacientes/transcribir`

**Requiere**: sesión paciente · `multipart/form-data`

```bash
curl -X POST http://localhost:5173/api/pacientes/transcribir \
  -F "audio=@recording.wav"
```

Formatos: wav, mp3, m4a, ogg, webm

**Response 200**
```json
{ "transcription": "Me siento muy cansado y sin energía últimamente", "language": "es", "duration": 3.5 }
```

---

## Especialistas

### POST `/api/especialistas`

**Requiere**: sesión admin

```json
{
  "dni": "87654321",
  "nombres": "Dr. Juan",
  "apellidos": "Pérez",
  "email": "juan@hospital.com",
  "password": "temporal123",
  "telefono": "912345678",
  "especialidad": "Psiquiatría",
  "num_colegiatura": "CMP-12345",
  "anios_experiencia": 10,
  "institucion": "Hospital Nacional",
  "cargo": "Médico Residente",
  "horario_atencion": "Lunes a Viernes 8-16h",
  "rol": "especialista"
}
```

Validaciones:
- DNI: 8 dígitos
- Email: formato válido
- Teléfono: 9 dígitos
- Rol: `admin` o `especialista`

**Response 201**
```json
{ "id_especialista": 1, "nombres": "Dr. Juan", "apellidos": "Pérez", "email": "juan@hospital.com" }
```

---

## Historias Clínicas

### POST `/api/historias`

**Requiere**: sesión especialista/admin

```json
{
  "id_paciente": 1,
  "id_especialista": 2,
  "motivo_consulta": "Síntomas de ansiedad y depresión",
  "diagnostico_inicial": "Evaluación preliminar",
  "antecedentes_familiares": {
    "depresion": true,
    "ansiedad": false,
    "otros": "Diabetes tipo 2"
  },
  "antecedentes_personales": "Sin antecedentes relevantes",
  "habitos_personales": {
    "alcohol": "Ocasional",
    "tabaco": "No",
    "drogas": "No",
    "ejercicio": "3 veces por semana"
  },
  "medicacion_actual": [
    { "nombre": "Sertralina", "dosis": "50mg", "frecuencia": "1 vez al día" }
  ]
}
```

**Response 201**
```json
{ "id_historia": 1, "id_paciente": 1, "fecha_apertura": "2025-12-09T10:00:00Z", "estado": "activo" }
```

---

### POST `/api/historias/[id]/cerrar`

**Requiere**: sesión especialista/admin

Sin body.

**Response 200**
```json
{ "id_historia": 1, "estado": "cerrado", "fecha_cierre": "2025-12-09T16:00:00Z" }
```

---

## Evaluaciones

### POST `/api/respuestas/[id]/reprocesar`

**Requiere**: sesión admin o especialista

Sin body. Proceso **síncrono**: elimina la evaluación anterior, envía al ML API y crea una nueva con auditoría de quién y cuándo reprocesó.

**Response 200**
```json
{
  "success": true,
  "message": "Respuesta reprocesada exitosamente",
  "evaluacion": {
    "id_evaluacion": 15,
    "condiciones_detectadas": {
      "depression": { "detected": true, "probability": 0.78, "keywords": ["cansado", "triste"] },
      "anxiety": { "detected": true, "probability": 0.65, "keywords": ["nervioso", "preocupado"] }
    },
    "nivel_riesgo_global": "moderado",
    "notas_sistema": "Reprocesado por Dr. Juan (especialista) el 2025-12-09T15:30:00Z"
  }
}
```

**Errores**: 401 sesión expirada · 403 rol insuficiente · 404 respuesta no encontrada · 500 error ML o BD

### POST `/api/respuestas/[id]/validacion`

**Requiere**: sesión admin o especialista

```json
{
  "decision": "modificar",
  "diagnosticoEspecialista": {
    "depression": true,
    "anxiety": false
  },
  "nivelConfianza": 90,
  "observaciones": "Los hallazgos clínicos son más consistentes con depresión.",
  "recomendacionPaciente": "Programar seguimiento semanal.",
  "requiereSeguimiento": true
}
```

**Notas**:
- `decision`: `aceptar`, `rechazar` o `modificar`
- Si `decision = aceptar`, el backend fuerza el diagnóstico del especialista a coincidir con el modelo
- Si `decision = rechazar` o `modificar`, la validación queda registrada con sus diferencias para análisis y uso futuro

**Response 200**
```json
{
  "success": true,
  "message": "Validación guardada correctamente",
  "validacion": {
    "id_validacion": 7,
    "id_evaluacion": 15,
    "id_especialista": 2,
    "precision_global": "media",
    "util_para_entrenamiento": true
  }
}
```

**Errores**: 400 body inválido · 401 sesión expirada · 403 rol insuficiente · 409 sin evaluación ML disponible · 422 sin cambios frente al modelo · 500 error BD

---

## Seguridad

- **Cookies HttpOnly** (30 min): previene XSS, expiración automática
- **Bcrypt (10 rounds)**: hashing de contraseñas
- **RBAC**:
  - `admin`: acceso completo
  - `especialista`: gestión de pacientes, historias y evaluaciones
  - `paciente`: solo perfil y respuestas propias
- **Soft delete**: `flg_activo = false` en lugar de DELETE físico
- **Validación Zod**: en todos los endpoints con body

---

## Troubleshooting

| Error | Causa | Solución |
|---|---|---|
| 401 | Sesión expirada | Re-autenticarse |
| 403 | Rol insuficiente | Verificar permisos del usuario |
| 500 (límite de respuestas) | Ya se registraron 2 respuestas hoy | Esperar al día siguiente (GMT-5) |
| 500 (error ML) | ML API no disponible | Verificar que el backend Python esté corriendo en el puerto 8000 |
