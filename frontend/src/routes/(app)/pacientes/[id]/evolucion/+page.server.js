import { error } from '@sveltejs/kit';
import * as pacientesService from '$lib/server/services/pacientes.js';
import * as respuestasService from '$lib/server/services/respuestas.js';

export async function load({ params }) {
	const idPaciente = parseInt(params.id);

	const paciente = await pacientesService.getPacienteById(idPaciente);
	if (!paciente) {
		throw error(404, 'Paciente no encontrado');
	}

	const evolucion = await respuestasService.getEvolucionByPaciente(idPaciente, 30);

	return { paciente, evolucion };
}
