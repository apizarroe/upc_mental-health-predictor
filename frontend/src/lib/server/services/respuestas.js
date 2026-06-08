import sql from '../db/client.js';

/**
 * Verifica si el paciente ya completó el cuestionario 2 veces hoy (GMT-5 Lima/Peru)
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<boolean>} - true si ya completó 2 veces hoy, false si aún puede responder
 */
export async function yaRespondioDobleHoy(idPaciente) {
	// Obtener componentes de fecha en zona horaria Lima (GMT-5)
	const ahora = new Date();
	const partes = new Intl.DateTimeFormat('en-US', {
		timeZone: 'America/Lima',
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
		hour12: false
	}).formatToParts(ahora);

	const fecha = {};
	partes.forEach(({ type, value }) => {
		fecha[type] = value;
	});

	// Construir fecha en formato 'YYYY-MM-DD' para Lima
	const fechaHoy = `${fecha.year}-${fecha.month}-${fecha.day}`;

	const [result] = await sql`
		SELECT COUNT(*) as count
		FROM paciente_respuesta
		WHERE id_paciente = ${idPaciente}
		AND TO_CHAR(fecha_respuesta AT TIME ZONE 'America/Lima', 'YYYY-MM-DD') = ${fechaHoy}
	`;

	return parseInt(result.count) >= 2;
}

/**
 * Obtiene todas las respuestas de un paciente
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<Array>} - Array de respuestas
 */
export async function getRespuestasByPaciente(idPaciente) {
	const respuestas = await sql`
		SELECT
			pr.*,
			em.trastornos_detectados,
			em.condiciones_detectadas,
			em.nivel_riesgo_global,
			em.interpretacion,
			em.requiere_atencion
		FROM paciente_respuesta pr
		LEFT JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_paciente = ${idPaciente}
		ORDER BY pr.fecha_respuesta DESC
	`;
	return respuestas;
}

/**
 * Obtiene las respuestas del día actual (GMT-5 Lima/Peru)
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<Array>} - Array de respuestas del día
 */
export async function getRespuestasDelDia(idPaciente) {
	// IMPORTANTE: PostgreSQL guarda los timestamps en la zona horaria del servidor (GMT-5 Lima)
	// Por lo tanto, debemos comparar con fechas en la misma zona horaria

	// Obtener la fecha/hora actual en UTC
	const ahora = new Date();

	// Obtener componentes de fecha en zona horaria Lima (GMT-5)
	const partes = new Intl.DateTimeFormat('en-US', {
		timeZone: 'America/Lima',
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
		hour12: false
	}).formatToParts(ahora);

	// Extraer valores
	const fecha = {};
	partes.forEach(({ type, value }) => {
		fecha[type] = value;
	});

	const year = fecha.year;
	const month = fecha.month;
	const day = fecha.day;

	// Construir fecha en formato 'YYYY-MM-DD'
	const fechaHoy = `${year}-${month}-${day}`;

	console.log(`🕐 Buscando respuestas del día (hora Lima GMT-5):`);
	console.log(`   Fecha buscada: ${fechaHoy}`);
	console.log(`   ID Paciente: ${idPaciente}`);

	// Usar TO_CHAR para convertir la fecha a string y compararla como texto
	// Esto evita problemas de conversión de zona horaria
	const respuestas = await sql`
		SELECT
			pr.*,
			em.trastornos_detectados,
			em.condiciones_detectadas,
			em.nivel_riesgo_global,
			em.interpretacion,
			em.requiere_atencion
		FROM paciente_respuesta pr
		LEFT JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_paciente = ${idPaciente}
		AND TO_CHAR(pr.fecha_respuesta AT TIME ZONE 'America/Lima', 'YYYY-MM-DD') = ${fechaHoy}
		ORDER BY pr.fecha_respuesta DESC
	`;

	console.log(
		`📋 Historial del día (Paciente ${idPaciente}): ${respuestas.length} respuesta(s) encontrada(s)`
	);

	return respuestas;
}

/**
 * Obtiene una respuesta por su ID
 * @param {number} idRespuesta - ID de la respuesta
 * @returns {Promise<Object|null>} - Respuesta encontrada o null
 */
export async function getRespuestaById(idRespuesta) {
	const [respuesta] = await sql`
		SELECT
			pr.*,
			em.trastornos_detectados,
			em.condiciones_detectadas,
			em.nivel_riesgo_global,
			em.interpretacion,
			em.requiere_atencion,
			em.palabras_clave,
			em.metricas_modelo
		FROM paciente_respuesta pr
		LEFT JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_respuesta = ${idRespuesta}
	`;
	return respuesta;
}

/**
 * Crea una nueva respuesta del paciente
 * @param {Object} data - Datos de la respuesta
 * @returns {Promise<Object>} - Respuesta creada
 */
export async function createRespuesta(data) {
	// PostgreSQL con postgres.js acepta objetos JavaScript directamente para JSONB
	// No necesitamos hacer JSON.stringify
	const [respuesta] = await sql`
		INSERT INTO paciente_respuesta (
			id_paciente,
			respuestas,
			estado_procesamiento,
			fecha_respuesta
		) VALUES (
			${data.id_paciente},
			${sql.json(data.respuestas)},
			'pendiente',
			NOW() AT TIME ZONE 'America/Lima'
		)
		RETURNING *
	`;
	return respuesta;
}

/**
 * Actualiza el estado de procesamiento de una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @param {string} estado - Nuevo estado: 'pendiente', 'procesado', 'error'
 * @param {number|null} idEvaluacion - ID de la evaluación ML (si fue procesado)
 * @param {string|null} errorMensaje - Mensaje de error (si hubo error)
 * @returns {Promise<Object>} - Respuesta actualizada
 */
export async function updateEstadoRespuesta(
	idRespuesta,
	estado,
	idEvaluacion = null,
	errorMensaje = null
) {
	const [respuesta] = await sql`
		UPDATE paciente_respuesta
		SET
			estado_procesamiento = ${estado},
			id_evaluacion = ${idEvaluacion},
			error_mensaje = ${errorMensaje}
		WHERE id_respuesta = ${idRespuesta}
		RETURNING *
	`;
	return respuesta;
}

/**
 * Obtiene el historial de respuestas con paginación
 * @param {number} idPaciente - ID del paciente
 * @param {number} limite - Cantidad de registros por página
 * @param {number} offset - Desplazamiento
 * @returns {Promise<Array>} - Array de respuestas
 */
export async function getRespuestasPaginadas(idPaciente, limite = 10, offset = 0) {
	const respuestas = await sql`
		SELECT
			pr.id_respuesta,
			pr.fecha_respuesta,
			pr.estado_procesamiento,
			em.condiciones_detectadas,
			em.nivel_riesgo_global,
			em.requiere_atencion
		FROM paciente_respuesta pr
		LEFT JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_paciente = ${idPaciente}
		ORDER BY pr.fecha_respuesta DESC
		LIMIT ${limite}
		OFFSET ${offset}
	`;
	return respuestas;
}

/**
 * Cuenta el total de respuestas de un paciente
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<number>} - Total de respuestas
 */
export async function contarRespuestas(idPaciente) {
	const [result] = await sql`
		SELECT COUNT(*) as count
		FROM paciente_respuesta
		WHERE id_paciente = ${idPaciente}
	`;
	return parseInt(result.count);
}

/**
 * Cuenta el total de notas diarias (respuestas) registradas en el sistema,
 * sin importar el paciente ni la fecha.
 * @returns {Promise<number>} - Total de notas diarias
 */
export async function contarTodasRespuestas() {
	const [result] = await sql`
		SELECT COUNT(*) AS count
		FROM paciente_respuesta
	`;
	return parseInt(result.count);
}

/**
 * Obtiene el detalle completo de una respuesta con evaluación ML
 * @param {number} idRespuesta - ID de la respuesta
 * @returns {Promise<Object>} - Respuesta con evaluación ML completa
 */
export async function getRespuestaDetalle(idRespuesta) {
	const [respuesta] = await sql`
		SELECT
			pr.*,
			em.id_evaluacion,
			em.modelo_nombre,
			em.modelo_tipo,
			em.modelo_version,
			em.trastornos_detectados,
			em.condiciones_detectadas,
			em.nivel_riesgo_global,
			em.interpretacion,
			em.requiere_atencion,
			em.palabras_clave,
			em.metricas_modelo,
			em.fecha_evaluacion
		FROM paciente_respuesta pr
		LEFT JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_respuesta = ${idRespuesta}
	`;

	return respuesta;
}

/**
 * Marca una nota diaria como atendida respecto a las señales de riesgo detectadas.
 * El valor nace en NULL y solo puede pasar a TRUE (no existe estado FALSE).
 * @param {number} idRespuesta - ID de la respuesta
 * @returns {Promise<Object>} - Respuesta actualizada
 */
export async function marcarRiesgoAtendido(idRespuesta) {
	const [respuesta] = await sql`
		UPDATE paciente_respuesta
		SET riesgo_atendido = TRUE
		WHERE id_respuesta = ${idRespuesta}
		RETURNING *
	`;
	return respuesta;
}

/**
 * Obtiene las observaciones asociadas a una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @returns {Promise<Array>} - Array de observaciones
 */
export async function getObservacionesByRespuesta(idRespuesta) {
	const observaciones = await sql`
		SELECT
			o.id_observacion,
			o.id_respuesta,
			o.descripcion,
			o.fecha_observacion,
			o.id_especialista,
			e.nombres   AS especialista_nombres,
			e.apellidos AS especialista_apellidos
		FROM observacion o
		LEFT JOIN especialista e ON o.id_especialista = e.id_especialista
		WHERE o.id_respuesta = ${idRespuesta}
		ORDER BY o.id_observacion ASC
	`;

	return observaciones;
}

/**
 * Reemplaza todas las observaciones de una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @param {string[]} observaciones - Descripciones de observaciones
 * @returns {Promise<Array>} - Observaciones guardadas
 */
export async function replaceObservacionesByRespuesta(idRespuesta, observaciones, idEspecialista = null) {
	// observaciones: [{ id_observacion: number|null, descripcion: string }]
	// Solo contiene las observaciones del especialista actual (propias + nuevas)
	const limpias = observaciones
		.map((o) => ({ id_observacion: o.id_observacion ?? null, descripcion: o.descripcion.trim() }))
		.filter((o) => o.descripcion);

	return sql.begin(async (tx) => {
		const idsConservar = limpias.filter((o) => o.id_observacion).map((o) => o.id_observacion);

		// Eliminar solo las observaciones PROPIAS que ya no están en la lista
		if (idsConservar.length > 0) {
			await tx`
				DELETE FROM observacion
				WHERE id_respuesta = ${idRespuesta}
				  AND id_especialista = ${idEspecialista}
				  AND NOT (id_observacion = ANY(${idsConservar}))
			`;
		} else {
			await tx`
				DELETE FROM observacion
				WHERE id_respuesta = ${idRespuesta}
				  AND id_especialista = ${idEspecialista}
			`;
		}

		const nuevas = limpias.filter((o) => !o.id_observacion);

		if (nuevas.length > 0) {
			// Validar que no se superen 3 observaciones en total
			const [{ count }] = await tx`
				SELECT COUNT(*) AS count FROM observacion WHERE id_respuesta = ${idRespuesta}
			`;
			if (parseInt(count) + nuevas.length > 3) {
				throw new Error('LIMITE_OBSERVACIONES');
			}
		}

		if (limpias.length === 0) return [];

		const observacionesGuardadas = [];

		for (const obs of limpias) {
			if (obs.id_observacion) {
				// Observación propia existente: solo actualizar descripcion
				const [updated] = await tx`
					UPDATE observacion
					SET descripcion       = ${obs.descripcion},
					    fecha_observacion = CASE
					        WHEN descripcion IS DISTINCT FROM ${obs.descripcion}
					        THEN NOW() AT TIME ZONE 'America/Lima'
					        ELSE fecha_observacion
					    END
					WHERE id_observacion = ${obs.id_observacion}
					  AND id_especialista = ${idEspecialista}
					RETURNING id_observacion, id_respuesta, descripcion, id_especialista, fecha_observacion
				`;
				if (updated) observacionesGuardadas.push(updated);
			} else {
				// Nueva observación
				const [inserted] = await tx`
					INSERT INTO observacion (id_respuesta, descripcion, id_especialista, fecha_observacion)
					VALUES (${idRespuesta}, ${obs.descripcion}, ${idEspecialista}, NOW() AT TIME ZONE 'America/Lima')
					RETURNING id_observacion, id_respuesta, descripcion, id_especialista, fecha_observacion
				`;
				observacionesGuardadas.push(inserted);
			}
		}

		return observacionesGuardadas;
	});
}

/**
 * Obtiene la evolución de probabilidades ML de un paciente en los últimos N días.
 * Agrupa por día (zona horaria Lima GMT-5) y promedia si hay múltiples respuestas.
 * @param {number} idPaciente
 * @param {number} dias - ventana máxima (30 para cubrir los tres gráficos)
 * @returns {Promise<Array<{fecha: string, prob_depresion: number, prob_ansiedad: number}>>}
 */
export async function getEvolucionByPaciente(idPaciente, dias = 30) {
	const rows = await sql`
		SELECT
			DATE(pr.fecha_respuesta AT TIME ZONE 'America/Lima') AS fecha,
			AVG((em.trastornos_detectados->'depression'->>'probability')::FLOAT) AS prob_depresion,
			AVG((em.trastornos_detectados->'anxiety'->>'probability')::FLOAT)    AS prob_ansiedad
		FROM paciente_respuesta pr
		INNER JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		WHERE pr.id_paciente        = ${idPaciente}
		  AND pr.estado_procesamiento = 'procesado'
		  AND pr.fecha_respuesta    >= (NOW() AT TIME ZONE 'America/Lima') - (${dias} || ' days')::INTERVAL
		  AND em.trastornos_detectados IS NOT NULL
		GROUP BY DATE(pr.fecha_respuesta AT TIME ZONE 'America/Lima')
		ORDER BY fecha ASC
	`;

	return rows.map((r) => ({
		fecha: r.fecha instanceof Date ? r.fecha.toISOString().split('T')[0] : String(r.fecha),
		prob_depresion: Math.round((parseFloat(r.prob_depresion) || 0) * 100),
		prob_ansiedad: Math.round((parseFloat(r.prob_ansiedad) || 0) * 100)
	}));
}
