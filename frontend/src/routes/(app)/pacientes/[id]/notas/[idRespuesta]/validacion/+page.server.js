import { error } from '@sveltejs/kit';
import * as pacientesService from '$lib/server/services/pacientes.js';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as validacionesService from '$lib/server/services/validaciones.js';

export async function load({ params, parent }) {
	const { user } = await parent();

	const idPaciente = Number.parseInt(params.id, 10);
	const idRespuesta = Number.parseInt(params.idRespuesta, 10);

	const paciente = await pacientesService.getPacienteById(idPaciente);
	if (!paciente) {
		throw error(404, 'Paciente no encontrado');
	}

	const respuesta = await respuestasService.getRespuestaDetalle(idRespuesta);
	if (!respuesta) {
		throw error(404, 'Respuesta no encontrada');
	}

	if (!respuesta.id_evaluacion || !respuesta.trastornos_detectados) {
		throw error(409, 'La respuesta todavía no cuenta con un diagnóstico ML para validar.');
	}

	const validacionActual = await validacionesService.getValidacionByEvaluacionAndEspecialista(
		respuesta.id_evaluacion,
		user.id_especialista
	);

	return {
		user,
		paciente,
		respuesta,
		validacionActual,
		diagnosticoModelo: validacionesService.getDiagnosticoModelo(respuesta.trastornos_detectados)
	};
}
