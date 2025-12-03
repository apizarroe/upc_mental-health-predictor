import { error } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as pacientesService from '$lib/server/services/pacientes.js';

export async function load({ params }) {
	const idPaciente = parseInt(params.id);

	// Verificar que el paciente existe
	const paciente = await pacientesService.getPacienteById(idPaciente);
	if (!paciente) {
		throw error(404, 'Paciente no encontrado');
	}

	// Obtener respuestas del paciente con paginación
	const limite = 20;
	const offset = 0;

	const respuestas = await respuestasService.getRespuestasPaginadas(idPaciente, limite, offset);
	const total = await respuestasService.contarRespuestas(idPaciente);

	return {
		paciente,
		respuestas,
		total,
		limite
	};
}
