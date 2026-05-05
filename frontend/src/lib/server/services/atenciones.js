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
