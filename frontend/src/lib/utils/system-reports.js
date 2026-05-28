export const UMBRAL_RECOMENDACION_PRUEBAS = 38;

export const PRUEBAS_RECOMENDADAS = {
	depression: [
		'Cuestionario de Salud del Paciente (PHQ-9)',
		'Escala de Hamilton para la Ansiedad (HAM-A)',
		'Inventario de Ansiedad Estado-Rasgo (STAI)'
	],
	anxiety: [
		'Escala de Ansiedad Generalizada (GAD-7)',
		'Inventario de Depresión de Beck (BDI)',
		'Escala de Hamilton para la Depresión (HAM-D)'
	]
};

function esFechaISO(valor) {
	return /^\d{4}-\d{2}-\d{2}$/.test(valor);
}

function construirFechaLocal(valor) {
	const [year, month, day] = valor.split('-').map(Number);
	return new Date(year, month - 1, day);
}

function sumarDias(fecha, dias) {
	const copia = new Date(fecha);
	copia.setDate(copia.getDate() + dias);
	return copia;
}

function sumarMeses(fecha, meses) {
	const copia = new Date(fecha);
	copia.setMonth(copia.getMonth() + meses);
	return copia;
}

function normalizarNumero(valor) {
	const numero = Number(valor ?? 0);
	if (!Number.isFinite(numero)) return 0;
	return Math.round(numero * 100) / 100;
}

export function escapeCsvValue(valor) {
	const texto = String(valor ?? '');
	if (texto.includes('"') || texto.includes(',') || texto.includes('\n')) {
		return `"${texto.replaceAll('"', '""')}"`;
	}
	return texto;
}

export function validarRangoReporte(fechaInicio, fechaFin) {
	if (!esFechaISO(fechaInicio) || !esFechaISO(fechaFin)) {
		return {
			ok: false,
			error: 'Las fechas deben usar el formato YYYY-MM-DD.'
		};
	}

	const inicio = construirFechaLocal(fechaInicio);
	const fin = construirFechaLocal(fechaFin);

	if (Number.isNaN(inicio.getTime()) || Number.isNaN(fin.getTime())) {
		return {
			ok: false,
			error: 'Las fechas ingresadas no son válidas.'
		};
	}

	if (inicio > fin) {
		return {
			ok: false,
			error: 'La fecha de inicio no puede ser mayor que la fecha de fin.'
		};
	}

	const limiteMaximo = sumarMeses(inicio, 4);
	if (fin > limiteMaximo) {
		return {
			ok: false,
			error: 'El rango máximo permitido es de 4 meses.'
		};
	}

	return {
		ok: true,
		fechaInicio,
		fechaFin,
		inicio,
		fin,
		inicioTimestamp: `${fechaInicio} 00:00:00`,
		finExclusiveTimestamp: `${sumarDias(fin, 1).getFullYear()}-${String(sumarDias(fin, 1).getMonth() + 1).padStart(2, '0')}-${String(sumarDias(fin, 1).getDate()).padStart(2, '0')} 00:00:00`
	};
}

export function construirResumenPruebasRecomendadas(promediosPacientes = []) {
	const porPruebaMap = new Map();
	const pacientes = {
		depression: new Set(),
		anxiety: new Set()
	};

	for (const promedio of promediosPacientes) {
		const idPaciente = Number(promedio.id_paciente);
		const promedioDep = normalizarNumero(promedio.promedio_depresion);
		const promedioAnx = normalizarNumero(promedio.promedio_ansiedad);

		if (promedioDep >= UMBRAL_RECOMENDACION_PRUEBAS) {
			pacientes.depression.add(idPaciente);
			for (const prueba of PRUEBAS_RECOMENDADAS.depression) {
				porPruebaMap.set(prueba, {
					nombre: prueba,
					condicion: 'depression',
					total: (porPruebaMap.get(prueba)?.total ?? 0) + 1
				});
			}
		}

		if (promedioAnx >= UMBRAL_RECOMENDACION_PRUEBAS) {
			pacientes.anxiety.add(idPaciente);
			for (const prueba of PRUEBAS_RECOMENDADAS.anxiety) {
				porPruebaMap.set(prueba, {
					nombre: prueba,
					condicion: 'anxiety',
					total: (porPruebaMap.get(prueba)?.total ?? 0) + 1
				});
			}
		}
	}

	const porPrueba = Array.from(porPruebaMap.values()).sort((a, b) =>
		a.nombre.localeCompare(b.nombre, 'es')
	);

	const pacientesConRecomendacion = new Set([
		...pacientes.depression.values(),
		...pacientes.anxiety.values()
	]).size;

	const recomendacionesDep = pacientes.depression.size * PRUEBAS_RECOMENDADAS.depression.length;
	const recomendacionesAnx = pacientes.anxiety.size * PRUEBAS_RECOMENDADAS.anxiety.length;

	return {
		umbral_porcentaje: UMBRAL_RECOMENDACION_PRUEBAS,
		total_recomendaciones: recomendacionesDep + recomendacionesAnx,
		pacientes_con_recomendacion: pacientesConRecomendacion,
		por_condicion: {
			depression: {
				pacientes: pacientes.depression.size,
				recomendaciones: recomendacionesDep,
				pruebas: PRUEBAS_RECOMENDADAS.depression
			},
			anxiety: {
				pacientes: pacientes.anxiety.size,
				recomendaciones: recomendacionesAnx,
				pruebas: PRUEBAS_RECOMENDADAS.anxiety
			}
		},
		por_prueba: porPrueba
	};
}

export function generarCsvReporte(reporte) {
	const snapshot = reporte.indicadores_json ?? {};
	const metadata = snapshot.metadata ?? {};
	const totales = snapshot.totales ?? {};
	const pruebas = snapshot.pruebas_psicologicas_recomendadas ?? {};
	const porCondicion = pruebas.por_condicion ?? {};
	const porPrueba = pruebas.por_prueba ?? [];

	const filas = [
		['Seccion', 'Campo', 'Valor'],
		['metadata', 'id_reporte', reporte.id_reporte],
		['metadata', 'fecha_generacion', reporte.fecha_generacion],
		['metadata', 'usuario_solicitante', metadata.usuario_solicitante ?? ''],
		['metadata', 'fecha_inicio', reporte.fecha_inicio],
		['metadata', 'fecha_fin', reporte.fecha_fin],
		['totales', 'pacientes_atendidos', totales.pacientes_atendidos ?? 0],
		['totales', 'notas_analizadas', totales.notas_analizadas ?? 0],
		['totales', 'diagnosticos_sugeridos', totales.diagnosticos_sugeridos ?? 0],
		['totales', 'diagnosticos_aceptados', totales.diagnosticos_aceptados ?? 0],
		['totales', 'pruebas_psicologicas_recomendadas', pruebas.total_recomendaciones ?? 0],
		['pruebas_por_condicion', 'depression_pacientes', porCondicion.depression?.pacientes ?? 0],
		[
			'pruebas_por_condicion',
			'depression_recomendaciones',
			porCondicion.depression?.recomendaciones ?? 0
		],
		['pruebas_por_condicion', 'anxiety_pacientes', porCondicion.anxiety?.pacientes ?? 0],
		['pruebas_por_condicion', 'anxiety_recomendaciones', porCondicion.anxiety?.recomendaciones ?? 0]
	];

	for (const prueba of porPrueba) {
		filas.push(['pruebas_por_prueba', `${prueba.condicion}:${prueba.nombre}`, prueba.total]);
	}

	return filas.map((fila) => fila.map(escapeCsvValue).join(',')).join('\n');
}
