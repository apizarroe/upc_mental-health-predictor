# Esquema de Base de Datos

Este documento describe el esquema de la base de datos para el sistema de predicción de trastornos mentales.

## Tablas

### paciente
Información de los pacientes del centro de atención psicológica con acceso al sistema.

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
| usuario             | VARCHAR(50)  | UNIQUE        | Nombre de usuario para login (único)      |
| password_hash       | VARCHAR(255) |               | Contraseña hasheada (bcrypt)              |
| rol                 | VARCHAR(20)  | DEFAULT 'paciente' | Rol fijo: 'paciente'                 |
| ultimo_acceso       | TIMESTAMP    |               | Fecha y hora del último inicio de sesión  |
| intentos_fallidos   | INT          | DEFAULT 0     | Contador de intentos fallidos de login    |
| bloqueado_hasta     | TIMESTAMP    |               | Fecha hasta la cual está bloqueada la cuenta |
| fecha_registro      | TIMESTAMP    | DEFAULT NOW   | Fecha de registro en el sistema           |
| flg_activo          | BOOLEAN      | DEFAULT true  | Estado activo/inactivo del paciente       |

**Índices sugeridos:**
```sql
CREATE INDEX idx_paciente_dni ON paciente(dni);
CREATE INDEX idx_paciente_nombres ON paciente(nombres, apellidos);
CREATE INDEX idx_paciente_activo ON paciente(flg_activo);
CREATE UNIQUE INDEX idx_paciente_usuario ON paciente(usuario);
CREATE INDEX idx_paciente_rol ON paciente(rol);
```

### especialista
Profesionales de salud mental del centro con credenciales de acceso al sistema.

| Campo              | Tipo         | Restricciones | Descripción                                  |
|--------------------|--------------|---------------|----------------------------------------------|
| id_especialista    | BIGSERIAL    | PRIMARY KEY   | Identificador único del especialista         |
| dni                | VARCHAR(12)  |               | DNI del especialista                         |
| nombres            | VARCHAR(80)  |               | Nombres del especialista                     |
| apellidos          | VARCHAR(80)  |               | Apellidos del especialista                   |
| especialidad       | VARCHAR(50)  |               | Especialidad: 'Psicólogo', 'Psiquiatra', etc|
| colegiatura        | VARCHAR(20)  |               | Número de colegiatura (CMP, CPsP)           |
| correo             | VARCHAR(50)  |               | Email profesional                            |
| telefono           | VARCHAR(20)  |               | Teléfono de contacto                         |
| cargo              | VARCHAR(50)  |               | Cargo en el centro                           |
| usuario            | VARCHAR(50)  | UNIQUE        | Nombre de usuario para login (único)         |
| password_hash      | VARCHAR(255) |               | Contraseña hasheada (bcrypt)                 |
| rol                | VARCHAR(20)  | DEFAULT 'especialista' | Rol: 'admin', 'especialista', 'coordinador' |
| ultimo_acceso      | TIMESTAMP    |               | Fecha y hora del último inicio de sesión     |
| intentos_fallidos  | INT          | DEFAULT 0     | Contador de intentos fallidos de login       |
| bloqueado_hasta    | TIMESTAMP    |               | Fecha hasta la cual está bloqueada la cuenta |
| flg_activo         | BOOLEAN      | DEFAULT true  | Estado activo/inactivo del especialista      |

**Índices sugeridos:**
```sql
CREATE INDEX idx_especialista_dni ON especialista(dni);
CREATE INDEX idx_especialista_colegiatura ON especialista(colegiatura);
CREATE INDEX idx_especialista_activo ON especialista(flg_activo);
CREATE UNIQUE INDEX idx_especialista_usuario ON especialista(usuario);
CREATE INDEX idx_especialista_rol ON especialista(rol);
```

### historia_clinica
Historia clínica de cada paciente con información detallada de antecedentes médicos, psicológicos, familiares y situación actual del paciente al momento de apertura de la historia.

| Campo                       | Tipo        | Restricciones | Descripción                                          |
|-----------------------------|-------------|---------------|------------------------------------------------------|
| id_historia                 | BIGSERIAL   | PRIMARY KEY   | Identificador único de la historia clínica           |
| id_paciente                 | BIGINT      | FOREIGN KEY   | Referencia a paciente(id_paciente)                   |
| fecha_apertura              | TIMESTAMP   | DEFAULT NOW   | Fecha y hora de apertura de la historia             |
| especialista_apertura       | BIGINT      | FOREIGN KEY   | ID del especialista que abrió la historia            |
| servicio_origen             | VARCHAR(100)|               | Servicio o área de origen del paciente               |
| antecedentes_personales     | TEXT        |               | Antecedentes médicos y psicológicos personales       |
| antecedentes_familiares     | TEXT        |               | Antecedentes familiares en formato JSON: depresion, ansiedad, bipolaridad, esquizofrenia, tdah, toc, adicciones, suicidio, otros (booleanos) |
| antecedentes_psicosociales  | TEXT        |               | Contexto psicosocial del paciente                    |
| habitos_personales          | TEXT        |               | Hábitos en formato JSON plano: alcohol, alcohol_frecuencia, tabaco, tabaco_frecuencia, drogas, drogas_frecuencia, sueño_horas, sueño_calidad, alimentacion, ejercicio, otros |
| situacion_familiar          | TEXT        |               | Descripción de la dinámica familiar actual           |
| situacion_laboral           | TEXT        |               | Situación laboral y ocupacional actual               |
| evaluacion_inicial          | TEXT        |               | Evaluación psicológica inicial                       |
| diagnostico_inicial         | TEXT        |               | Diagnóstico o impresión diagnóstica inicial          |
| tratamientos_previos        | TEXT        |               | Tratamientos psicológicos previos recibidos          |
| situacion_historia          | VARCHAR(20) |               | Estado: 'abierta', 'cerrada', 'en_revision'          |
| fecha_actualizacion         | TIMESTAMP   |               | Última fecha de actualización de la historia         |
| especialista_actualizacion  | BIGINT      |               | ID del último especialista que actualizó             |
| fecha_cierre                | TIMESTAMP   |               | Fecha de cierre de la historia                       |
| motivo_cierre               | TEXT        |               | Motivo o razón del cierre de la historia             |

**Relaciones:**
- **FK**: `id_paciente` → `paciente(id_paciente)`
- **FK**: `especialista_apertura` → `especialista(id_especialista)`
- **FK**: `especialista_actualizacion` → `especialista(id_especialista)`

**Índices:**
```sql
CREATE INDEX idx_historia_paciente ON historia_clinica(id_paciente);
```

### paciente_medicacion
Registro de medicaciones que el paciente ya tomaba al momento de la apertura de la historia clínica (medicamentos por preexistencias o condiciones previas).

| Campo                    | Tipo         | Restricciones | Descripción                                          |
|--------------------------|--------------|---------------|------------------------------------------------------|
| id_medicacion_paciente   | SERIAL       | PRIMARY KEY   | Identificador único del registro de medicación       |
| id_historia              | INT          | FOREIGN KEY   | Referencia a historia_clinica(id_historia)           |
| medicacion               | VARCHAR(150) | NOT NULL      | Nombre del medicamento                               |
| concentracion            | VARCHAR(50)  |               | Concentración (ej: "50 mg", "10 mg/ml")              |
| forma_farmaceutica       | VARCHAR(50)  |               | Forma farmacéutica (Tableta, Cápsula, Jarabe, etc.)  |
| dosis                    | VARCHAR(50)  |               | Dosis administrada (ej: "1 tableta", "5 ml")         |
| frecuencia               | VARCHAR(50)  |               | Frecuencia de administración (ej: "Cada 8 horas")    |
| anio_inicio              | INT          |               | Año de inicio del tratamiento                        |
| tipo_medicacion          | VARCHAR(50)  |               | Tipo (ej: "Crónica", "Psicotrópico", "Antidepresivo")|
| prescrito_por            | VARCHAR(100) |               | Nombre del médico o centro que prescribió            |
| observaciones            | TEXT         |               | Comentarios o detalles adicionales sobre el medicamento |
| fecha_registro           | TIMESTAMP    | DEFAULT NOW   | Fecha de registro en el sistema                      |

**Relaciones:**
- **FK**: `id_historia` → `historia_clinica(id_historia)`

**Índices:**
```sql
CREATE INDEX idx_medicacion_historia ON paciente_medicacion(id_historia);
```

### notas
Notas diarias del paciente sobre su estado emocional, actividades y situaciones. Los pacientes registran estas notas directamente en el sistema y los especialistas pueden leerlas.

| Campo              | Tipo         | Restricciones | Descripción                                          |
|--------------------|--------------|---------------|------------------------------------------------------|
| id_nota            | BIGSERIAL    | PRIMARY KEY   | Identificador único de la nota                       |
| id_paciente        | BIGINT       | FOREIGN KEY   | Referencia a paciente(id_paciente)                   |
| pregunta           | VARCHAR(255) | NOT NULL      | Pregunta que se respondió                            |
| respuesta          | TEXT         | NOT NULL      | Respuesta del paciente                               |
| fecha_registro     | TIMESTAMP    | DEFAULT NOW   | Fecha y hora de creación de la nota                  |

**Relaciones:**
- **FK**: `id_paciente` → `paciente(id_paciente)`

**Índices:**
```sql
CREATE INDEX idx_notas_paciente ON notas(id_paciente);
CREATE INDEX idx_notas_fecha ON notas(fecha_registro);
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
  "sexo" CHAR (1),
  "direccion" VARCHAR(255),
  "telefono" VARCHAR(20),
  "correo" VARCHAR(50),
  "contacto_emergencia" VARCHAR(150),
  "telefono_emergencia" VARCHAR(20),
  "usuario" VARCHAR(50) UNIQUE,
  "password_hash" VARCHAR(255),
  "rol" VARCHAR(20) DEFAULT 'paciente',
  "ultimo_acceso" TIMESTAMP,
  "intentos_fallidos" INT DEFAULT 0,
  "bloqueado_hasta" TIMESTAMP,
  "fecha_registro" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "flg_activo" BOOLEAN DEFAULT true
);

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
  "usuario" VARCHAR(50) UNIQUE,
  "password_hash" VARCHAR(255),
  "rol" VARCHAR(20) DEFAULT 'especialista',
  "ultimo_acceso" TIMESTAMP,
  "intentos_fallidos" INT DEFAULT 0,
  "bloqueado_hasta" TIMESTAMP,
  "flg_activo" BOOLEAN DEFAULT true
);

CREATE TABLE "historia_clinica" (
  "id_historia" BIGSERIAL PRIMARY KEY,
  "id_paciente" BIGINT,
  "fecha_apertura" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "especialista_apertura" BIGINT,
  "servicio_origen" VARCHAR(100),
  "antecedentes_personales" TEXT,
  "antecedentes_familiares" TEXT,
  "antecedentes_psicosociales" TEXT,
  "habitos_personales" TEXT,
  "situacion_familiar" TEXT,
  "situacion_laboral" TEXT,
  "evaluacion_inicial" TEXT,
  "diagnostico_inicial" TEXT,
  "tratamientos_previos" TEXT,
  "situacion_historia" VARCHAR(20) DEFAULT 'abierta',
  "fecha_actualizacion" TIMESTAMP,
  "especialista_actualizacion" BIGINT,
  "fecha_cierre" TIMESTAMP,
  "motivo_cierre" TEXT
);

CREATE TABLE "paciente_medicacion" (
  "id_medicacion_paciente" SERIAL PRIMARY KEY,
  "id_historia" INT NOT NULL,
  "medicacion" VARCHAR(150) NOT NULL,
  "concentracion" VARCHAR(50),
  "forma_farmaceutica" VARCHAR(50),
  "dosis" VARCHAR(50),
  "frecuencia" VARCHAR(50),
  "anio_inicio" INT,
  "tipo_medicacion" VARCHAR(50),
  "prescrito_por" VARCHAR(100),
  "observaciones" TEXT,
  "fecha_registro" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE "notas" (
  "id_nota" BIGSERIAL PRIMARY KEY,
  "id_paciente" BIGINT NOT NULL,
  "pregunta" VARCHAR(255) NOT NULL,
  "respuesta" TEXT NOT NULL,
  "fecha_registro" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

-- Foreign Key historia_clinica
ALTER TABLE "historia_clinica"
  ADD CONSTRAINT "fk_historia_paciente"
  FOREIGN KEY ("id_paciente")
  REFERENCES "paciente" ("id_paciente");

ALTER TABLE "historia_clinica"
  ADD CONSTRAINT "fk_historia_especialista_apertura"
  FOREIGN KEY ("especialista_apertura")
  REFERENCES "especialista" ("id_especialista");

ALTER TABLE "historia_clinica"
  ADD CONSTRAINT "fk_historia_especialista_actualizacion"
  FOREIGN KEY ("especialista_actualizacion")
  REFERENCES "especialista" ("id_especialista");

-- Foreign Key paciente_medicacion
ALTER TABLE "paciente_medicacion"
  ADD CONSTRAINT "fk_medicacion_historia"
  FOREIGN KEY ("id_historia")
  REFERENCES "historia_clinica" ("id_historia");

-- Foreign Key notas
ALTER TABLE "notas"
  ADD CONSTRAINT "fk_notas_paciente"
  FOREIGN KEY ("id_paciente")
  REFERENCES "paciente" ("id_paciente");

-- Índices paciente
CREATE INDEX idx_paciente_dni ON paciente(dni);
CREATE INDEX idx_paciente_activo ON paciente(flg_activo);
CREATE UNIQUE INDEX idx_paciente_usuario ON paciente(usuario);
CREATE INDEX idx_paciente_rol ON paciente(rol);

-- Índices especialista
CREATE INDEX idx_especialista_dni ON especialista(dni);
CREATE INDEX idx_especialista_activo ON especialista(flg_activo);
CREATE UNIQUE INDEX idx_especialista_usuario ON especialista(usuario);
CREATE INDEX idx_especialista_rol ON especialista(rol);

-- Índices historia_clinica
CREATE INDEX idx_historia_paciente ON historia_clinica(id_paciente);

-- Índices paciente_medicacion
CREATE INDEX idx_medicacion_historia ON paciente_medicacion (id_historia);

-- Índices notas
CREATE INDEX idx_notas_paciente ON notas(id_paciente);
CREATE INDEX idx_notas_fecha ON notas(fecha_registro);
```

## Sistema de Autenticación y Roles

### Roles disponibles:
- **admin**: Acceso total al sistema, gestión de usuarios y configuración (especialista)
- **especialista**: Acceso a sus pacientes asignados, creación de historias clínicas (especialista)
- **paciente**: Acceso limitado a su propia información, historial y predicciones (paciente)

### Campos de autenticación:

**En tabla especialista:**
- `usuario`: Nombre único para login (ej: "mgonzalez")
- `password_hash`: Hash bcrypt de la contraseña (nunca almacenar en texto plano)
- `rol`: Define nivel de acceso - valores: 'admin', 'especialista'
- `ultimo_acceso`: Auditoría de sesiones
- `intentos_fallidos`: Seguridad contra fuerza bruta
- `bloqueado_hasta`: Bloqueo temporal tras múltiples intentos fallidos

**En tabla paciente:**
- `usuario`: Nombre único para login (ej: "jperez")
- `password_hash`: Hash bcrypt de la contraseña
- `rol`: Siempre 'paciente' (valor fijo)
- `ultimo_acceso`: Auditoría de sesiones
- `intentos_fallidos`: Seguridad contra fuerza bruta
- `bloqueado_hasta`: Bloqueo temporal tras múltiples intentos fallidos

### Flujo de autenticación unificado:
1. Usuario ingresa credenciales (usuario + contraseña)
2. Sistema busca usuario en **ambas tablas** (especialista y paciente)
3. Valida contraseña usando bcrypt.compare()
4. Verifica que cuenta esté activa (flg_activo = true)
5. Verifica que no esté bloqueada (bloqueado_hasta)
6. Actualiza ultimo_acceso y resetea intentos_fallidos
7. Crea sesión con datos del usuario, rol, y tipo (especialista/paciente)

### Diferenciación de acceso por rol:
- **Especialistas (admin/especialista)**: Acceso al panel de administración, gestión de pacientes, historias clínicas
- **Pacientes**: Acceso solo a:
  - Su propia historia clínica (solo lectura)
  - Sus propias sesiones y notas
  - Resultados de predicciones de ML sobre sus notas
  - Actualización de sus datos personales (dirección, teléfono, contacto de emergencia)

### Políticas de seguridad:
- Bloquear cuenta por 15 minutos tras 5 intentos fallidos de login
- Expirar sesiones después de 30 minutos de inactividad
- Requerir contraseñas con mínimo 8 caracteres, mayúsculas, minúsculas y números
- Los pacientes NO pueden ver información de otros pacientes
- Los pacientes NO pueden crear o editar historias clínicas
- Los especialistas solo pueden ver pacientes asignados a ellos (a menos que sean admin)

## Consideraciones de Seguridad

1. **Datos Sensibles**:
   - Todos los datos de pacientes son información de salud protegida
   - Cumplir con Ley de Protección de Datos Personales del Perú
   - NUNCA almacenar contraseñas en texto plano

2. **Encriptación**:
   - Datos en tránsito: HTTPS/TLS
   - Datos en reposo: Encriptar campos sensibles
   - Contraseñas: bcrypt con factor de costo 10 o superior

3. **Auditoría**:
   - Registrar todos los inicios de sesión (exitosos y fallidos)
   - Auditar acceso a historias clínicas
   - Implementar tabla de logs de acceso

4. **Backups**:
   - Backups automáticos diarios
   - Encriptación de backups
   - Pruebas de restauración

5. **Control de Acceso**:
   - RBAC (Role-Based Access Control)
   - Especialistas solo ven sus pacientes asignados
   - Administradores tienen acceso completo
   - Validar permisos en cada endpoint de la API

## Valores de Ejemplo

### Datos de prueba para desarrollo

```sql
INSERT INTO especialista (dni, nombres, apellidos, especialidad, colegiatura, correo, telefono, cargo, usuario, password_hash, rol)
VALUES
('12345678', 'María', 'González Pérez', 'Psicóloga Clínica', 'CPsP12345', 'mgonzalez@centro.com', '987654321', 'Psicóloga Senior', 'mgonzalez', '$2a$10$JesoGqxHvlJ3/F/5NzF.H.TDUl7xT.At0qqNKoL4L1TCCLgkO1i8u', 'admin'),
('23456789', 'Carlos', 'Ramírez Torres', 'Psiquiatra', 'CMP23456', 'cramirez@centro.com', '987654322', 'Psiquiatra', 'cramirez', '$2a$10$7H9dY06fzkEAbeffjDMj1O3NeeB7.XWufcSInLeIEAap0cWHAfZoG', 'especialista');

/*
$2b$10$rZ9pJKxL8YQ4K5J9m8X9Ye9vT8K9m8X9Ye9vT8K9m8X9Ye9vT8K9m
*/
/*
Credenciales de acceso para pruebas (ESPECIALISTAS):
- Usuario: mgonzalez | Contraseña: Admin123! | Rol: admin
- Usuario: cramirez  | Contraseña: Pass123!  | Rol: especialista

Credenciales de acceso para pruebas (PACIENTES):
- Usuario: jperez    | Contraseña: Pass1234! | Rol: paciente
- Usuario: atorres   | Contraseña: Pass123! | Rol: paciente
- Usuario: lmartinez | Contraseña: Pass123! | Rol: paciente

Nota: Los password_hash son ejemplos ficticios. En producción, generar hashes reales usando bcrypt.
Para generar un hash real en Node.js:
  const bcrypt = require('bcrypt');
  const hash = await bcrypt.hash('tuContraseña', 10);
*/

INSERT INTO paciente (dni, nombres, apellidos, fecha_nacimiento, sexo, direccion, telefono, correo, contacto_emergencia, telefono_emergencia, usuario, password_hash, rol)
VALUES
('87654321', 'Juan', 'Pérez López', '1990-05-15', 'M', 'Av. Principal 123', '912345678', 'jperez@email.com', 'María Pérez', '923456789', 'jperez', '$2b$10$bPPc3azVhcS/usAw7W0BC.TWgLxIfkm2Txmx3ZXvyfT43lNvxOQVi', 'paciente'),
('98765432', 'Ana', 'Torres Mendoza', '1985-08-20', 'F', 'Jr. Los Olivos 456', '923456789', 'atorres@email.com', 'Pedro Torres', '934567890', 'atorres', '$2a$10$7H9dY06fzkEAbeffjDMj1O3NeeB7.XWufcSInLeIEAap0cWHAfZoG', 'paciente'),
('45678912', 'Luis', 'Martínez Silva', '1992-03-10', 'M', 'Calle Las Flores 789', '934567891', 'lmartinez@email.com', 'Rosa Martínez', '945678901', 'lmartinez', '$2a$10$7H9dY06fzkEAbeffjDMj1O3NeeB7.XWufcSInLeIEAap0cWHAfZoG', 'paciente');

INSERT INTO historia_clinica (
    id_paciente,
    especialista_apertura,
    servicio_origen,
    antecedentes_personales,
    antecedentes_familiares,
    antecedentes_psicosociales,
    habitos_personales,
    situacion_familiar,
    situacion_laboral,
    evaluacion_inicial,
    diagnostico_inicial,
    tratamientos_previos,
    situacion_historia
)
VALUES
(
    1,
    1,
    'Consulta Externa',
    'Sin antecedentes médicos relevantes. No hospitalizaciones previas.',
    '{"depresion": false, "ansiedad": true, "bipolaridad": false, "esquizofrenia": false, "tdah": false, "toc": false, "adicciones": false, "suicidio": false, "otros": "Madre con trastorno de ansiedad generalizada diagnosticado hace 10 años"}',
    'Nivel socioeconómico medio. Educación universitaria completa. Red de apoyo familiar presente.',
    '{"alcohol": "Ocasional", "alcohol_frecuencia": "1-2 veces/mes", "tabaco": "No", "tabaco_frecuencia": "", "drogas": "No", "drogas_frecuencia": "", "sueño_horas": "6-7h", "sueño_calidad": "Regular", "alimentacion": "Adecuada", "ejercicio": "2-3 veces/semana", "otros": ""}',
    'Vive con pareja e hijo de 5 años. Relación familiar estable con comunicación fluida.',
    'Empleado a tiempo completo en empresa privada. Estrés laboral moderado por alta carga de trabajo.',
    'Paciente refiere episodios de ansiedad recurrentes desde hace 3 meses, principalmente en contexto laboral. Presenta preocupación excesiva, tensión muscular y dificultad para concentrarse. No síntomas depresivos asociados.',
    'Impresión diagnóstica: Trastorno de Ansiedad Generalizada (F41.1)',
    'Ninguno',
    'abierta'
),
(
    2,
    2,
    'Emergencia',
    'Diabetes tipo 2 diagnosticada hace 2 años, en tratamiento con metformina. Sin otras enfermedades crónicas.',
    '{"depresion": true, "ansiedad": false, "bipolaridad": true, "esquizofrenia": false, "tdah": false, "toc": false, "adicciones": true, "suicidio": false, "otros": "Padre con depresión mayor. Abuela materna con trastorno bipolar. Tío paterno con problemas de alcoholismo"}',
    'Nivel socioeconómico bajo. Educación secundaria completa. Vive en zona urbano-marginal. Escaso acceso a servicios de salud.',
    '{"alcohol": "No", "alcohol_frecuencia": "", "tabaco": "Sí", "tabaco_frecuencia": "5 cigarrillos/día", "drogas": "No", "drogas_frecuencia": "", "sueño_horas": "4-5h", "sueño_calidad": "Mala", "alimentacion": "Regular", "ejercicio": "No realiza", "otros": "Refiere insomnio de conciliación frecuente"}',
    'Vive sola con dos hijos menores (8 y 5 años). Separada hace 1 año. Escaso apoyo familiar. Conflictos con ex pareja por pensión alimenticia.',
    'Desempleada actualmente. Situación económica precaria. Busca trabajo activamente sin éxito. Dependencia económica de familiares.',
    'Paciente presenta estado de ánimo deprimido persistente por más de 6 meses, pérdida de interés en actividades previamente disfrutadas, alteración del sueño con insomnio, fatiga constante, sentimientos de culpa y pensamientos de desesperanza. No ideación suicida actual pero sí pensamientos pasivos de muerte. Llanto fácil. Aislamiento social progresivo.',
    'Impresión diagnóstica: Episodio Depresivo Mayor Moderado (F32.1)',
    'Tratamiento previo con sertralina 50mg por 3 meses hace 1 año, suspendido por iniciativa propia debido a efectos secundarios (náuseas).',
    'abierta'
),
(
    3,
    1,
    'Consulta Externa',
    'Alergia a penicilina. Gastritis crónica en tratamiento. Sin antecedentes psiquiátricos previos.',
    '{"depresion": false, "ansiedad": false, "bipolaridad": false, "esquizofrenia": false, "tdah": true, "toc": false, "adicciones": false, "suicidio": false, "otros": "Hermano menor diagnosticado con TDAH en la infancia"}',
    'Nivel socioeconómico medio-alto. Profesional independiente. Red social amplia. Buen soporte familiar.',
    '{"alcohol": "Frecuente", "alcohol_frecuencia": "3-4 veces/semana", "tabaco": "No", "tabaco_frecuencia": "", "drogas": "Ocasional", "drogas_frecuencia": "Marihuana 1-2 veces/mes", "sueño_horas": "7-8h", "sueño_calidad": "Buena", "alimentacion": "Buena", "ejercicio": "4-5 veces/semana", "otros": "Practica yoga y meditación regularmente"}',
    'Soltero, vive solo. Relación cercana con familia de origen. Sin hijos.',
    'Profesional independiente en diseño gráfico. Ingresos variables pero estables. Satisfecho con su trabajo pero con periodos de alta demanda estresantes.',
    'Paciente consulta por dificultades de concentración, inquietud constante y procrastinación que afectan su desempeño laboral. Refiere que estos síntomas han estado presentes desde la adolescencia pero se han intensificado en el último año. Dificultad para organizar tareas y cumplir plazos. Olvidos frecuentes.',
    'Impresión diagnóstica a descartar: Trastorno por Déficit de Atención e Hiperactividad del Adulto (F90.0)',
    'Ninguno',
    'abierta'
);

INSERT INTO paciente_medicacion (
    id_historia,
    medicacion,
    concentracion,
    forma_farmaceutica,
    dosis,
    frecuencia,
    anio_inicio,
    tipo_medicacion,
    prescrito_por,
    observaciones
)
VALUES
(
    2,
    'Metformina',
    '850 mg',
    'Tableta',
    '1 tableta',
    'Cada 12 horas con alimentos',
    2022,
    'Crónica',
    'Dr. Luis Martínez - Endocrinólogo',
    'Para control de diabetes tipo 2. Paciente refiere buena adherencia al tratamiento. Última HbA1c: 6.8%'
),
(
    2,
    'Ácido Fólico',
    '5 mg',
    'Tableta',
    '1 tableta',
    '1 vez al día',
    2023,
    'Suplemento',
    'Dra. Carmen López - Medicina General',
    'Suplementación por anemia leve detectada hace 1 año. Hemoglobina actual: 11.5 g/dL'
),
(
    3,
    'Omeprazol',
    '20 mg',
    'Cápsula',
    '1 cápsula',
    '1 vez al día en ayunas',
    2021,
    'Crónica',
    'Dr. Roberto Sánchez - Gastroenterólogo',
    'Tratamiento para gastritis crónica. Paciente refiere mejoría de síntomas con el tratamiento.'
);
```

## Migración de Datos

Si necesitas migrar datos existentes o cambiar el esquema, documentar todas las migraciones en:
- `frontend/src/lib/server/db/migrations/`

## Notas Técnicas

- **Motor**: PostgreSQL (recomendado para producción)
- **Encoding**: UTF-8
- **Timezone**: UTC para todos los timestamps
- **Naming Convention**: snake_case para nombres de tablas y columnas
