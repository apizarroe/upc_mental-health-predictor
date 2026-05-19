import sql from '../db/client.js';

function normalizarDiagnostico(diagnostico = {}) {
	return {
		depression: Boolean(diagnostico.depression),
		anxiety: Boolean(diagnostico.anxiety)
	};
}

function limpiarTextoOpcional(valor) {
	if (typeof valor !== 'string') return null;
	const limpio = valor.trim();
	return limpio ? limpio : null;
}

export function getDiagnosticoModelo(trastornosDetectados = {}) {
	return {
		depression: Boolean(trastornosDetectados?.depression?.has_condition),
		anxiety: Boolean(trastornosDetectados?.anxiety?.has_condition)
	};
}

export function calcularComparacionDiagnosticos(diagnosticoModelo, diagnosticoEspecialista) {
	const modelo = normalizarDiagnostico(diagnosticoModelo);
	const especialista = normalizarDiagnostico(diagnosticoEspecialista);

	const condiciones = ['depression', 'anxiety'];
	const coincidencias = condiciones.filter(
		(condicion) => modelo[condicion] === especialista[condicion]
	);
	const falsosPositivos = condiciones.filter(
		(condicion) => modelo[condicion] && !especialista[condicion]
	);
	const falsosNegativos = condiciones.filter(
		(condicion) => !modelo[condicion] && especialista[condicion]
	);

	return {
		coincidencias,
		falsosPositivos,
		falsosNegativos,
		esCoincidenteTotal: coincidencias.length === condiciones.length
	};
}

function mapearPrecisionPorDecision(decision) {
	if (decision === 'aceptar') return 'alta';
	if (decision === 'modificar') return 'media';
	return 'baja';
}

export async function getValidacionByEvaluacionAndEspecialista(idEvaluacion, idEspecialista) {
	const [validacion] = await sql`
		SELECT
			ev.*,
			e.nombres AS especialista_nombres,
			e.apellidos AS especialista_apellidos
		FROM evaluacion_validacion ev
		LEFT JOIN especialista e ON e.id_especialista = ev.id_especialista
		WHERE ev.id_evaluacion = ${idEvaluacion}
		  AND ev.id_especialista = ${idEspecialista}
		ORDER BY ev.fecha_validacion DESC, ev.id_validacion DESC
		LIMIT 1
	`;

	return validacion ?? null;
}

export async function saveValidacion({
	idEvaluacion,
	idEspecialista,
	decision,
	diagnosticoModelo,
	diagnosticoEspecialista,
	nivelConfianza = null,
	observaciones = null,
	recomendacionPaciente = null,
	requiereSeguimiento = false
}) {
	const diagnosticoEspecialistaNormalizado = normalizarDiagnostico(diagnosticoEspecialista);
	const comparacion = calcularComparacionDiagnosticos(
		diagnosticoModelo,
		diagnosticoEspecialistaNormalizado
	);

	const coincidencias = {
		decision,
		diagnostico_modelo: normalizarDiagnostico(diagnosticoModelo),
		diagnostico_especialista: diagnosticoEspecialistaNormalizado,
		coincidencias: comparacion.coincidencias,
		falsos_positivos: comparacion.falsosPositivos,
		falsos_negativos: comparacion.falsosNegativos
	};

	const payload = {
		diagnosticoEspecialista: diagnosticoEspecialistaNormalizado,
		coincidencias,
		precisionGlobal: mapearPrecisionPorDecision(decision),
		falsosPositivos: comparacion.falsosPositivos,
		falsosNegativos: comparacion.falsosNegativos,
		nivelConfianza,
		observaciones: limpiarTextoOpcional(observaciones),
		recomendacionPaciente: limpiarTextoOpcional(recomendacionPaciente),
		requiereSeguimiento: Boolean(requiereSeguimiento),
		utilParaEntrenamiento: decision !== 'aceptar'
	};

	const existente = await getValidacionByEvaluacionAndEspecialista(idEvaluacion, idEspecialista);

	if (existente) {
		const [actualizada] = await sql`
			UPDATE evaluacion_validacion
			SET
				fecha_validacion = NOW() AT TIME ZONE 'America/Lima',
				diagnostico_especialista = ${sql.json(payload.diagnosticoEspecialista)},
				coincidencias = ${sql.json(payload.coincidencias)},
				precision_global = ${payload.precisionGlobal},
				falsos_positivos = ${payload.falsosPositivos},
				falsos_negativos = ${payload.falsosNegativos},
				nivel_confianza = ${payload.nivelConfianza},
				observaciones = ${payload.observaciones},
				recomendacion_paciente = ${payload.recomendacionPaciente},
				requiere_seguimiento = ${payload.requiereSeguimiento},
				util_para_entrenamiento = ${payload.utilParaEntrenamiento}
			WHERE id_validacion = ${existente.id_validacion}
			RETURNING *
		`;

		return actualizada;
	}

	const [creada] = await sql`
		INSERT INTO evaluacion_validacion (
			id_evaluacion,
			id_especialista,
			diagnostico_especialista,
			coincidencias,
			precision_global,
			falsos_positivos,
			falsos_negativos,
			nivel_confianza,
			observaciones,
			recomendacion_paciente,
			requiere_seguimiento,
			util_para_entrenamiento
		) VALUES (
			${idEvaluacion},
			${idEspecialista},
			${sql.json(payload.diagnosticoEspecialista)},
			${sql.json(payload.coincidencias)},
			${payload.precisionGlobal},
			${payload.falsosPositivos},
			${payload.falsosNegativos},
			${payload.nivelConfianza},
			${payload.observaciones},
			${payload.recomendacionPaciente},
			${payload.requiereSeguimiento},
			${payload.utilParaEntrenamiento}
		)
		RETURNING *
	`;

	return creada;
}
