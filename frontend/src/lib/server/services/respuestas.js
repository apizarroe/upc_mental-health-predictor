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
		AND TO_CHAR(fecha_respuesta, 'YYYY-MM-DD') = ${fechaHoy}
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
		AND TO_CHAR(pr.fecha_respuesta, 'YYYY-MM-DD') = ${fechaHoy}
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
			estado_procesamiento
		) VALUES (
			${data.id_paciente},
			${sql.json(data.respuestas)},
			'pendiente'
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
 * Obtiene las observaciones asociadas a una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @returns {Promise<Array>} - Array de observaciones
 */
export async function getObservacionesByRespuesta(idRespuesta) {
	const observaciones = await sql`
		SELECT
			id_observacion,
			id_respuesta,
			descripcion
		FROM observacion
		WHERE id_respuesta = ${idRespuesta}
		ORDER BY id_observacion ASC
	`;

	return observaciones;
}

/**
 * Reemplaza todas las observaciones de una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @param {string[]} observaciones - Descripciones de observaciones
 * @returns {Promise<Array>} - Observaciones guardadas
 */
export async function replaceObservacionesByRespuesta(idRespuesta, observaciones) {
	const observacionesLimpias = observaciones
		.map((observacion) => observacion.trim())
		.filter(Boolean);

	return sql.begin(async (tx) => {
		await tx`
			DELETE FROM observacion
			WHERE id_respuesta = ${idRespuesta}
		`;

		if (observacionesLimpias.length === 0) {
			return [];
		}

		const observacionesGuardadas = [];

		for (const descripcion of observacionesLimpias) {
			const [observacion] = await tx`
				INSERT INTO observacion (
					id_respuesta,
					descripcion
				) VALUES (
					${idRespuesta},
					${descripcion}
				)
				RETURNING
					id_observacion,
					id_respuesta,
					descripcion
			`;

			observacionesGuardadas.push(observacion);
		}

		return observacionesGuardadas;
	});
}
