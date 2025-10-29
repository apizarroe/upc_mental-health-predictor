# API CRUD - Especialistas

Documentación de los endpoints para gestión de especialistas en el sistema.

## Base URL

```
http://localhost:5173/api/especialistas
```

## Endpoints

### 1. Listar todos los especialistas

```bash
GET /api/especialistas
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id_especialista": 1,
      "dni": "12345678",
      "nombres": "María",
      "apellidos": "González Pérez",
      "especialidad": "Psicóloga Clínica",
      "colegiatura": "CPsP12345",
      "correo": "mgonzalez@centro.com",
      "telefono": "987654321",
      "cargo": "Psicóloga Senior",
      "flg_activo": true
    }
  ],
  "count": 1
}
```

### 2. Obtener un especialista por ID

```bash
GET /api/especialistas/:id
```

**Ejemplo:**
```bash
curl http://localhost:5173/api/especialistas/1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_especialista": 1,
    "dni": "12345678",
    "nombres": "María",
    "apellidos": "González Pérez",
    "especialidad": "Psicóloga Clínica",
    "colegiatura": "CPsP12345",
    "correo": "mgonzalez@centro.com",
    "telefono": "987654321",
    "cargo": "Psicóloga Senior",
    "flg_activo": true
  }
}
```

**Respuesta error (404):**
```json
{
  "success": false,
  "error": "Especialista no encontrado"
}
```

### 3. Crear un nuevo especialista

```bash
POST /api/especialistas
```

**Body (JSON):**
```json
{
  "dni": "12345678",
  "nombres": "María",
  "apellidos": "González Pérez",
  "especialidad": "Psicóloga Clínica",
  "colegiatura": "CPsP12345",
  "correo": "mgonzalez@centro.com",
  "telefono": "987654321",
  "cargo": "Psicóloga Senior"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5173/api/especialistas \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "nombres": "María",
    "apellidos": "González Pérez",
    "especialidad": "Psicóloga Clínica",
    "colegiatura": "CPsP12345",
    "correo": "mgonzalez@centro.com",
    "telefono": "987654321",
    "cargo": "Psicóloga Senior"
  }'
```

**Campos requeridos:**
- `dni` (string, max 12)
- `nombres` (string, max 80)
- `apellidos` (string, max 80)
- `especialidad` (string, max 50)
- `colegiatura` (string, max 20)
- `correo` (string, email, max 50)
- `telefono` (string, max 20)
- `cargo` (string, max 50)

**Campos auto-generados:**
- `id_especialista`: Auto-incremental (BIGSERIAL)
- `flg_activo`: Se setea automáticamente en `true`

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "data": {
    "id_especialista": 1,
    "dni": "12345678",
    "nombres": "María",
    "apellidos": "González Pérez",
    "especialidad": "Psicóloga Clínica",
    "colegiatura": "CPsP12345",
    "correo": "mgonzalez@centro.com",
    "telefono": "987654321",
    "cargo": "Psicóloga Senior",
    "flg_activo": true
  }
}
```

**Respuesta error (400):**
```json
{
  "success": false,
  "error": "Datos de entrada inválidos"
}
```

### 4. Actualizar un especialista

```bash
PUT /api/especialistas/:id
```

**Body (JSON) - Todos los campos son opcionales:**
```json
{
  "telefono": "999888777",
  "correo": "nuevo.correo@centro.com"
}
```

**Ejemplo con curl:**
```bash
curl -X PUT http://localhost:5173/api/especialistas/1 \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "999888777"
  }'
```

**Notas:**
- Solo se actualizan los campos enviados en el body
- Los campos no enviados mantienen su valor actual
- Puedes actualizar uno o varios campos a la vez

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_especialista": 1,
    "dni": "12345678",
    "nombres": "María",
    "apellidos": "González Pérez",
    "especialidad": "Psicóloga Clínica",
    "colegiatura": "CPsP12345",
    "correo": "nuevo.correo@centro.com",
    "telefono": "999888777",
    "cargo": "Psicóloga Senior",
    "flg_activo": true
  }
}
```

### 5. Eliminar (desactivar) un especialista

```bash
DELETE /api/especialistas/:id
```

**Ejemplo:**
```bash
curl -X DELETE http://localhost:5173/api/especialistas/1
```

**Nota:** Esta operación NO elimina físicamente el registro, solo setea `flg_activo = false` (soft delete).

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_especialista": 1,
    "dni": "12345678",
    "nombres": "María",
    "apellidos": "González Pérez",
    "especialidad": "Psicóloga Clínica",
    "colegiatura": "CPsP12345",
    "correo": "mgonzalez@centro.com",
    "telefono": "987654321",
    "cargo": "Psicóloga Senior",
    "flg_activo": false
  },
  "message": "Especialista desactivado exitosamente"
}
```

## Validaciones

- **dni**: String, máximo 12 caracteres
- **nombres**: String, máximo 80 caracteres
- **apellidos**: String, máximo 80 caracteres
- **especialidad**: String, máximo 50 caracteres
- **colegiatura**: String, máximo 20 caracteres
- **correo**: String formato email válido, máximo 50 caracteres
- **telefono**: String, máximo 20 caracteres
- **cargo**: String, máximo 50 caracteres

## Códigos de Estado HTTP

- `200` - OK: Operación exitosa
- `201` - Created: Recurso creado exitosamente
- `400` - Bad Request: Datos inválidos
- `404` - Not Found: Recurso no encontrado
- `500` - Internal Server Error: Error del servidor

## Notas

- El campo `flg_activo` se usa para soft delete (eliminación lógica)
- Solo se listan especialistas con `flg_activo = true` por defecto
- El `id_especialista` es auto-generado y no debe enviarse en POST
