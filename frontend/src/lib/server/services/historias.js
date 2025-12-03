import sql from '../db/client.js';

export async function getAllHistorias() {
	const historias = await sql`
		SELECT
			hc.*,
			p.nombres AS paciente_nombres,
			p.apellidos AS paciente_apellidos,
			p.dni AS paciente_dni,
			e.nombres AS especialista_nombres,
			e.apellidos AS especialista_apellidos
		FROM historia_clinica hc
		LEFT JOIN paciente p ON hc.id_paciente = p.id_paciente
		LEFT JOIN especialista e ON hc.especialista_apertura = e.id_especialista
		ORDER BY hc.fecha_apertura DESC
	`;
	return historias;
}

export async function getHistoriaById(id) {
	const [historia] = await sql`
		SELECT
			hc.*,
			p.nombres AS paciente_nombres,
			p.apellidos AS paciente_apellidos,
			p.dni AS paciente_dni,
			p.fecha_nacimiento AS paciente_fecha_nacimiento,
			p.sexo AS paciente_sexo,
			p.telefono AS paciente_telefono,
			p.correo AS paciente_correo,
			e.nombres AS especialista_nombres,
			e.apellidos AS especialista_apellidos
		FROM historia_clinica hc
		LEFT JOIN paciente p ON hc.id_paciente = p.id_paciente
		LEFT JOIN especialista e ON hc.especialista_apertura = e.id_especialista
		WHERE hc.id_historia = ${id}
	`;
	return historia;
}

export async function getHistoriaByPacienteId(idPaciente) {
	const [historia] = await sql`
		SELECT * FROM historia_clinica
		WHERE id_paciente = ${idPaciente}
		AND (situacion_historia IS NULL OR situacion_historia != 'Cerrada')
		LIMIT 1
	`;
	return historia;
}

export async function createHistoria(data) {
	// Convertir campos JSONB a JSON si vienen como objetos
	const antecedentesFamiliares = data.antecedentes_familiares
		? (typeof data.antecedentes_familiares === 'string'
			? data.antecedentes_familiares
			: JSON.stringify(data.antecedentes_familiares))
		: null;

	const habitosPersonales = data.habitos_personales
		? (typeof data.habitos_personales === 'string'
			? data.habitos_personales
			: JSON.stringify(data.habitos_personales))
		: null;

	const [historia] = await sql`
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
		) VALUES (
			${data.id_paciente},
			${data.especialista_apertura},
			${data.servicio_origen || null},
			${data.antecedentes_personales || null},
			${antecedentesFamiliares}::jsonb,
			${data.antecedentes_psicosociales || null},
			${habitosPersonales}::jsonb,
			${data.situacion_familiar || null},
			${data.situacion_laboral || null},
			${data.evaluacion_inicial || null},
			${data.diagnostico_inicial || null},
			${data.tratamientos_previos || null},
			${data.situacion_historia || 'Abierta'}
		)
		RETURNING *
	`;
	return historia;
}

export async function updateHistoria(id, data, idEspecialista) {
	const updates = {};
	const allowedFields = [
		'servicio_origen',
		'antecedentes_personales',
		'antecedentes_familiares',
		'antecedentes_psicosociales',
		'habitos_personales',
		'situacion_familiar',
		'situacion_laboral',
		'evaluacion_inicial',
		'diagnostico_inicial',
		'tratamientos_previos',
		'situacion_historia',
		'motivo_cierre'
	];

	for (const field of allowedFields) {
		if (data[field] !== undefined) {
			// Convertir campos JSONB si vienen como objetos
			if (field === 'antecedentes_familiares' || field === 'habitos_personales') {
				if (typeof data[field] === 'object' && data[field] !== null) {
					updates[field] = JSON.stringify(data[field]);
				} else {
					updates[field] = data[field];
				}
			} else {
				updates[field] = data[field];
			}
		}
	}

	if (Object.keys(updates).length === 0) {
		return getHistoriaById(id);
	}

	updates.fecha_actualizacion = new Date();
	updates.especialista_actualizacion = idEspecialista;

	// Si se está cerrando la historia (temporal o definitivo), actualizar fecha_cierre
	if (data.situacion_historia === 'Cierre Temporal' || data.situacion_historia === 'Cierre Definitivo') {
		updates.fecha_cierre = new Date();
	}

	// Si se está reabriendo la historia, limpiar fecha_cierre
	if (data.situacion_historia === 'Abierta') {
		updates.fecha_cierre = null;
	}

	const [historia] = await sql`
		UPDATE historia_clinica
		SET ${sql(updates)}
		WHERE id_historia = ${id}
		RETURNING *
	`;
	return historia;
}

export async function cerrarHistoria(id, motivoCierre, idEspecialista) {
	const [historia] = await sql`
		UPDATE historia_clinica
		SET
			situacion_historia = 'Cerrada',
			fecha_cierre = NOW(),
			motivo_cierre = ${motivoCierre},
			fecha_actualizacion = NOW(),
			especialista_actualizacion = ${idEspecialista}
		WHERE id_historia = ${id}
		RETURNING *
	`;
	return historia;
}

export async function getMedicacionesByHistoria(idHistoria) {
	const medicaciones = await sql`
		SELECT * FROM paciente_medicacion
		WHERE id_historia = ${idHistoria}
		ORDER BY fecha_registro DESC
	`;
	return medicaciones;
}

export async function addMedicacion(data) {
	const [medicacion] = await sql`
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
		) VALUES (
			${data.id_historia},
			${data.medicacion},
			${data.concentracion || null},
			${data.forma_farmaceutica || null},
			${data.dosis || null},
			${data.frecuencia || null},
			${data.anio_inicio || null},
			${data.tipo_medicacion || null},
			${data.prescrito_por || null},
			${data.observaciones || null}
		)
		RETURNING *
	`;
	return medicacion;
}

export async function deleteMedicacion(id) {
	const [medicacion] = await sql`
		DELETE FROM paciente_medicacion
		WHERE id_medicacion_paciente = ${id}
		RETURNING *
	`;
	return medicacion;
}
