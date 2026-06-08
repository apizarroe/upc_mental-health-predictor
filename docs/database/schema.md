# Esquema de Base de Datos

Este documento describe el esquema de la base de datos para el sistema de predicción de trastornos mentales.

## Tablas

### paciente

Información de los pacientes del centro de atención psicológica.

| Campo               | Tipo         | Restricciones | Descripción                                  |
| ------------------- | ------------ | ------------- | -------------------------------------------- |
| id_paciente         | BIGSERIAL    | PRIMARY KEY   | Identificador único del paciente             |
| dni                 | VARCHAR(12)  |               | DNI o documento de identidad                 |
| nombres             | VARCHAR(80)  |               | Nombres del paciente                         |
| apellidos           | VARCHAR(80)  |               | Apellidos del paciente                       |
| fecha_nacimiento    | DATE         |               | Fecha de nacimiento                          |
| sexo                | CHAR(1)      |               | Sexo: 'M' o 'F'                              |
| direccion           | VARCHAR(255) |               | Dirección de residencia                      |
| telefono            | VARCHAR(20)  |               | Teléfono de contacto                         |
| correo              | VARCHAR(50)  |               | Email del paciente                           |
| contacto_emergencia | VARCHAR(150) |               | Nombre de contacto de emergencia             |
| telefono_emergencia | VARCHAR(20)  |               | Teléfono de emergencia                       |
| password_hash       | VARCHAR(255) |               | Contraseña hasheada para acceso del paciente |
| ultimo_acceso       | TIMESTAMP    |               | Fecha y hora del último inicio de sesión     |
| intentos_fallidos   | INT          | DEFAULT 0     | Contador de intentos fallidos de login       |
| bloqueado_hasta     | TIMESTAMP    |               | Fecha hasta la cual está bloqueada la cuenta |
| fecha_registro      | TIMESTAMP    | DEFAULT NOW   | Fecha de registro en el sistema              |
| flg_activo          | BOOLEAN      | DEFAULT true  | Estado activo/inactivo del paciente          |
| estado_clinico      | VARCHAR(50)  |               | Estado clínico actual del paciente           |
| fecha_ultima_consulta | DATE       |               | Fecha de la última consulta registrada       |

**Índices:**

```sql
CREATE INDEX idx_paciente_dni ON paciente(dni); -- Crítico: usado en login (WHERE dni = ?)
CREATE INDEX idx_paciente_activo ON paciente(flg_activo); -- Usado en filtros
```

### especialista

Profesionales de salud mental del centro con credenciales de acceso al sistema.

| Campo             | Tipo         | Restricciones          | Descripción                                  |
| ----------------- | ------------ | ---------------------- | -------------------------------------------- |
| id_especialista   | BIGSERIAL    | PRIMARY KEY            | Identificador único del especialista         |
| dni               | VARCHAR(12)  |                        | DNI del especialista                         |
| nombres           | VARCHAR(80)  |                        | Nombres del especialista                     |
| apellidos         | VARCHAR(80)  |                        | Apellidos del especialista                   |
| especialidad      | VARCHAR(50)  |                        | Especialidad: 'Psicólogo', 'Psiquiatra', etc |
| colegiatura       | VARCHAR(20)  |                        | Número de colegiatura (CMP, CPsP)            |
| correo            | VARCHAR(50)  |                        | Email profesional                            |
| telefono          | VARCHAR(20)  |                        | Teléfono de contacto                         |
| cargo             | VARCHAR(50)  |                        | Cargo en el centro                           |
| usuario           | VARCHAR(50)  | UNIQUE                 | Nombre de usuario para login (único)         |
| password_hash     | VARCHAR(255) |                        | Contraseña hasheada (bcrypt)                 |
| rol               | VARCHAR(20)  | DEFAULT 'especialista' | Rol: 'admin', 'especialista', 'coordinador'  |
| ultimo_acceso     | TIMESTAMP    |                        | Fecha y hora del último inicio de sesión     |
| intentos_fallidos | INT          | DEFAULT 0              | Contador de intentos fallidos de login       |
| bloqueado_hasta   | TIMESTAMP    |                        | Fecha hasta la cual está bloqueada la cuenta |
| flg_activo        | BOOLEAN      | DEFAULT true           | Estado activo/inactivo del especialista      |

**Índices:**

```sql
CREATE UNIQUE INDEX idx_especialista_usuario ON especialista(usuario); -- Crítico: login (WHERE usuario = ?)
CREATE INDEX idx_especialista_activo ON especialista(flg_activo); -- Usado en filtros
CREATE INDEX idx_especialista_rol ON especialista(rol); -- Control de acceso por rol
```

### historia_clinica

Historia clínica de cada paciente con información detallada de antecedentes médicos, psicológicos, familiares y situación actual del paciente al momento de apertura de la historia.

| Campo                      | Tipo         | Restricciones     | Descripción                                                                                                                                                            |
| -------------------------- | ------------ | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id_historia                | BIGSERIAL    | PRIMARY KEY       | Identificador único de la historia clínica                                                                                                                             |
| id_paciente                | BIGINT       | FOREIGN KEY       | Referencia a paciente(id_paciente)                                                                                                                                     |
| fecha_apertura             | TIMESTAMP    | DEFAULT NOW       | Fecha y hora de apertura de la historia                                                                                                                                |
| especialista_apertura      | BIGINT       | FOREIGN KEY       | ID del especialista que abrió la historia                                                                                                                              |
| servicio_origen            | VARCHAR(100) |                   | Servicio o área de origen del paciente                                                                                                                                 |
| antecedentes_personales    | TEXT         |                   | Antecedentes médicos y psicológicos personales                                                                                                                         |
| antecedentes_familiares    | JSONB        |                   | Antecedentes familiares en formato JSON: depresion, ansiedad, bipolaridad, esquizofrenia, tdah, toc, adicciones, suicidio, otros (booleanos)                           |
| antecedentes_psicosociales | TEXT         |                   | Contexto psicosocial del paciente                                                                                                                                      |
| habitos_personales         | JSONB        |                   | Hábitos en formato JSON: alcohol, alcohol_frecuencia, tabaco, tabaco_frecuencia, drogas, drogas_frecuencia, sueño_horas, sueño_calidad, alimentacion, ejercicio, otros |
| situacion_familiar         | TEXT         |                   | Descripción de la dinámica familiar actual                                                                                                                             |
| situacion_laboral          | TEXT         |                   | Situación laboral y ocupacional actual                                                                                                                                 |
| evaluacion_inicial         | TEXT         |                   | Evaluación psicológica inicial                                                                                                                                         |
| diagnostico_inicial        | TEXT         |                   | Diagnóstico o impresión diagnóstica inicial                                                                                                                            |
| tratamientos_previos       | TEXT         |                   | Tratamientos psicológicos previos recibidos                                                                                                                            |
| situacion_historia         | VARCHAR(30)  | DEFAULT 'Abierta' | Estado: 'Abierta', 'Cerrada', 'En revisión'                                                                                                                            |
| fecha_actualizacion        | TIMESTAMP    |                   | Última fecha de actualización de la historia                                                                                                                           |
| especialista_actualizacion | BIGINT       | FOREIGN KEY       | ID del último especialista que actualizó                                                                                                                               |
| fecha_cierre               | TIMESTAMP    |                   | Fecha de cierre de la historia                                                                                                                                         |
| motivo_cierre              | TEXT         |                   | Motivo o razón del cierre de la historia                                                                                                                               |

**Relaciones:**

- **FK**: `id_paciente` → `paciente(id_paciente)` (usado en LEFT JOIN y WHERE)
- **FK**: `especialista_apertura` → `especialista(id_especialista)` (usado en LEFT JOIN)
- **FK**: `especialista_actualizacion` → `especialista(id_especialista)` (referencia opcional)

**Índices:**

```sql
CREATE INDEX idx_historia_id_paciente ON historia_clinica(id_paciente); -- Crítico: FK usado en WHERE y JOIN
CREATE INDEX idx_historia_especialista_apertura ON historia_clinica(especialista_apertura); -- FK usado en JOIN
CREATE INDEX idx_historia_fecha_apertura ON historia_clinica(fecha_apertura DESC); -- ORDER BY DESC
CREATE INDEX idx_historia_situacion ON historia_clinica(situacion_historia); -- Filtros por estado
```

### paciente_medicacion

Registro de medicaciones que el paciente ya tomaba al momento de la apertura de la historia clínica (medicamentos por preexistencias o condiciones previas).

| Campo                  | Tipo         | Restricciones         | Descripción                                             |
| ---------------------- | ------------ | --------------------- | ------------------------------------------------------- |
| id_medicacion_paciente | SERIAL       | PRIMARY KEY           | Identificador único del registro de medicación          |
| id_historia            | INT          | FOREIGN KEY, NOT NULL | Referencia a historia_clinica(id_historia)              |
| medicacion             | VARCHAR(150) | NOT NULL              | Nombre del medicamento                                  |
| concentracion          | VARCHAR(50)  |                       | Concentración (ej: "50 mg", "10 mg/ml")                 |
| forma_farmaceutica     | VARCHAR(50)  |                       | Forma farmacéutica (Tableta, Cápsula, Jarabe, etc.)     |
| dosis                  | VARCHAR(50)  |                       | Dosis administrada (ej: "1 tableta", "5 ml")            |
| frecuencia             | VARCHAR(50)  |                       | Frecuencia de administración (ej: "Cada 8 horas")       |
| anio_inicio            | INT          |                       | Año de inicio del tratamiento                           |
| tipo_medicacion        | VARCHAR(50)  |                       | Tipo (ej: "Crónica", "Psicotrópico", "Antidepresivo")   |
| prescrito_por          | VARCHAR(100) |                       | Nombre del médico o centro que prescribió               |
| observaciones          | TEXT         |                       | Comentarios o detalles adicionales sobre el medicamento |
| fecha_registro         | TIMESTAMP    | DEFAULT NOW           | Fecha de registro en el sistema                         |

**Relaciones:**

- **FK**: `id_historia` → `historia_clinica(id_historia)` (usado en WHERE)

**Índices:**

```sql
CREATE INDEX idx_medicacion_historia ON paciente_medicacion(id_historia); -- FK usado en WHERE
CREATE INDEX idx_medicacion_fecha ON paciente_medicacion(fecha_registro DESC); -- ORDER BY DESC
```

### paciente_respuesta

Registro de respuestas diarias del paciente al cuestionario de seguimiento. Cada registro representa una sesión de respuesta que será procesada por el modelo de ML.

| Campo                | Tipo        | Restricciones                 | Descripción                                                                                                  |
| -------------------- | ----------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------ |
| id_respuesta         | BIGSERIAL   | PRIMARY KEY                   | Identificador único de la respuesta                                                                          |
| id_paciente          | BIGINT      | FOREIGN KEY, NOT NULL         | Referencia a paciente(id_paciente)                                                                           |
| fecha_respuesta      | TIMESTAMP   | DEFAULT NOW, NOT NULL         | Fecha y hora de la respuesta                                                                                 |
| respuestas           | JSONB       | NOT NULL                      | Respuestas del cuestionario en formato JSON                                                                  |
| estado_procesamiento | VARCHAR(20) | DEFAULT 'pendiente', NOT NULL | Estado: 'pendiente', 'procesado', 'error'                                                                    |
| id_evaluacion        | BIGINT      | FOREIGN KEY                   | Referencia a evaluacion_ml(id_evaluacion)                                                                    |
| error_mensaje        | TEXT        |                               | Mensaje de error si el procesamiento falló                                                                   |
| riesgo_atendido      | BOOLEAN     |                               | Marca si el especialista tomó acción ante señales de riesgo detectadas en la nota. Nace en NULL y solo puede pasar a TRUE (no existe estado FALSE) |

**Relaciones:**

- **FK**: `id_paciente` → `paciente(id_paciente)` (usado en WHERE, COUNT y LEFT JOIN)
- **FK**: `id_evaluacion` → `evaluacion_ml(id_evaluacion)` (usado en LEFT JOIN)

**Índices:**

```sql
-- Índice compuesto crítico para búsquedas por paciente con ordenamiento por fecha
CREATE INDEX idx_respuesta_paciente_fecha ON paciente_respuesta(id_paciente, fecha_respuesta DESC);

-- Índice para JOIN con evaluacion_ml
CREATE INDEX idx_respuesta_evaluacion ON paciente_respuesta(id_evaluacion);

-- Índice para filtros por estado (opcional)
CREATE INDEX idx_respuesta_estado ON paciente_respuesta(estado_procesamiento);
```

### observacion

Observaciones registradas por el especialista sobre una respuesta diaria del paciente.

| Campo             | Tipo      | Restricciones         | Descripción                                   |
| ----------------- | --------- | --------------------- | --------------------------------------------- |
| id_observacion    | BIGSERIAL | PRIMARY KEY           | Identificador único de la observación         |
| id_respuesta      | BIGINT    | FOREIGN KEY, NOT NULL | Referencia a paciente_respuesta(id_respuesta) |
| descripcion       | TEXT      | NOT NULL              | Contenido de la observación                   |
| id_especialista   | BIGINT    | FOREIGN KEY           | Especialista que registró la observación      |
| fecha_observacion | TIMESTAMP |                       | Fecha y hora del registro (zona Lima GMT-5)   |

**Relaciones:**

- **FK**: `id_respuesta` → `paciente_respuesta(id_respuesta)` (usado en WHERE e INSERT)
- **FK**: `id_especialista` → `especialista(id_especialista)` (usado en LEFT JOIN)

**Índices:**

```sql
CREATE INDEX idx_observacion_respuesta ON observacion(id_respuesta);
```

### atencion

Registro de atenciones clínicas realizadas por el especialista en el contexto de una historia clínica. Permite documentar cada consulta con observaciones y recomendaciones en texto libre.

| Campo           | Tipo        | Restricciones         | Descripción                                                              |
| --------------- | ----------- | --------------------- | ------------------------------------------------------------------------ |
| id_atencion     | SERIAL      | PRIMARY KEY           | Identificador único de la atención                                       |
| id_historia     | INTEGER     | FOREIGN KEY, NOT NULL | Referencia a historia_clinica(id_historia)                               |
| id_especialista | INTEGER     | FOREIGN KEY, NOT NULL | Especialista que registra la atención                                    |
| fecha_atencion  | TIMESTAMP   | NOT NULL, DEFAULT NOW | Fecha y hora de la atención (zona Lima GMT-5)                            |
| tipo_atencion   | VARCHAR(20) | NOT NULL, CHECK       | Tipo: 'Presencial', 'Virtual', 'Telefónica'                              |
| observaciones   | TEXT        |                       | Observaciones clínicas en texto libre                                    |
| recomendaciones | TEXT        |                       | Recomendaciones para el paciente en texto libre                          |

**Relaciones:**

- **FK**: `id_historia` → `historia_clinica(id_historia)`
- **FK**: `id_especialista` → `especialista(id_especialista)`

**Constraints:**

```sql
CHECK (tipo_atencion IN ('Presencial', 'Virtual', 'Telefónica'))
```

**Nota:** Solo el especialista autor puede editar su propia atención (`id_especialista` se toma automáticamente de la sesión activa).

---

### evaluacion_ml

Almacena los resultados de la evaluación de Machine Learning sobre las respuestas del paciente. Contiene las predicciones del modelo sobre trastornos mentales detectados.

| Campo                  | Tipo         | Restricciones         | Descripción                                              |
| ---------------------- | ------------ | --------------------- | -------------------------------------------------------- |
| id_evaluacion          | BIGSERIAL    | PRIMARY KEY           | Identificador único de la evaluación                     |
| id_respuesta           | BIGINT       | FOREIGN KEY, NOT NULL | Referencia a paciente_respuesta(id_respuesta)            |
| fecha_evaluacion       | TIMESTAMP    | DEFAULT NOW, NOT NULL | Fecha y hora de la evaluación                            |
| modelo_nombre          | VARCHAR(100) | NOT NULL              | Nombre del modelo utilizado                              |
| modelo_tipo            | VARCHAR(20)  | NOT NULL              | Tipo de modelo (ej: 'multilabel_classifier')             |
| modelo_version         | VARCHAR(50)  |                       | Versión del modelo BERT utilizado                        |
| trastornos_detectados  | JSONB        | NOT NULL              | Trastornos detectados con probabilidades en formato JSON |
| condiciones_detectadas | TEXT[]       |                       | Array de nombres de condiciones detectadas               |
| nivel_riesgo_global    | VARCHAR(20)  |                       | Nivel de riesgo: 'bajo', 'moderado', 'alto'              |
| palabras_clave         | JSONB        |                       | Palabras clave identificadas en el texto                 |
| interpretacion         | TEXT         |                       | Interpretación generada por el modelo                    |
| metricas_modelo        | JSONB        |                       | Métricas de confianza del modelo                         |
| requiere_atencion      | BOOLEAN      | DEFAULT false         | Indicador de atención urgente requerida                  |
| notas_sistema          | TEXT         |                       | Notas adicionales del sistema                            |

**Relaciones:**

- **FK**: `id_respuesta` → `paciente_respuesta(id_respuesta)` (usado en INSERT)

**Índices:**

```sql
-- Índice crítico para JOIN desde paciente_respuesta
CREATE INDEX idx_evaluacion_respuesta ON evaluacion_ml(id_respuesta);
```

### evaluacion_validacion

Validación del especialista sobre los resultados de la evaluación de ML. Permite comparar las predicciones del modelo con el diagnóstico profesional para mejorar el sistema.

| Campo                    | Tipo        | Restricciones         | Descripción                                              |
| ------------------------ | ----------- | --------------------- | -------------------------------------------------------- |
| id_validacion            | BIGSERIAL   | PRIMARY KEY           | Identificador único de la validación                     |
| id_evaluacion            | BIGINT      | FOREIGN KEY, NOT NULL | Referencia a evaluacion_ml(id_evaluacion)                |
| id_especialista          | BIGINT      | FOREIGN KEY, NOT NULL | Especialista que realiza la validación                   |
| fecha_validacion         | TIMESTAMP   | DEFAULT NOW, NOT NULL | Fecha y hora de la validación                            |
| diagnostico_especialista | JSONB       | NOT NULL              | Diagnóstico del especialista en formato JSON             |
| coincidencias            | JSONB       |                       | Análisis de coincidencias entre ML y especialista        |
| precision_global         | VARCHAR(20) | NOT NULL              | Precisión: 'alta', 'media', 'baja'                       |
| falsos_positivos         | TEXT[]      |                       | Trastornos detectados por ML pero no por especialista    |
| falsos_negativos         | TEXT[]      |                       | Trastornos no detectados por ML pero sí por especialista |
| nivel_confianza          | INT         |                       | Nivel de confianza del especialista (0-100)              |
| observaciones            | TEXT        |                       | Observaciones del especialista                           |
| recomendacion_paciente   | TEXT        |                       | Recomendaciones para el tratamiento del paciente         |
| requiere_seguimiento     | BOOLEAN     | DEFAULT false         | Indicador de seguimiento requerido                       |
| util_para_entrenamiento  | BOOLEAN     | DEFAULT true          | Si la validación es útil para reentrenar el modelo       |

**Relaciones:**

- **FK**: `id_evaluacion` → `evaluacion_ml(id_evaluacion)`
- **FK**: `id_especialista` → `especialista(id_especialista)`

**Nota:** Esta tabla está definida en el esquema de base de datos pero **no se utiliza actualmente** en el código del frontend. Los índices se crearán cuando se implemente la funcionalidad de validación.

---

### reporte_indicadores_sistema

Almacena los snapshots históricos de los reportes de indicadores del sistema generados por un usuario administrador. Cada registro guarda el rango consultado, el solicitante y el snapshot completo en JSONB para que la exportación CSV se reconstruya sin recalcular métricas.

| Campo                       | Tipo        | Restricciones         | Descripción                                                              |
| --------------------------- | ----------- | --------------------- | ------------------------------------------------------------------------ |
| id_reporte                  | BIGSERIAL   | PRIMARY KEY           | Identificador único del reporte                                          |
| fecha_generacion            | TIMESTAMP   | DEFAULT NOW, NOT NULL | Fecha y hora de generación del snapshot                                  |
| id_especialista_solicitante | BIGINT      | FOREIGN KEY, NOT NULL | Administrador que solicitó la generación del reporte                     |
| fecha_inicio                | DATE        | NOT NULL              | Fecha inicial del rango consultado                                       |
| fecha_fin                   | DATE        | NOT NULL              | Fecha final del rango consultado                                         |
| indicadores_json            | JSONB       | NOT NULL              | Snapshot completo de indicadores, metadata y desglose del reporte        |
| formato_exportacion         | VARCHAR(20) | NOT NULL              | Formato principal de exportación. En v1 el valor esperado es `csv`       |

**Relaciones:**

- **FK**: `id_especialista_solicitante` → `especialista(id_especialista)`

**Índices:**

```sql
CREATE INDEX idx_reporte_indicadores_fecha_generacion
ON reporte_indicadores_sistema(fecha_generacion DESC);

CREATE INDEX idx_reporte_indicadores_solicitante
ON reporte_indicadores_sistema(id_especialista_solicitante);
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
  "password_hash" VARCHAR(255),
  "ultimo_acceso" TIMESTAMP,
  "intentos_fallidos" INT DEFAULT 0,
  "bloqueado_hasta" TIMESTAMP,
  "fecha_registro" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "flg_activo" BOOLEAN DEFAULT true,
  "estado_clinico" VARCHAR(50),
  "fecha_ultima_consulta" DATE
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
  "antecedentes_familiares" JSONB,
  "antecedentes_psicosociales" TEXT,
  "habitos_personales" JSONB,
  "situacion_familiar" TEXT,
  "situacion_laboral" TEXT,
  "evaluacion_inicial" TEXT,
  "diagnostico_inicial" TEXT,
  "tratamientos_previos" TEXT,
  "situacion_historia" VARCHAR(30) DEFAULT 'Abierta',
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

CREATE TABLE "paciente_respuesta" (
  "id_respuesta" BIGSERIAL PRIMARY KEY,
  "id_paciente" BIGINT NOT NULL,
  "fecha_respuesta" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
  "respuestas" JSONB NOT NULL,
  "estado_procesamiento" VARCHAR(20) DEFAULT 'pendiente' NOT NULL,
  "id_evaluacion" BIGINT,
  "error_mensaje" TEXT
);

CREATE TABLE "observacion" (
  "id_observacion" BIGSERIAL PRIMARY KEY,
  "id_respuesta" BIGINT NOT NULL,
  "descripcion" TEXT NOT NULL,
  "id_especialista" BIGINT,
  "fecha_observacion" TIMESTAMP
);

CREATE TABLE "atencion" (
  "id_atencion" SERIAL PRIMARY KEY,
  "id_historia" INTEGER NOT NULL,
  "id_especialista" INTEGER NOT NULL,
  "fecha_atencion" TIMESTAMP NOT NULL DEFAULT NOW(),
  "tipo_atencion" VARCHAR(20) NOT NULL CHECK (tipo_atencion IN ('Presencial', 'Virtual', 'Telefónica')),
  "observaciones" TEXT,
  "recomendaciones" TEXT
);

CREATE TABLE "evaluacion_ml" (
  "id_evaluacion" BIGSERIAL PRIMARY KEY,
  "id_respuesta" BIGINT NOT NULL,
  "fecha_evaluacion" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
  "modelo_nombre" VARCHAR(100) NOT NULL,
  "modelo_tipo" VARCHAR(50) NOT NULL,
  "modelo_version" VARCHAR(70),
  "trastornos_detectados" JSONB NOT NULL,
  "condiciones_detectadas" TEXT[],
  "nivel_riesgo_global" VARCHAR(20),
  "palabras_clave" JSONB,
  "interpretacion" TEXT,
  "metricas_modelo" JSONB,
  "requiere_atencion" BOOLEAN DEFAULT false,
  "notas_sistema" TEXT
);

CREATE TABLE "evaluacion_validacion" (
  "id_validacion" BIGSERIAL PRIMARY KEY,
  "id_evaluacion" BIGINT NOT NULL,
  "id_especialista" BIGINT NOT NULL,
  "fecha_validacion" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
  "diagnostico_especialista" JSONB NOT NULL,
  "coincidencias" JSONB,
  "precision_global" VARCHAR(20) NOT NULL,
  "falsos_positivos" TEXT[],
  "falsos_negativos" TEXT[],
  "nivel_confianza" INT,
  "observaciones" TEXT,
  "recomendacion_paciente" TEXT,
  "requiere_seguimiento" BOOLEAN DEFAULT false,
  "util_para_entrenamiento" BOOLEAN DEFAULT true
);

CREATE TABLE "reporte_indicadores_sistema" (
  "id_reporte" BIGSERIAL PRIMARY KEY,
  "fecha_generacion" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
  "id_especialista_solicitante" BIGINT NOT NULL,
  "fecha_inicio" DATE NOT NULL,
  "fecha_fin" DATE NOT NULL,
  "indicadores_json" JSONB NOT NULL,
  "formato_exportacion" VARCHAR(20) NOT NULL DEFAULT 'csv'
);

-- Foreign Keys para historia_clinica
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

-- Foreign Key para paciente_medicacion
ALTER TABLE "paciente_medicacion"
  ADD CONSTRAINT "fk_medicacion_historia"
  FOREIGN KEY ("id_historia")
  REFERENCES "historia_clinica" ("id_historia");

-- Foreign Keys para paciente_respuesta
ALTER TABLE "paciente_respuesta"
  ADD CONSTRAINT "fk_respuesta_paciente"
  FOREIGN KEY ("id_paciente")
  REFERENCES "paciente" ("id_paciente");

ALTER TABLE "paciente_respuesta"
  ADD CONSTRAINT "fk_respuesta_evaluacion"
  FOREIGN KEY ("id_evaluacion")
  REFERENCES "evaluacion_ml" ("id_evaluacion");

-- Foreign Keys para observacion
ALTER TABLE "observacion"
  ADD CONSTRAINT "fk_observacion_respuesta"
  FOREIGN KEY ("id_respuesta")
  REFERENCES "paciente_respuesta" ("id_respuesta");

ALTER TABLE "observacion"
  ADD CONSTRAINT "fk_observacion_especialista"
  FOREIGN KEY ("id_especialista")
  REFERENCES "especialista" ("id_especialista");

-- Foreign Keys para atencion
ALTER TABLE "atencion"
  ADD CONSTRAINT "fk_atencion_historia"
  FOREIGN KEY ("id_historia")
  REFERENCES "historia_clinica" ("id_historia");

ALTER TABLE "atencion"
  ADD CONSTRAINT "fk_atencion_especialista"
  FOREIGN KEY ("id_especialista")
  REFERENCES "especialista" ("id_especialista");

-- Foreign Key para evaluacion_ml
ALTER TABLE "evaluacion_ml"
  ADD CONSTRAINT "fk_evaluacion_respuesta"
  FOREIGN KEY ("id_respuesta")
  REFERENCES "paciente_respuesta" ("id_respuesta");

-- Foreign Key para reporte_indicadores_sistema
ALTER TABLE "reporte_indicadores_sistema"
  ADD CONSTRAINT "fk_reporte_indicadores_especialista"
  FOREIGN KEY ("id_especialista_solicitante")
  REFERENCES "especialista" ("id_especialista");

-- Índices para tabla paciente
CREATE INDEX idx_paciente_dni ON paciente(dni); -- Usado en login (WHERE dni = ?)
CREATE INDEX idx_paciente_activo ON paciente(flg_activo); -- Usado en filtros

-- Índices para tabla especialista
CREATE UNIQUE INDEX idx_especialista_usuario ON especialista(usuario); -- Crítico: login (WHERE usuario = ?)
CREATE INDEX idx_especialista_activo ON especialista(flg_activo); -- Usado en filtros
CREATE INDEX idx_especialista_rol ON especialista(rol); -- Control de acceso por rol

-- Índices para tabla historia_clinica
CREATE INDEX idx_historia_id_paciente ON historia_clinica(id_paciente); -- FK usado en WHERE y LEFT JOIN
CREATE INDEX idx_historia_especialista_apertura ON historia_clinica(especialista_apertura); -- FK usado en LEFT JOIN
CREATE INDEX idx_historia_fecha_apertura ON historia_clinica(fecha_apertura DESC); -- ORDER BY DESC
CREATE INDEX idx_historia_situacion ON historia_clinica(situacion_historia); -- Filtros por estado

-- Índices para tabla paciente_medicacion
CREATE INDEX idx_medicacion_historia ON paciente_medicacion(id_historia); -- FK usado en WHERE
CREATE INDEX idx_medicacion_fecha ON paciente_medicacion(fecha_registro DESC); -- ORDER BY DESC

-- Índices para tabla paciente_respuesta (críticos para rendimiento)
CREATE INDEX idx_respuesta_paciente_fecha ON paciente_respuesta(id_paciente, fecha_respuesta DESC); -- Índice compuesto
CREATE INDEX idx_respuesta_evaluacion ON paciente_respuesta(id_evaluacion); -- FK usado en LEFT JOIN
CREATE INDEX idx_respuesta_estado ON paciente_respuesta(estado_procesamiento); -- Filtros por estado

-- Índice para tabla observacion
CREATE INDEX idx_observacion_respuesta ON observacion(id_respuesta); -- FK usado en WHERE e INSERT

-- Índices para tabla evaluacion_ml
CREATE INDEX idx_evaluacion_respuesta ON evaluacion_ml(id_respuesta); -- FK usado en LEFT JOIN

-- Índices para tabla reporte_indicadores_sistema
CREATE INDEX idx_reporte_indicadores_fecha_generacion ON reporte_indicadores_sistema(fecha_generacion DESC); -- Historial ordenado por generación
CREATE INDEX idx_reporte_indicadores_solicitante ON reporte_indicadores_sistema(id_especialista_solicitante); -- JOIN con especialista y auditoría por solicitante
```

## Sistema de Autenticación y Roles

### Roles disponibles:

- **admin**: Acceso total al sistema, gestión de usuarios y configuración
- **coordinador**: Acceso a reportes, supervisión de casos, asignación de pacientes
- **especialista**: Acceso a sus pacientes asignados, creación de historias clínicas

### Campos de autenticación en tabla especialista:

- `usuario`: Nombre único para login (ej: "mgonzalez")
- `password_hash`: Hash bcrypt de la contraseña (nunca almacenar en texto plano)
- `rol`: Define nivel de acceso y permisos
- `ultimo_acceso`: Auditoría de sesiones
- `intentos_fallidos`: Seguridad contra fuerza bruta
- `bloqueado_hasta`: Bloqueo temporal tras múltiples intentos fallidos

### Campos de autenticación en tabla paciente:

- `dni`: Se usa como nombre de usuario para login
- `password_hash`: Hash bcrypt de la contraseña
- `ultimo_acceso`: Auditoría de sesiones
- `intentos_fallidos`: Seguridad contra fuerza bruta
- `bloqueado_hasta`: Bloqueo temporal tras múltiples intentos fallidos

### Flujo de autenticación:

1. Usuario ingresa credenciales (usuario/dni + contraseña)
2. Sistema busca usuario en tabla correspondiente (especialista o paciente)
3. Valida contraseña usando bcrypt.compare()
4. Verifica que cuenta esté activa (flg_activo = true)
5. Verifica que no esté bloqueada (bloqueado_hasta)
6. Actualiza ultimo_acceso y resetea intentos_fallidos
7. Crea sesión con datos del usuario

### Políticas de seguridad:

- Bloquear cuenta por 15 minutos tras 5 intentos fallidos de login
- Expirar sesiones después de 30 minutos de inactividad
- Requerir contraseñas con mínimo 8 caracteres, mayúsculas, minúsculas y números

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
Credenciales de acceso para pruebas:
- Usuario: mgonzalez | Contraseña: Admin123! | Rol: admin
- Usuario: cramirez  | Contraseña: Pass123!  | Rol: especialista

Nota: Los password_hash son ejemplos ficticios. En producción, generar hashes reales usando bcrypt.
Para generar un hash real en Node.js:
  const bcrypt = require('bcrypt');
  const hash = await bcrypt.hash('tuContraseña', 10);
*/

INSERT INTO paciente (dni, nombres, apellidos, fecha_nacimiento, sexo, direccion, telefono, correo, contacto_emergencia, telefono_emergencia, estado_clinico, fecha_ultima_consulta)
VALUES
('87654321', 'Juan', 'Pérez López', '1990-05-15', 'M', 'Av. Principal 123', '912345678', 'jperez@email.com', 'María Pérez', '923456789', 'En tratamiento', '2026-04-20'),
('98765432', 'Ana', 'Torres Mendoza', '1985-08-20', 'F', 'Jr. Los Olivos 456', '923456789', 'atorres@email.com', 'Pedro Torres', '934567890', 'Seguimiento', '2026-03-15'),
('45678912', 'Luis', 'Martínez Silva', '1992-03-10', 'M', 'Calle Las Flores 789', '934567891', 'lmartinez@email.com', 'Rosa Martínez', '945678901', 'Alta', '2026-02-10');

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
    'Abierta'
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
    'Abierta'
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
    'Abierta'
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

INSERT INTO atencion (id_historia, id_especialista, fecha_atencion, tipo_atencion, observaciones, recomendaciones)
VALUES
(
    1,
    1,
    NOW() AT TIME ZONE 'America/Lima',
    'Presencial',
    'Paciente muestra avances en el manejo de la ansiedad. Refiere menor frecuencia de episodios durante la semana. Mantiene técnicas de respiración aprendidas.',
    'Continuar con técnicas de relajación. Incrementar actividad física a 4 veces por semana. Próxima sesión en 2 semanas.'
),
(
    2,
    2,
    NOW() AT TIME ZONE 'America/Lima',
    'Virtual',
    'Paciente reporta leve mejoría en estado anímico. Duerme mejor con apoyo farmacológico. Aún presenta episodios de llanto espontáneo.',
    'Mantener dosis actual de medicación. Incorporar rutina de actividades placenteras diarias. Evaluar adherencia terapéutica en próxima consulta.'
);

INSERT INTO observacion (id_respuesta, descripcion, id_especialista, fecha_observacion)
VALUES
(
    1,
    'Paciente reporta mejoría en el manejo del estrés laboral. Se observa mayor autoconciencia emocional.',
    1,
    NOW() AT TIME ZONE 'America/Lima'
),
(
    1,
    'Se recomienda continuar con las técnicas de mindfulness trabajadas en sesión.',
    2,
    NOW() AT TIME ZONE 'America/Lima'
);
```

## Migración de Datos

Si necesitas migrar datos existentes o cambiar el esquema, documentar todas las migraciones en:

- `frontend/src/lib/server/db/migrations/`

## Notas Técnicas

- **Motor**: PostgreSQL 17.6 (recomendado para producción)
- **Encoding**: UTF-8
- **Timezone**: UTC para todos los timestamps (el frontend usa GMT-5 para Perú)
- **Naming Convention**: snake_case para nombres de tablas y columnas
- **JOINs**: Todas las relaciones usan LEFT JOIN en el código actual
- **JSONB**: Se usa para campos `antecedentes_familiares`, `habitos_personales`, `respuestas`, `trastornos_detectados`, `palabras_clave`, `metricas_modelo`
- **Arrays**: Se usa TEXT[] para `condiciones_detectadas`, `falsos_positivos`, `falsos_negativos`
