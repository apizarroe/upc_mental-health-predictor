# API CRUD - Historias Clínicas

Documentación de los endpoints para gestión de historias clínicas en el sistema.

## Base URL

```
http://localhost:5173/api/historias
```

## Endpoints

### 1. Listar todas las historias clínicas

```bash
GET /api/historias
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id_historia": 1,
      "id_paciente": 1,
      "fecha_apertura": "2024-01-15",
      "antecedentes_personales": "Sin antecedentes médicos relevantes",
      "antecedentes_familiares": "Historia familiar de ansiedad",
      "tratamientos_previos": "Ninguno",
      "situacion_historia": "abierta"
    }
  ],
  "count": 1
}
```

### 2. Obtener una historia clínica por ID

```bash
GET /api/historias/:id
```

**Ejemplo:**
```bash
curl http://localhost:5173/api/historias/1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_historia": 1,
    "id_paciente": 1,
    "fecha_apertura": "2024-01-15",
    "antecedentes_personales": "Sin antecedentes médicos relevantes",
    "antecedentes_familiares": "Historia familiar de ansiedad",
    "tratamientos_previos": "Ninguno",
    "situacion_historia": "abierta"
  }
}
```

**Respuesta error (404):**
```json
{
  "success": false,
  "error": "Historia clínica no encontrada"
}
```

### 3. Obtener historias clínicas por paciente

```bash
GET /api/historias/paciente/:id_paciente
```

**Ejemplo:**
```bash
curl http://localhost:5173/api/historias/paciente/1
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": [
    {
      "id_historia": 1,
      "id_paciente": 1,
      "fecha_apertura": "2024-01-15",
      "antecedentes_personales": "Sin antecedentes médicos relevantes",
      "antecedentes_familiares": "Historia familiar de ansiedad",
      "tratamientos_previos": "Ninguno",
      "situacion_historia": "abierta"
    }
  ],
  "count": 1
}
```

### 4. Crear una nueva historia clínica

```bash
POST /api/historias
```

**Body (JSON):**
```json
{
  "id_paciente": 1,
  "fecha_apertura": "2024-01-15",
  "antecedentes_personales": "Sin antecedentes médicos relevantes",
  "antecedentes_familiares": "Historia familiar de ansiedad",
  "tratamientos_previos": "Ninguno",
  "situacion_historia": "abierta"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5173/api/historias \
  -H "Content-Type: application/json" \
  -d '{
    "id_paciente": 1,
    "fecha_apertura": "2024-01-15",
    "antecedentes_personales": "Sin antecedentes médicos relevantes",
    "antecedentes_familiares": "Historia familiar de ansiedad",
    "tratamientos_previos": "Ninguno",
    "situacion_historia": "abierta"
  }'
```

**Campos requeridos:**
- `id_paciente` (bigint, FK a paciente)
- `fecha_apertura` (date)
- `antecedentes_personales` (text)
- `antecedentes_familiares` (text)
- `tratamientos_previos` (text)
- `situacion_historia` (string, max 20)

**Valores comunes para situacion_historia:**
- `abierta`
- `cerrada`
- `en_revision`

**Campos auto-generados:**
- `id_historia`: Auto-incremental (BIGSERIAL)

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "data": {
    "id_historia": 1,
    "id_paciente": 1,
    "fecha_apertura": "2024-01-15",
    "antecedentes_personales": "Sin antecedentes médicos relevantes",
    "antecedentes_familiares": "Historia familiar de ansiedad",
    "tratamientos_previos": "Ninguno",
    "situacion_historia": "abierta"
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

### 5. Actualizar una historia clínica

```bash
PUT /api/historias/:id
```

**Body (JSON) - Todos los campos son opcionales:**
```json
{
  "antecedentes_personales": "Actualización de antecedentes personales",
  "situacion_historia": "cerrada"
}
```

**Ejemplo con curl:**
```bash
curl -X PUT http://localhost:5173/api/historias/1 \
  -H "Content-Type: application/json" \
  -d '{
    "situacion_historia": "cerrada"
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
    "id_historia": 1,
    "id_paciente": 1,
    "fecha_apertura": "2024-01-15",
    "antecedentes_personales": "Actualización de antecedentes personales",
    "antecedentes_familiares": "Historia familiar de ansiedad",
    "tratamientos_previos": "Ninguno",
    "situacion_historia": "cerrada"
  }
}
```

### 6. Eliminar una historia clínica

```bash
DELETE /api/historias/:id
```

**Ejemplo:**
```bash
curl -X DELETE http://localhost:5173/api/historias/1
```

**Nota:** Esta operación elimina físicamente el registro de la base de datos. Usar con precaución.

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "id_historia": 1,
    "id_paciente": 1,
    "fecha_apertura": "2024-01-15",
    "antecedentes_personales": "Sin antecedentes médicos relevantes",
    "antecedentes_familiares": "Historia familiar de ansiedad",
    "tratamientos_previos": "Ninguno",
    "situacion_historia": "abierta"
  },
  "message": "Historia clínica eliminada exitosamente"
}
```

## Validaciones

- **id_paciente**: Bigint, debe existir en la tabla paciente
- **fecha_apertura**: Date formato YYYY-MM-DD
- **antecedentes_personales**: Text (sin límite de longitud)
- **antecedentes_familiares**: Text (sin límite de longitud)
- **tratamientos_previos**: Text (sin límite de longitud)
- **situacion_historia**: String, máximo 20 caracteres

## Códigos de Estado HTTP

- `200` - OK: Operación exitosa
- `201` - Created: Recurso creado exitosamente
- `400` - Bad Request: Datos inválidos
- `404` - Not Found: Recurso no encontrado
- `500` - Internal Server Error: Error del servidor

## Relaciones

- Cada historia clínica pertenece a **un paciente** (`id_paciente` FK)
- Un paciente puede tener **múltiples historias clínicas**

## Notas

- El `id_historia` es auto-generado y no debe enviarse en POST
- El `id_paciente` debe existir en la tabla paciente
- Los campos de texto (TEXT) no tienen límite de longitud
- Se recomienda validar que el paciente existe antes de crear una historia clínica
