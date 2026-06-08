import sql from '../db/client.js';

export async function getAtencionesByHistoria(idHistoria) {
	return sql`
		SELECT
			a.id_atencion,
			a.id_historia,
			a.id_especialista,
			a.fecha_atencion,
			a.tipo_atencion,
			a.observaciones,
			a.recomendaciones,
			e.nombres   AS especialista_nombres,
			e.apellidos AS especialista_apellidos
		FROM atencion a
		INNER JOIN especialista e ON a.id_especialista = e.id_especialista
		WHERE a.id_historia = ${idHistoria}
		ORDER BY a.fecha_atencion DESC
	`;
}

export async function createAtencion(idHistoria, idEspecialista, data) {
	const [atencion] = await sql`
		INSERT INTO atencion (id_historia, id_especialista, fecha_atencion, tipo_atencion, observaciones, recomendaciones)
		VALUES (
			${idHistoria},
			${idEspecialista},
			NOW() AT TIME ZONE 'America/Lima',
			${data.tipo_atencion},
			${data.observaciones ?? null},
			${data.recomendaciones ?? null}
		)
		RETURNING *
	`;
	return atencion;
}

/**
 * Obtiene las atenciones clínicas más recientes registradas por un especialista,
 * incluyendo el nombre del paciente atendido.
 * @param {number} idEspecialista - ID del especialista que registró las atenciones
 * @param {number} limite - Cantidad máxima de atenciones a retornar
 * @returns {Promise<Array>} - Atenciones ordenadas de la más reciente a la más antigua
 */
export async function getAtencionesRecientes(idEspecialista, limite = 7) {
	return sql`
		SELECT
			a.id_atencion,
			a.fecha_atencion,
			a.tipo_atencion,
			p.id_paciente,
			p.nombres   AS paciente_nombres,
			p.apellidos AS paciente_apellidos
		FROM atencion a
		JOIN historia_clinica hc ON hc.id_historia = a.id_historia
		JOIN paciente p ON p.id_paciente = hc.id_paciente
		WHERE a.id_especialista = ${idEspecialista}
		ORDER BY a.fecha_atencion DESC
		LIMIT ${limite}
	`;
}

/**
 * Cuenta el total de atenciones clínicas registradas en el sistema.
 * @returns {Promise<number>} - Total de atenciones
 */
export async function contarTodasAtenciones() {
	const [result] = await sql`
		SELECT COUNT(*) AS count
		FROM atencion
	`;
	return parseInt(result.count);
}

export async function updateAtencion(idAtencion, idEspecialista, data) {
	const [atencion] = await sql`
		UPDATE atencion
		SET
			tipo_atencion   = ${data.tipo_atencion},
			observaciones   = ${data.observaciones ?? null},
			recomendaciones = ${data.recomendaciones ?? null}
		WHERE id_atencion   = ${idAtencion}
		  AND id_especialista = ${idEspecialista}
		RETURNING *
	`;
	return atencion;
}
