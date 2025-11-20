import sql from '../db/client.js';

/**
 * Servicio para gestionar especialistas en la base de datos
 */

/**
 * Obtener todos los especialistas (activos e inactivos)
 * Retorna todos para que el frontend pueda mostrar métricas completas
 */
export async function getAllEspecialistas() {
	const especialistas = await sql`
		SELECT * FROM especialista
		ORDER BY id_especialista DESC
	`;
	return especialistas;
}

/**
 * Obtener un especialista por ID
 */
export async function getEspecialistaById(id) {
	const [especialista] = await sql`
		SELECT * FROM especialista
		WHERE id_especialista = ${id}
	`;
	return especialista;
}

/**
 * Crear un nuevo especialista
 * Setea automáticamente: flg_activo (true)
 */
export async function createEspecialista(data) {
	const [especialista] = await sql`
		INSERT INTO especialista (
			dni,
			nombres,
			apellidos,
			especialidad,
			colegiatura,
			correo,
			telefono,
			cargo,
			flg_activo
		) VALUES (
			${data.dni}::varchar,
			${data.nombres}::varchar,
			${data.apellidos}::varchar,
			${data.especialidad}::varchar,
			${data.colegiatura}::varchar,
			${data.correo}::varchar,
			${data.telefono}::varchar,
			${data.cargo}::varchar,
			true
		)
		RETURNING *
	`;
	return especialista;
}

/**
 * Actualizar un especialista existente
 * Solo actualiza los campos que se envían en data
 */
export async function updateEspecialista(id, data) {
	// Filtrar solo los campos que están presentes en data
	const updates = {};
	const allowedFields = [
		'dni',
		'nombres',
		'apellidos',
		'especialidad',
		'colegiatura',
		'correo',
		'telefono',
		'cargo',
		'flg_activo'
	];

	// Solo incluir campos que están definidos
	for (const field of allowedFields) {
		if (data[field] !== undefined) {
			updates[field] = data[field];
		}
	}

	// Si no hay campos para actualizar, retornar el especialista actual
	if (Object.keys(updates).length === 0) {
		return getEspecialistaById(id);
	}

	// Construir la query dinámicamente
	const [especialista] = await sql`
		UPDATE especialista
		SET ${sql(updates)}
		WHERE id_especialista = ${id}
		RETURNING *
	`;
	return especialista;
}

/**
 * Eliminar (desactivar) un especialista
 * No elimina físicamente, solo setea flg_activo = false
 */
export async function deleteEspecialista(id) {
	const [especialista] = await sql`
		UPDATE especialista
		SET flg_activo = false
		WHERE id_especialista = ${id}
		RETURNING *
	`;
	return especialista;
}

/**
 * Eliminar físicamente un especialista (usar con precaución)
 */
export async function hardDeleteEspecialista(id) {
	const [especialista] = await sql`
		DELETE FROM especialista
		WHERE id_especialista = ${id}
		RETURNING *
	`;
	return especialista;
}
