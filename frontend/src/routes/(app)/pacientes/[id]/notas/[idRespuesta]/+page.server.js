import { error } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as pacientesService from '$lib/server/services/pacientes.js';

export async function load({ params, parent }) {
	const { user } = await parent();
	const idPaciente = parseInt(params.id);
	const idRespuesta = parseInt(params.idRespuesta);

	// Verificar que el paciente existe
	const paciente = await pacientesService.getPacienteById(idPaciente);
	if (!paciente) {
		throw error(404, 'Paciente no encontrado');
	}

	// Obtener detalle completo de la respuesta con evaluación ML
	const respuesta = await respuestasService.getRespuestaDetalle(idRespuesta);
	if (!respuesta) {
		throw error(404, 'Respuesta no encontrada');
	}

	const observaciones = await respuestasService.getObservacionesByRespuesta(idRespuesta);

	return {
		paciente,
		respuesta,
		observaciones,
		currentUserId: user?.id_especialista ?? null
	};
}
