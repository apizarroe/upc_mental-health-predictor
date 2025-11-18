import { error, redirect } from '@sveltejs/kit';
import { canAccessPacientes } from '$lib/utils/permissions.js';
import * as historiasService from '$lib/server/services/historias.js';

export async function load({ params, fetch, parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para ver pacientes
	if (!canAccessPacientes(user.rol)) {
		// Redirigir a la lista de pacientes si no tiene permiso
		throw redirect(303, '/pacientes');
	}

	try {
		const response = await fetch(`/api/pacientes/${params.id}`);
		const result = await response.json();

		if (!result.success) {
			throw error(404, result.error || 'Paciente no encontrado');
		}

		// Verificar si el paciente tiene historia clínica activa
		const historiaClinica = await historiasService.getHistoriaByPacienteId(params.id);

		return {
			paciente: result.data,
			tieneHistoria: !!historiaClinica
		};
	} catch (err) {
		if (err.status === 303 || err.status === 404) {
			throw err;
		}
		throw error(500, 'Error al cargar datos del paciente');
	}
}
