# API CRUD - Pacientes

Documentación de los endpoints para gestión de pacientes en el sistema.

## Base URL

```
http://localhost:5173/api/pacientes
```

## Endpoints

### 1. Listar todos los pacientes

```bash
GET /api/pacientes
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id_paciente": 1,
      "dni": "12345678",
      "nombres": "Juan",
      "apellidos": "Pérez García",
      "fecha_nacimiento": "1990-05-15",
      "sexo": "M",
      "direccion": "Av. Principal 123",
      "telefono": "987654321",
      "correo": "juan.perez@email.com",
      "contacto_emergencia": "María Pérez",
      "telefono_emergencia": "923456789",
      "fecha_registro": "2024-10-27T04:30:00.000Z",
      "flg_activo": true
    }
  ],
  "count": 1
}
```

### 2. Obtener un paciente por ID

```bash
GET /api/pacientes/:id
```

**Ejemplo:**
```bash
curl http://localhost:5173/api/pacientes/1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_paciente": 1,
    "dni": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "direccion": "Av. Principal 123",
    "telefono": "987654321",
    "correo": "juan.perez@email.com",
    "contacto_emergencia": "María Pérez",
    "telefono_emergencia": "923456789",
    "fecha_registro": "2024-10-27T04:30:00.000Z",
    "flg_activo": true
  }
}
```

**Respuesta error (404):**
```json
{
  "success": false,
  "error": "Paciente no encontrado"
}
```

### 3. Crear un nuevo paciente

```bash
POST /api/pacientes
```

**Body (JSON):**
```json
{
  "dni": "12345678",
  "nombres": "Juan",
  "apellidos": "Pérez García",
  "fecha_nacimiento": "1990-05-15",
  "sexo": "M",
  "direccion": "Av. Principal 123",
  "telefono": "987654321",
  "correo": "juan.perez@email.com",
  "contacto_emergencia": "María Pérez",
  "telefono_emergencia": "923456789"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5173/api/pacientes \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "direccion": "Av. Principal 123",
    "telefono": "987654321",
    "correo": "juan.perez@email.com",
    "contacto_emergencia": "María Pérez",
    "telefono_emergencia": "923456789"
  }'
```

**Campos requeridos:**
- `dni` (string, max 12)
- `nombres` (string, max 80)
- `apellidos` (string, max 80)
- `fecha_nacimiento` (date, formato YYYY-MM-DD)
- `sexo` (char, 'M' o 'F')
- `direccion` (string, max 255)
- `telefono` (string, max 20)
- `correo` (string, email, max 50)
- `contacto_emergencia` (string, max 150)
- `telefono_emergencia` (string, max 20)

**Campos auto-generados:**
- `id_paciente`: Auto-incremental (BIGSERIAL)
- `fecha_registro`: Se setea automáticamente con NOW()
- `flg_activo`: Se setea automáticamente en `true`

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "data": {
    "id_paciente": 1,
    "dni": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "direccion": "Av. Principal 123",
    "telefono": "987654321",
    "correo": "juan.perez@email.com",
    "contacto_emergencia": "María Pérez",
    "telefono_emergencia": "923456789",
    "fecha_registro": "2024-10-27T04:30:00.000Z",
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

### 4. Actualizar un paciente

```bash
PUT /api/pacientes/:id
```

**Body (JSON) - Todos los campos son opcionales:**
```json
{
  "telefono": "999888777",
  "direccion": "Nueva Direccion 456"
}
```

**Ejemplo con curl:**
```bash
curl -X PUT http://localhost:5173/api/pacientes/1 \
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
    "id_paciente": 1,
    "dni": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "direccion": "Nueva Direccion 456",
    "telefono": "999888777",
    "correo": "juan.perez@email.com",
    "contacto_emergencia": "María Pérez",
    "telefono_emergencia": "923456789",
    "fecha_registro": "2024-10-27T04:30:00.000Z",
    "flg_activo": true
  }
}
```

### 5. Eliminar (desactivar) un paciente

```bash
DELETE /api/pacientes/:id
```

**Ejemplo:**
```bash
curl -X DELETE http://localhost:5173/api/pacientes/1
```

**Nota:** Esta operación NO elimina físicamente el registro, solo setea `flg_activo = false` (soft delete).

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_paciente": 1,
    "dni": "12345678",
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "sexo": "M",
    "direccion": "Av. Principal 123",
    "telefono": "987654321",
    "correo": "juan.perez@email.com",
    "contacto_emergencia": "María Pérez",
    "telefono_emergencia": "923456789",
    "fecha_registro": "2024-10-27T04:30:00.000Z",
    "flg_activo": false
  },
  "message": "Paciente desactivado exitosamente"
}
```

## Validaciones

- **dni**: String, máximo 12 caracteres
- **nombres**: String, máximo 80 caracteres
- **apellidos**: String, máximo 80 caracteres
- **fecha_nacimiento**: Date en formato YYYY-MM-DD
- **sexo**: Char(1), solo acepta 'M' o 'F'
- **direccion**: String, máximo 255 caracteres
- **telefono**: String, máximo 20 caracteres
- **correo**: String formato email válido, máximo 50 caracteres
- **contacto_emergencia**: String, máximo 150 caracteres
- **telefono_emergencia**: String, máximo 20 caracteres

## Códigos de Estado HTTP

- `200` - OK: Operación exitosa
- `201` - Created: Recurso creado exitosamente
- `400` - Bad Request: Datos inválidos
- `404` - Not Found: Recurso no encontrado
- `500` - Internal Server Error: Error del servidor

## Notas

- El campo `flg_activo` se usa para soft delete (eliminación lógica)
- Solo se listan pacientes con `flg_activo = true` por defecto
- El `id_paciente` es auto-generado y no debe enviarse en POST
- Los campos `fecha_registro` y `flg_activo` se setean automáticamente en la creación

