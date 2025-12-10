# Frontend API - Mental Health Predictor

Documentación de los endpoints REST del servidor SvelteKit para gestión de pacientes, especialistas, historias clínicas y evaluaciones ML.

## 🚀 Inicio Rápido

El servidor SvelteKit expone una API REST en el puerto 5173 (desarrollo) que maneja:
- Autenticación dual (pacientes y especialistas)
- CRUD de entidades (pacientes, especialistas, historias)
- Gestión de respuestas de pacientes
- Integración con ML API (predicción y transcripción)
- Reprocesamiento de evaluaciones

**Base URL**: `http://localhost:5173/api`

---

## 📡 Endpoints

### Resumen de Endpoints

| Categoría | Método | Endpoint | Descripción |
|-----------|--------|----------|-------------|
| **Autenticación** | POST | `/api/auth/login` | Login especialistas/admin |
| | POST | `/api/auth/login-paciente` | Login pacientes |
| | POST | `/api/auth/logout` | Logout especialistas/admin |
| | POST | `/api/auth/logout-paciente` | Logout pacientes |
| | GET | `/api/auth/session` | Verificar sesión activa |
| **Pacientes** | GET | `/api/pacientes` | Listar pacientes |
| | POST | `/api/pacientes` | Crear paciente |
| | GET | `/api/pacientes/[id]` | Obtener paciente |
| | PUT | `/api/pacientes/[id]` | Actualizar paciente |
| | DELETE | `/api/pacientes/[id]` | Eliminar (soft delete) |
| | GET | `/api/pacientes/buscar-dni/[dni]` | Buscar por DNI |
| | GET | `/api/pacientes/perfil` | Perfil autenticado |
| | POST | `/api/pacientes/cambiar-password` | Cambiar contraseña |
| | POST | `/api/pacientes/respuestas` | Crear respuesta + ML |
| | POST | `/api/pacientes/transcribir` | Transcribir audio |
| **Especialistas** | GET | `/api/especialistas` | Listar especialistas |
| | POST | `/api/especialistas` | Crear especialista |
| | GET | `/api/especialistas/[id]` | Obtener especialista |
| | PUT | `/api/especialistas/[id]` | Actualizar especialista |
| | DELETE | `/api/especialistas/[id]` | Eliminar (soft delete) |
| **Historias** | GET | `/api/historias` | Listar historias |
| | POST | `/api/historias` | Crear historia |
| | GET | `/api/historias/[id]` | Obtener historia |
| | PUT | `/api/historias/[id]` | Actualizar historia |
| | POST | `/api/historias/[id]/cerrar` | Cerrar historia |
| | GET | `/api/historias/paciente/[id]` | Historias de paciente |
| **Evaluaciones** | POST | `/api/respuestas/[id]/reprocesar` | Reprocesar con ML |

---

## 🔐 Autenticación

### 1. Login Especialistas/Admin

**POST** `/api/auth/login`

#### Request Body

```json
{
  "email": "especialista@hospital.com",
  "password": "password123"
}
```

#### Response (200 OK)

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

**Cookie creada**: `session` (HttpOnly, 30 min)

---

### 2. Login Pacientes

**POST** `/api/auth/login-paciente`

#### Request Body

```json
{
  "dni": "12345678",
  "password": "password123"
}
```

#### Response (200 OK)

```json
{
  "message": "Login exitoso",
  "paciente": {
    "id_paciente": 1,
    "nombres": "María",
    "apellidos": "García",
    "dni": "12345678"
  },
  "requiresPasswordChange": false
}
```

**Cookie creada**: `session_paciente` (HttpOnly, 30 min)

---

### 3. Logout

**POST** `/api/auth/logout` - Especialistas/Admin
**POST** `/api/auth/logout-paciente` - Pacientes

#### Response (200 OK)

```json
{
  "message": "Logout exitoso"
}
```

---

## 👥 Pacientes

### 1. Listar Pacientes

**GET** `/api/pacientes`

**Requiere**: Sesión de especialista/admin

#### Response (200 OK)

```json
[
  {
    "id_paciente": 1,
    "nombres": "María",
    "apellidos": "García",
    "dni": "12345678",
    "email": "maria@example.com",
    "fecha_nacimiento": "1990-05-15",
    "genero": "F",
    "telefono": "987654321",
    "direccion": "Av. Principal 123",
    "estado_civil": "Soltero",
    "ocupacion": "Ingeniera",
    "nivel_educativo": "Universitario",
    "contacto_emergencia_nombre": "Pedro García",
    "contacto_emergencia_telefono": "912345678",
    "flg_activo": true,
    "fecha_registro": "2025-12-01T10:30:00Z"
  }
]
```

---

### 2. Crear Paciente

**POST** `/api/pacientes`

**Requiere**: Sesión de especialista/admin

#### Request Body

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

**Validaciones**:
- DNI: 8 dígitos
- Email: formato válido
- Teléfono: 9 dígitos
- Password: mínimo 8 caracteres

#### Response (201 Created)

```json
{
  "id_paciente": 1,
  "dni": "12345678",
  "nombres": "María",
  "apellidos": "García"
}
```

---

### 3. Crear Respuesta de Paciente

**POST** `/api/pacientes/respuestas`

**Requiere**: Sesión de paciente

#### Request Body

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

**Validaciones**:
- Exactamente 4 respuestas
- Cada respuesta mínimo 10 palabras
- Máximo 2 respuestas por día (GMT-5 Lima)

#### Response (201 Created)

```json
{
  "message": "Respuesta registrada exitosamente. Procesando evaluación...",
  "id_respuesta": 42,
  "fecha_respuesta": "2025-12-09T14:30:00Z"
}
```

**Nota**: La evaluación ML se procesa **asíncronamente** (fire-and-forget). El paciente no ve los resultados.

---

### 4. Transcribir Audio

**POST** `/api/pacientes/transcribir`

**Requiere**: Sesión de paciente

**Content-Type**: `multipart/form-data`

#### Request Body

```
audio: archivo.wav (formatos: wav, mp3, m4a, ogg, webm)
```

#### Response (200 OK)

```json
{
  "transcription": "Me siento muy cansado y sin energía últimamente",
  "language": "es",
  "duration": 3.5
}
```

**Errores**:
- 400: Archivo no proporcionado
- 415: Formato no soportado
- 500: Error en transcripción

---

## 👨‍⚕️ Especialistas

### 1. Listar Especialistas

**GET** `/api/especialistas`

**Requiere**: Sesión de admin

#### Response (200 OK)

```json
[
  {
    "id_especialista": 1,
    "nombres": "Dr. Juan",
    "apellidos": "Pérez",
    "dni": "87654321",
    "email": "juan@hospital.com",
    "telefono": "912345678",
    "especialidad": "Psiquiatría",
    "num_colegiatura": "CMP-12345",
    "anios_experiencia": 10,
    "institucion": "Hospital Nacional",
    "cargo": "Médico Residente",
    "horario_atencion": "Lunes a Viernes 8-16h",
    "rol": "especialista",
    "flg_activo": true
  }
]
```

---

### 2. Crear Especialista

**POST** `/api/especialistas`

**Requiere**: Sesión de admin

#### Request Body

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

**Validaciones**:
- DNI: 8 dígitos
- Email: formato válido
- Rol: `admin` o `especialista`
- Teléfono: 9 dígitos

#### Response (201 Created)

```json
{
  "id_especialista": 1,
  "nombres": "Dr. Juan",
  "apellidos": "Pérez",
  "email": "juan@hospital.com"
}
```

---

## 📋 Historias Clínicas

### 1. Crear Historia Clínica

**POST** `/api/historias`

**Requiere**: Sesión de especialista/admin

#### Request Body

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
    {
      "nombre": "Sertralina",
      "dosis": "50mg",
      "frecuencia": "1 vez al día"
    }
  ]
}
```

#### Response (201 Created)

```json
{
  "id_historia": 1,
  "id_paciente": 1,
  "fecha_apertura": "2025-12-09T10:00:00Z",
  "estado": "activo"
}
```

---

### 2. Obtener Historias de un Paciente

**GET** `/api/historias/paciente/[id_paciente]`

**Requiere**: Sesión de especialista/admin

#### Response (200 OK)

```json
[
  {
    "id_historia": 1,
    "id_paciente": 1,
    "id_especialista": 2,
    "motivo_consulta": "Síntomas de ansiedad y depresión",
    "diagnostico_inicial": "Evaluación preliminar",
    "fecha_apertura": "2025-12-09T10:00:00Z",
    "fecha_cierre": null,
    "estado": "activo",
    "especialista": {
      "nombres": "Dr. Juan",
      "apellidos": "Pérez",
      "especialidad": "Psiquiatría"
    }
  }
]
```

---

## 🔄 Reprocesar Evaluaciones

### Reprocesar Respuesta con ML

**POST** `/api/respuestas/[idRespuesta]/reprocesar`

**Requiere**: Sesión de especialista/admin

**Importante**: Este endpoint es **síncrono** - espera el resultado del ML antes de responder.

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Respuesta reprocesada exitosamente",
  "evaluacion": {
    "id_evaluacion": 15,
    "trastornos_detectados": ["depression", "anxiety"],
    "condiciones_detectadas": {
      "depression": {
        "detected": true,
        "probability": 0.78,
        "confidence": 0.82,
        "keywords": ["cansado", "triste", "solo"]
      },
      "anxiety": {
        "detected": true,
        "probability": 0.65,
        "confidence": 0.71,
        "keywords": ["nervioso", "preocupado"]
      }
    },
    "nivel_riesgo_global": "moderado",
    "interpretacion": "Se detectaron indicadores de depresión (78%) y ansiedad (65%)",
    "requiere_atencion": true,
    "notas_sistema": "Reprocesado por Dr. Juan (especialista) el 2025-12-09T15:30:00Z"
  }
}
```

**Flujo**:
1. Valida sesión y rol (admin/especialista)
2. Cambia estado a `pendiente`
3. **DELETE** evaluación anterior
4. Envía a ML API (espera resultado)
5. Crea nueva evaluación
6. Guarda auditoría en `notas_sistema`
7. Actualiza estado a `procesado`

**Errores**:
- 401: No autorizado
- 403: Rol insuficiente
- 404: Respuesta no encontrada
- 500: Error en ML o BD

---

## 🔒 Seguridad

### Autenticación
- **Cookies HttpOnly**: Previene XSS
- **Sesiones de 30 minutos**: Expiración automática
- **Bcrypt (10 rounds)**: Hashing seguro de contraseñas
- **Dual sessions**: Pacientes y especialistas separados

### Autorización
- **RBAC**: Role-Based Access Control
  - `admin`: Acceso completo
  - `especialista`: Gestión de pacientes, historias, evaluaciones
  - `paciente`: Solo perfil y respuestas propias

### Validación
- **Zod schemas**: Validación estricta de inputs
- **Sanitización**: Prevención de SQL injection
- **Soft delete**: Flag `flg_activo` en lugar de DELETE físico

---

## 🌍 Timezone

**IMPORTANTE**: El sistema opera en **GMT-5 (America/Lima)**.

### Consideraciones:
- PostgreSQL guarda timestamps en GMT-5
- Frontend maneja conversiones con `Intl.DateTimeFormat`
- Límite de 2 respuestas por día usa comparación de strings con `TO_CHAR()`
- Función `getRespuestasDelDia()` maneja timezone correctamente

---

## 💡 Notas Importantes

### Procesamiento ML

**Asíncrono (Fire-and-Forget)**:
- Usado en: `POST /api/pacientes/respuestas`
- Ventaja: Usuario no espera
- Desventaja: No hay feedback inmediato

**Síncrono (Blocking)**:
- Usado en: `POST /api/respuestas/[id]/reprocesar`
- Ventaja: Feedback inmediato
- Desventaja: Usuario espera (~5-10 segundos)

### Confidencialidad
- Pacientes **NO ven** evaluaciones ML
- Solo especialistas/admin acceden a trastornos detectados
- Historial de pacientes muestra solo respuestas

### Límite Diario
- Máximo 2 respuestas por día por paciente
- Validación en GMT-5 Lima
- Evita spam y mantiene calidad de datos

---

## 🐛 Troubleshooting

### Error 401: No autorizado
- Cookie expirada (30 min)
- Sesión inválida
- **Solución**: Re-autenticarse

### Error 403: Acceso denegado
- Rol insuficiente para la operación
- **Solución**: Verificar permisos del usuario

### Error 500: Límite de respuestas alcanzado
- Ya se enviaron 2 respuestas hoy
- **Solución**: Esperar al día siguiente (GMT-5)

### Error 500: Error ML
- ML API no disponible
- Timeout en procesamiento
- **Solución**: Verificar que backend Python esté corriendo en puerto 8000

---

## 📝 Changelog

### v2.0.0 (2025-12-09)
- ✨ **NUEVO**: Endpoint de reprocesar evaluaciones (síncrono)
- 🎙️ **NUEVO**: Transcripción de audio con Faster-Whisper
- 🔒 Mejoras en confidencialidad (pacientes no ven evaluaciones)
- 🌍 Fix timezone GMT-5 para respuestas del día
- 📝 Auditoría de reprocesamiento

### v1.0.0 (2025-11-20)
- ✨ Implementación inicial
- 🔐 Autenticación dual (pacientes/especialistas)
- 📊 CRUD completo de entidades
- 🤖 Integración con ML API
- 📋 Gestión de historias clínicas
