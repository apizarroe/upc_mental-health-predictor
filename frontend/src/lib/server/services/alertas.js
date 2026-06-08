import sql from '../db/client.js';

export async function getAlertasRiesgo(idEspecialista) {
	const alertas = await sql`
		SELECT
			pr.id_respuesta,
			pr.id_paciente,
			pr.fecha_respuesta,
			em.trastornos_detectados,
			em.nivel_riesgo_global,
			em.requiere_atencion,
			em.fecha_evaluacion,
			p.nombres AS paciente_nombres,
			p.apellidos AS paciente_apellidos,
			EXISTS (
				SELECT 1
				FROM historia_clinica hc
				JOIN atencion a ON a.id_historia = hc.id_historia
				WHERE hc.id_paciente = p.id_paciente
				AND a.id_especialista = ${idEspecialista}
			) AS es_mi_paciente,
			COALESCE(
				(
					SELECT jsonb_agg(DISTINCT jsonb_build_object(
						'id_especialista', e2.id_especialista,
						'usuario', e2.usuario,
						'nombres', e2.nombres,
						'apellidos', e2.apellidos
					))
					FROM historia_clinica hc2
					JOIN atencion a2 ON a2.id_historia = hc2.id_historia
					JOIN especialista e2 ON e2.id_especialista = a2.id_especialista
					WHERE hc2.id_paciente = p.id_paciente
				),
				'[]'::jsonb
			) AS especialistas_tratantes
		FROM paciente_respuesta pr
		JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
		JOIN paciente p ON p.id_paciente = pr.id_paciente
		WHERE
			em.trastornos_detectados IS NOT NULL
			AND em.trastornos_detectados ? 'risk_assessment'
			AND jsonb_array_length(em.trastornos_detectados->'risk_assessment'->'señales_detectadas') > 0
			AND em.fecha_evaluacion >= NOW() AT TIME ZONE 'America/Lima' - INTERVAL '14 days'
			AND pr.riesgo_atendido IS NOT TRUE
		ORDER BY em.fecha_evaluacion DESC
	`;
	return alertas;
}

/**
 * Cuenta el total de alertas de riesgo pendientes en el sistema (todos los especialistas),
 * en la ventana de los últimos 14 días.
 * @returns {Promise<number>} - Total de alertas pendientes
 */
export async function getConteoAlertasTotal() {
	try {
		const [result] = await sql`
			SELECT COUNT(*) AS total
			FROM paciente_respuesta pr
			JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
			WHERE
				em.trastornos_detectados IS NOT NULL
				AND em.trastornos_detectados ? 'risk_assessment'
				AND jsonb_array_length(em.trastornos_detectados->'risk_assessment'->'señales_detectadas') > 0
				AND em.fecha_evaluacion >= NOW() AT TIME ZONE 'America/Lima' - INTERVAL '14 days'
				AND pr.riesgo_atendido IS NOT TRUE
		`;
		return parseInt(result.total);
	} catch {
		return 0;
	}
}

/**
 * Cuenta las alertas de riesgo pendientes de pacientes atendidos por el especialista
 * (relación paciente -> atencion -> especialista), en la ventana de los últimos 14 días.
 * @param {number} idEspecialista - ID del especialista
 * @returns {Promise<number>} - Total de alertas de "mis pacientes"
 */
export async function getConteoAlertasMisPacientes(idEspecialista) {
	try {
		const [result] = await sql`
			SELECT COUNT(*) AS total
			FROM paciente_respuesta pr
			JOIN evaluacion_ml em ON pr.id_evaluacion = em.id_evaluacion
			JOIN paciente p ON p.id_paciente = pr.id_paciente
			WHERE
				em.trastornos_detectados IS NOT NULL
				AND em.trastornos_detectados ? 'risk_assessment'
				AND jsonb_array_length(em.trastornos_detectados->'risk_assessment'->'señales_detectadas') > 0
				AND em.fecha_evaluacion >= NOW() AT TIME ZONE 'America/Lima' - INTERVAL '14 days'
				AND pr.riesgo_atendido IS NOT TRUE
				AND EXISTS (
					SELECT 1
					FROM historia_clinica hc
					JOIN atencion a ON a.id_historia = hc.id_historia
					WHERE hc.id_paciente = p.id_paciente
					AND a.id_especialista = ${idEspecialista}
				)
		`;
		return parseInt(result.total);
	} catch {
		return 0;
	}
}
