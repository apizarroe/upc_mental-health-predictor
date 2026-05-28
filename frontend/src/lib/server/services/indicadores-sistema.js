import sql from '../db/client.js';
import {
	construirResumenPruebasRecomendadas,
	generarCsvReporte,
	validarRangoReporte
} from '$lib/utils/system-reports.js';

function getNombreSolicitante(user) {
	return (
		[user?.nombres, user?.apellidos].filter(Boolean).join(' ').trim() || user?.usuario || 'Admin'
	);
}

function mapearReporte(reporte) {
	return {
		...reporte,
		solicitante_nombre:
			reporte.solicitante_nombre ??
			[reporte.solicitante_nombres, reporte.solicitante_apellidos].filter(Boolean).join(' ').trim()
	};
}

export function validarParametrosReporte(fechaInicio, fechaFin) {
	return validarRangoReporte(fechaInicio, fechaFin);
}

async function contarPacientesAtendidos(inicioTimestamp, finExclusiveTimestamp) {
	const [resultado] = await sql`
		SELECT COUNT(DISTINCT pr.id_paciente) AS total
		FROM paciente_respuesta pr
		INNER JOIN historia_clinica hc ON hc.id_paciente = pr.id_paciente
		WHERE pr.fecha_respuesta >= ${inicioTimestamp}
		  AND pr.fecha_respuesta < ${finExclusiveTimestamp}
	`;

	return Number(resultado?.total ?? 0);
}

async function contarNotasAnalizadas(inicioTimestamp, finExclusiveTimestamp) {
	const [resultado] = await sql`
		SELECT COUNT(*) AS total
		FROM paciente_respuesta
		WHERE fecha_respuesta >= ${inicioTimestamp}
		  AND fecha_respuesta < ${finExclusiveTimestamp}
		  AND id_evaluacion IS NOT NULL
	`;

	return Number(resultado?.total ?? 0);
}

async function contarDiagnosticosSugeridos(inicioTimestamp, finExclusiveTimestamp) {
	const [resultado] = await sql`
		SELECT COUNT(*) AS total
		FROM evaluacion_ml
		WHERE fecha_evaluacion >= ${inicioTimestamp}
		  AND fecha_evaluacion < ${finExclusiveTimestamp}
		  AND condiciones_detectadas IS NOT NULL
		  AND cardinality(condiciones_detectadas) > 0
	`;

	return Number(resultado?.total ?? 0);
}

async function contarDiagnosticosAceptados(inicioTimestamp, finExclusiveTimestamp) {
	const [resultado] = await sql`
		SELECT COUNT(*) AS total
		FROM evaluacion_validacion
		WHERE fecha_validacion >= ${inicioTimestamp}
		  AND fecha_validacion < ${finExclusiveTimestamp}
		  AND coincidencias ->> 'decision' = 'aceptar'
	`;

	return Number(resultado?.total ?? 0);
}

async function obtenerPromediosPorPaciente(inicioTimestamp, finExclusiveTimestamp) {
	return sql`
		SELECT
			pr.id_paciente,
			AVG(COALESCE((em.trastornos_detectados -> 'depression' ->> 'probability')::numeric, 0) * 100) AS promedio_depresion,
			AVG(COALESCE((em.trastornos_detectados -> 'anxiety' ->> 'probability')::numeric, 0) * 100) AS promedio_ansiedad
		FROM evaluacion_ml em
		INNER JOIN paciente_respuesta pr ON pr.id_respuesta = em.id_respuesta
		WHERE em.fecha_evaluacion >= ${inicioTimestamp}
		  AND em.fecha_evaluacion < ${finExclusiveTimestamp}
		GROUP BY pr.id_paciente
	`;
}

export async function generarReporteIndicadores({ fechaInicio, fechaFin, user }) {
	const rango = validarParametrosReporte(fechaInicio, fechaFin);
	if (!rango.ok) {
		const error = new Error(rango.error);
		error.status = 400;
		throw error;
	}

	const [
		pacientesAtendidos,
		notasAnalizadas,
		diagnosticosSugeridos,
		diagnosticosAceptados,
		promediosPacientes
	] = await Promise.all([
		contarPacientesAtendidos(rango.inicioTimestamp, rango.finExclusiveTimestamp),
		contarNotasAnalizadas(rango.inicioTimestamp, rango.finExclusiveTimestamp),
		contarDiagnosticosSugeridos(rango.inicioTimestamp, rango.finExclusiveTimestamp),
		contarDiagnosticosAceptados(rango.inicioTimestamp, rango.finExclusiveTimestamp),
		obtenerPromediosPorPaciente(rango.inicioTimestamp, rango.finExclusiveTimestamp)
	]);

	const pruebasRecomendadas = construirResumenPruebasRecomendadas(promediosPacientes);

	const snapshot = {
		metadata: {
			usuario_solicitante: getNombreSolicitante(user),
			id_especialista_solicitante: user.id_especialista,
			formato_exportacion: 'csv',
			fecha_inicio: fechaInicio,
			fecha_fin: fechaFin
		},
		totales: {
			pacientes_atendidos: pacientesAtendidos,
			notas_analizadas: notasAnalizadas,
			diagnosticos_sugeridos: diagnosticosSugeridos,
			diagnosticos_aceptados: diagnosticosAceptados
		},
		pruebas_psicologicas_recomendadas: pruebasRecomendadas
	};

	const [reporte] = await sql`
		INSERT INTO reporte_indicadores_sistema (
			id_especialista_solicitante,
			fecha_inicio,
			fecha_fin,
			indicadores_json,
			formato_exportacion
		) VALUES (
			${user.id_especialista},
			${fechaInicio},
			${fechaFin},
			${sql.json(snapshot)},
			'csv'
		)
		RETURNING *
	`;

	const [reporteConSolicitante] = await sql`
		SELECT
			ris.*,
			e.nombres AS solicitante_nombres,
			e.apellidos AS solicitante_apellidos
		FROM reporte_indicadores_sistema ris
		INNER JOIN especialista e ON e.id_especialista = ris.id_especialista_solicitante
		WHERE ris.id_reporte = ${reporte.id_reporte}
	`;

	return mapearReporte(reporteConSolicitante);
}

export async function listarReportesIndicadores({ limit = 20, offset = 0 } = {}) {
	const safeLimit = Math.max(1, Math.min(Number(limit) || 20, 100));
	const safeOffset = Math.max(0, Number(offset) || 0);

	const reportes = await sql`
		SELECT
			ris.*,
			e.nombres AS solicitante_nombres,
			e.apellidos AS solicitante_apellidos
		FROM reporte_indicadores_sistema ris
		INNER JOIN especialista e ON e.id_especialista = ris.id_especialista_solicitante
		ORDER BY ris.fecha_generacion DESC, ris.id_reporte DESC
		LIMIT ${safeLimit}
		OFFSET ${safeOffset}
	`;

	const [conteo] = await sql`
		SELECT COUNT(*) AS total
		FROM reporte_indicadores_sistema
	`;

	return {
		data: reportes.map(mapearReporte),
		total: Number(conteo?.total ?? 0),
		limit: safeLimit,
		offset: safeOffset
	};
}

export async function getReporteIndicadoresById(idReporte) {
	const [reporte] = await sql`
		SELECT
			ris.*,
			e.nombres AS solicitante_nombres,
			e.apellidos AS solicitante_apellidos
		FROM reporte_indicadores_sistema ris
		INNER JOIN especialista e ON e.id_especialista = ris.id_especialista_solicitante
		WHERE ris.id_reporte = ${idReporte}
	`;

	return reporte ? mapearReporte(reporte) : null;
}

export async function exportarReporteIndicadoresCsv(idReporte) {
	const reporte = await getReporteIndicadoresById(idReporte);

	if (!reporte) {
		return null;
	}

	return {
		reporte,
		csv: generarCsvReporte(reporte)
	};
}
