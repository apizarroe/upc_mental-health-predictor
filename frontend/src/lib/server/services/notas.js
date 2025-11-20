import sql from '../db/client.js';

/**
 * Servicio para gestión de notas de pacientes
 */

/**
 * Obtener todas las notas de un paciente
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<Array>} Lista de notas del paciente
 */
export async function getNotasByPaciente(idPaciente) {
	const notas = await sql`
		SELECT
			id_nota,
			id_paciente,
			pregunta,
			respuesta,
			fecha_registro
		FROM notas
		WHERE id_paciente = ${idPaciente}
		ORDER BY fecha_registro DESC
	`;

	return notas;
}

/**
 * Obtener una nota específica por ID
 * @param {number} idNota - ID de la nota
 * @returns {Promise<Object|null>} Nota encontrada o null
 */
export async function getNotaById(idNota) {
	const [nota] = await sql`
		SELECT
			id_nota,
			id_paciente,
			pregunta,
			respuesta,
			fecha_registro
		FROM notas
		WHERE id_nota = ${idNota}
	`;

	return nota || null;
}

/**
 * Crear una nueva nota
 * @param {number} idPaciente - ID del paciente
 * @param {string} pregunta - Pregunta respondida
 * @param {string} respuesta - Respuesta del paciente
 * @returns {Promise<Object>} Nota creada
 */
export async function createNota(idPaciente, pregunta, respuesta) {
	const [nota] = await sql`
		INSERT INTO notas (id_paciente, pregunta, respuesta)
		VALUES (${idPaciente}, ${pregunta}, ${respuesta})
		RETURNING
			id_nota,
			id_paciente,
			pregunta,
			respuesta,
			fecha_registro
	`;

	return nota;
}

/**
 * Crear múltiples notas a la vez (batch insert)
 * @param {number} idPaciente - ID del paciente
 * @param {Array<{pregunta: string, respuesta: string}>} notas - Array de notas a crear
 * @returns {Promise<Array>} Notas creadas
 */
export async function createNotasBatch(idPaciente, notas) {
	// Construir array de valores para inserción masiva
	const values = notas.map(nota => ({
		id_paciente: idPaciente,
		pregunta: nota.pregunta,
		respuesta: nota.respuesta
	}));

	const notasCreadas = await sql`
		INSERT INTO notas ${sql(values, 'id_paciente', 'pregunta', 'respuesta')}
		RETURNING
			id_nota,
			id_paciente,
			pregunta,
			respuesta,
			fecha_registro
	`;

	return notasCreadas;
}

/**
 * Actualizar una nota existente
 * @param {number} idNota - ID de la nota
 * @param {string} respuesta - Nueva respuesta
 * @returns {Promise<Object>} Nota actualizada
 */
export async function updateNota(idNota, respuesta) {
	const [nota] = await sql`
		UPDATE notas
		SET respuesta = ${respuesta}
		WHERE id_nota = ${idNota}
		RETURNING
			id_nota,
			id_paciente,
			pregunta,
			respuesta,
			fecha_registro
	`;

	return nota;
}

/**
 * Eliminar una nota
 * @param {number} idNota - ID de la nota
 * @returns {Promise<boolean>} true si se eliminó correctamente
 */
export async function deleteNota(idNota) {
	const result = await sql`
		DELETE FROM notas
		WHERE id_nota = ${idNota}
		RETURNING id_nota
	`;

	return result.length > 0;
}

/**
 * Obtener estadísticas de notas de un paciente
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<Object>} Estadísticas
 */
export async function getNotasStats(idPaciente) {
	const [stats] = await sql`
		SELECT
			COUNT(*) as total_notas,
			COUNT(DISTINCT DATE(fecha_registro)) as dias_con_notas,
			MIN(fecha_registro) as primera_nota,
			MAX(fecha_registro) as ultima_nota
		FROM notas
		WHERE id_paciente = ${idPaciente}
	`;

	return {
		totalNotas: parseInt(stats.total_notas),
		diasConNotas: parseInt(stats.dias_con_notas),
		primeraNota: stats.primera_nota,
		ultimaNota: stats.ultima_nota
	};
}

/**
 * Obtener notas agrupadas por fecha
 * @param {number} idPaciente - ID del paciente
 * @returns {Promise<Array>} Notas agrupadas por fecha
 */
export async function getNotasGroupedByDate(idPaciente) {
	const notas = await sql`
		SELECT
			DATE(fecha_registro) as fecha,
			json_agg(
				json_build_object(
					'id_nota', id_nota,
					'pregunta', pregunta,
					'respuesta', respuesta,
					'fecha_registro', fecha_registro
				)
				ORDER BY fecha_registro DESC
			) as notas_del_dia
		FROM notas
		WHERE id_paciente = ${idPaciente}
		GROUP BY DATE(fecha_registro)
		ORDER BY fecha DESC
	`;

	return notas.map(item => ({
		fecha: item.fecha,
		notas: item.notas_del_dia
	}));
}
