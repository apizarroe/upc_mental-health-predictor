# Esquema de Base de Datos

Este documento describe el esquema de la base de datos para el sistema de predicción de trastornos mentales.

## Diagrama Entidad-Relación

```
┌─────────────────────┐
│   especialista      │
├─────────────────────┤
│ id_especialista (PK)│
│ dni                 │
│ nombres             │
│ apellidos           │
│ especialidad        │
│ colegiatura         │
│ correo              │
│ telefono            │
│ cargo               │
│ flg_activo          │
└─────────────────────┘

┌─────────────────────┐
│     paciente        │
├─────────────────────┤
│ id_paciente (PK)    │
│ dni                 │
│ nombres             │
│ apellidos           │
│ fecha_nacimiento    │
│ sexo                │
│ direccion           │
│ telefono            │
│ correo              │
│ contacto_emergencia │
│ telefono_emergencia │
│ fecha_registro      │
│ flg_activo          │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────┐
│ historia_clinica    │
├─────────────────────┤
│ id_historia (PK)    │
│ id_paciente (FK)    │
│ fecha_apertura      │
│ antecedentes_pers.  │
│ antecedentes_fam.   │
│ tratamientos_prev.  │
│ situacion_historia  │
└─────────────────────┘
```

## Tablas

### paciente
Información de los pacientes del centro de atención psicológica.

| Campo                | Tipo         | Restricciones | Descripción                               |
|---------------------|--------------|---------------|-------------------------------------------|
| id_paciente         | BIGSERIAL    | PRIMARY KEY   | Identificador único del paciente          |
| dni                 | VARCHAR(12)  |               | DNI o documento de identidad              |
| nombres             | VARCHAR(80)  |               | Nombres del paciente                      |
| apellidos           | VARCHAR(80)  |               | Apellidos del paciente                    |
| fecha_nacimiento    | DATE         |               | Fecha de nacimiento                       |
| sexo                | CHAR(1)      |               | Sexo: 'M' o 'F'                          |
| direccion           | VARCHAR(255) |               | Dirección de residencia                   |
| telefono            | VARCHAR(20)  |               | Teléfono de contacto                      |
| correo              | VARCHAR(50)  |               | Email del paciente                        |
| contacto_emergencia | VARCHAR(150) |               | Nombre de contacto de emergencia          |
| telefono_emergencia | VARCHAR(20)  |               | Teléfono de emergencia                    |
| fecha_registro      | TIMESTAMP    |               | Fecha de registro en el sistema           |
| flg_activo          | BOOLEAN      |               | Estado activo/inactivo del paciente       |

**Índices sugeridos:**
```sql
CREATE INDEX idx_paciente_dni ON paciente(dni);
CREATE INDEX idx_paciente_nombres ON paciente(nombres, apellidos);
CREATE INDEX idx_paciente_activo ON paciente(flg_activo);
```

### especialista
Profesionales de salud mental del centro.

| Campo           | Tipo        | Restricciones | Descripción                                  |
|-----------------|-------------|---------------|----------------------------------------------|
| id_especialista | BIGSERIAL   | PRIMARY KEY   | Identificador único del especialista         |
| dni             | VARCHAR(12) |               | DNI del especialista                         |
| nombres         | VARCHAR(80) |               | Nombres del especialista                     |
| apellidos       | VARCHAR(80) |               | Apellidos del especialista                   |
| especialidad    | VARCHAR(50) |               | Especialidad: 'Psicólogo', 'Psiquiatra', etc|
| colegiatura     | VARCHAR(20) |               | Número de colegiatura (CMP, CPsP)           |
| correo          | VARCHAR(50) |               | Email profesional                            |
| telefono        | VARCHAR(20) |               | Teléfono de contacto                         |
| cargo           | VARCHAR(50) |               | Cargo en el centro                           |
| flg_activo      | BOOLEAN     |               | Estado activo/inactivo del especialista      |

**Índices sugeridos:**
```sql
CREATE INDEX idx_especialista_dni ON especialista(dni);
CREATE INDEX idx_especialista_colegiatura ON especialista(colegiatura);
CREATE INDEX idx_especialista_activo ON especialista(flg_activo);
```

### historia_clinica
Historia clínica de cada paciente con antecedentes médicos y psicológicos.

| Campo                    | Tipo        | Restricciones | Descripción                                  |
|--------------------------|-------------|---------------|----------------------------------------------|
| id_historia              | BIGSERIAL   | PRIMARY KEY   | Identificador único de la historia clínica   |
| id_paciente              | BIGINT      | FOREIGN KEY   | Referencia a paciente(id_paciente)           |
| fecha_apertura           | DATE        |               | Fecha de apertura de la historia             |
| antecedentes_personales  | TEXT        |               | Antecedentes personales del paciente         |
| antecedentes_familiares  | TEXT        |               | Antecedentes familiares                      |
| tratamientos_previos     | TEXT        |               | Tratamientos psicológicos previos            |
| situacion_historia       | VARCHAR(20) |               | Estado: 'abierta', 'cerrada', etc            |

**Relaciones:**
- **FK**: `id_paciente` → `paciente(id_paciente)`

**Índices sugeridos:**
```sql
CREATE INDEX idx_historia_paciente ON historia_clinica(id_paciente);
CREATE INDEX idx_historia_situacion ON historia_clinica(situacion_historia);
```

## Script SQL Completo

```sql
-- Tabla paciente
CREATE TABLE "paciente" (
  "id_paciente" BIGSERIAL PRIMARY KEY,
  "dni" VARCHAR(12),
  "nombres" VARCHAR(80),
  "apellidos" VARCHAR(80),
  "fecha_nacimiento" DATE,
  "sexo" CHAR(1),
  "direccion" VARCHAR(255),
  "telefono" VARCHAR(20),
  "correo" VARCHAR(50),
  "contacto_emergencia" VARCHAR(150),
  "telefono_emergencia" VARCHAR(20),
  "fecha_registro" TIMESTAMP,
  "flg_activo" BOOLEAN
);

-- Tabla especialista
CREATE TABLE "especialista" (
  "id_especialista" BIGSERIAL PRIMARY KEY,
  "dni" VARCHAR(12),
  "nombres" VARCHAR(80),
  "apellidos" VARCHAR(80),
  "especialidad" VARCHAR(50),
  "colegiatura" VARCHAR(20),
  "correo" VARCHAR(50),
  "telefono" VARCHAR(20),
  "cargo" VARCHAR(50),
  "flg_activo" BOOLEAN
);

-- Tabla historia_clinica
CREATE TABLE "historia_clinica" (
  "id_historia" BIGSERIAL PRIMARY KEY,
  "id_paciente" BIGINT,
  "fecha_apertura" DATE,
  "antecedentes_personales" TEXT,
  "antecedentes_familiares" TEXT,
  "tratamientos_previos" TEXT,
  "situacion_historia" VARCHAR(20)
);

-- Foreign Key
ALTER TABLE "historia_clinica"
  ADD CONSTRAINT "fk_historia_paciente"
  FOREIGN KEY ("id_paciente")
  REFERENCES "paciente" ("id_paciente");

-- Índices
CREATE INDEX idx_paciente_dni ON paciente(dni);
CREATE INDEX idx_paciente_activo ON paciente(flg_activo);
CREATE INDEX idx_especialista_dni ON especialista(dni);
CREATE INDEX idx_especialista_activo ON especialista(flg_activo);
CREATE INDEX idx_historia_paciente ON historia_clinica(id_paciente);
```

## Consideraciones de Seguridad

1. **Datos Sensibles**:
   - Todos los datos de pacientes son información de salud protegida
   - Cumplir con Ley de Protección de Datos Personales del Perú

2. **Encriptación**:
   - Datos en tránsito: HTTPS/TLS
   - Datos en reposo: Encriptar campos sensibles

3. **Auditoría**:
   - Agregar campos `created_at`, `updated_at` a todas las tablas
   - Implementar tabla de logs de acceso

4. **Backups**:
   - Backups automáticos diarios
   - Encriptación de backups
   - Pruebas de restauración

5. **Control de Acceso**:
   - RBAC (Role-Based Access Control)
   - Especialistas solo ven sus pacientes asignados
   - Administradores tienen acceso completo

## Valores de Ejemplo

### Datos de prueba para desarrollo

```sql
-- Insertar especialista de prueba
INSERT INTO especialista (dni, nombres, apellidos, especialidad, colegiatura, correo, telefono, cargo, flg_activo)
VALUES ('12345678', 'María', 'González Pérez', 'Psicóloga Clínica', 'CPsP12345', 'mgonzalez@centro.com', '987654321', 'Psicóloga Senior', true);

-- Insertar paciente de prueba
INSERT INTO paciente (dni, nombres, apellidos, fecha_nacimiento, sexo, direccion, telefono, correo, contacto_emergencia, telefono_emergencia, fecha_registro, flg_activo)
VALUES ('87654321', 'Juan', 'Pérez López', '1990-05-15', 'M', 'Av. Principal 123', '912345678', 'jperez@email.com', 'María Pérez', '923456789', CURRENT_TIMESTAMP, true);

-- Insertar historia clínica
INSERT INTO historia_clinica (id_paciente, fecha_apertura, antecedentes_personales, antecedentes_familiares, tratamientos_previos, situacion_historia)
VALUES (1, '2024-01-15', 'Sin antecedentes médicos relevantes', 'Historia familiar de ansiedad', 'Ninguno', 'abierta');
```

## Migración de Datos

Si necesitas migrar datos existentes o cambiar el esquema, documentar todas las migraciones en:
- `frontend/src/lib/server/db/migrations/`

## Notas Técnicas

- **Motor**: PostgreSQL (recomendado para producción)
- **Encoding**: UTF-8
- **Timezone**: UTC para todos los timestamps
- **Naming Convention**: snake_case para nombres de tablas y columnas
