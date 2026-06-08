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
		SELECT
			p.*,
			(
				SELECT MAX(a.fecha_atencion)
				FROM atencion a
				JOIN historia_clinica hc ON hc.id_historia = a.id_historia
				WHERE hc.id_paciente = p.id_paciente
			) AS fecha_ultima_consulta
		FROM paciente p
		ORDER BY p.id_paciente DESC
	`;
	return pacientes;
}

/**
 * Obtener IDs de pacientes que tienen historia clínica
 * Para performance, solo retorna los IDs
 */
export async function getPacientesConHistoriaClinica() {
	const pacientes = await sql`
		SELECT DISTINCT id_paciente
		FROM historia_clinica
	`;
	return pacientes.map(p => p.id_paciente);
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
 * Setea automáticamente:
 * - fecha_registro (NOW)
 * - flg_activo (true)
 * - password_hash (DNI hasheado con bcrypt)
 * - password_cambiado_en (NULL - para forzar cambio en primer login)
 */
export async function createPaciente(data) {
	// Hashear el DNI como contraseña por defecto
	const saltRounds = 10;
	const passwordHash = await bcrypt.hash(data.dni, saltRounds);

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
			password_hash,
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
			${passwordHash}::varchar,
			NOW() AT TIME ZONE 'America/Lima',
			true
		)
		RETURNING *
	`;
	return paciente;
}

/**
 * Actualizar un paciente existente
 * Solo actualiza los campos que se envían en data
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
