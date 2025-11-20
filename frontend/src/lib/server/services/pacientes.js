import sql from '../db/client.js';
import bcrypt from 'bcrypt';

/**
 * Servicio para gestionar pacientes en la base de datos
 */

/**
 * Obtener todos los pacientes (activos e inactivos)
 * Retorna todos para que el frontend pueda mostrar métricas completas
 */
export async function getAllPacientes() {
	const pacientes = await sql`
		SELECT * FROM paciente
		ORDER BY id_paciente DESC
	`;
	return pacientes;
}

/**
 * Obtener un paciente por ID
 */
export async function getPacienteById(id) {
	const [paciente] = await sql`
		SELECT * FROM paciente
		WHERE id_paciente = ${id}
	`;
	return paciente;
}

/**
 * Crear un nuevo paciente
 * Setea automáticamente: fecha_registro (NOW), flg_activo (true), rol ('paciente')
 * Si se proporciona usuario y password, hashea el password
 */
export async function createPaciente(data) {
	// Hashear password si se proporciona
	let passwordHash = null;
	if (data.password) {
		const saltRounds = 10;
		passwordHash = await bcrypt.hash(data.password, saltRounds);
	}

	const [paciente] = await sql`
		INSERT INTO paciente (
			dni,
			nombres,
			apellidos,
			fecha_nacimiento,
			sexo,
			direccion,
			telefono,
			correo,
			contacto_emergencia,
			telefono_emergencia,
			usuario,
			password_hash,
			rol,
			fecha_registro,
			flg_activo
		) VALUES (
			${data.dni}::varchar,
			${data.nombres}::varchar,
			${data.apellidos}::varchar,
			${data.fecha_nacimiento}::date,
			${data.sexo}::char,
			${data.direccion}::varchar,
			${data.telefono}::varchar,
			${data.correo}::varchar,
			${data.contacto_emergencia}::varchar,
			${data.telefono_emergencia}::varchar,
			${data.usuario || null}::varchar,
			${passwordHash},
			'paciente',
			NOW(),
			true
		)
		RETURNING *
	`;

	// No retornar password_hash en el response
	const { password_hash, ...pacienteSinPassword } = paciente;
	return pacienteSinPassword;
}

/**
 * Actualizar un paciente existente
 * Solo actualiza los campos que se envían en data
 * Nota: NO permite actualizar usuario o rol por seguridad (solo admins pueden)
 */
export async function updatePaciente(id, data) {
	// Filtrar solo los campos que están presentes en data
	const updates = {};
	const allowedFields = [
		'dni',
		'nombres',
		'apellidos',
		'fecha_nacimiento',
		'sexo',
		'direccion',
		'telefono',
		'correo',
		'contacto_emergencia',
		'telefono_emergencia',
		'flg_activo'
	];

	// Solo incluir campos que están definidos
	for (const field of allowedFields) {
		if (data[field] !== undefined) {
			updates[field] = data[field];
		}
	}

	// Si se proporciona un nuevo password, hashearlo
	if (data.password) {
		const saltRounds = 10;
		updates.password_hash = await bcrypt.hash(data.password, saltRounds);
	}

	// Si no hay campos para actualizar, retornar el paciente actual
	if (Object.keys(updates).length === 0) {
		return getPacienteById(id);
	}

	// Construir la query dinámicamente
	const [paciente] = await sql`
		UPDATE paciente
		SET ${sql(updates)}
		WHERE id_paciente = ${id}
		RETURNING *
	`;

	// No retornar password_hash en el response
	if (paciente) {
		const { password_hash, ...pacienteSinPassword } = paciente;
		return pacienteSinPassword;
	}

	return paciente;
}

/**
 * Eliminar (desactivar) un paciente
 * No elimina físicamente, solo setea flg_activo = false
 */
export async function deletePaciente(id) {
	const [paciente] = await sql`
		UPDATE paciente
		SET flg_activo = false
		WHERE id_paciente = ${id}
		RETURNING *
	`;
	return paciente;
}

/**
 * Eliminar físicamente un paciente (usar con precaución)
 */
export async function hardDeletePaciente(id) {
	const [paciente] = await sql`
		DELETE FROM paciente
		WHERE id_paciente = ${id}
		RETURNING *
	`;
	return paciente;
}
