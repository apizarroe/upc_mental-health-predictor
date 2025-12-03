import { error, redirect } from '@sveltejs/kit';
import { canUpdatePacientes } from '$lib/utils/permissions.js';

export async function load({ params, fetch, parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para editar pacientes
	if (!canUpdatePacientes(user.rol)) {
		// Redirigir a la lista de pacientes si no tiene permiso
		throw redirect(303, '/pacientes');
	}

	try {
		const response = await fetch(`/api/pacientes/${params.id}`);
		const result = await response.json();

		if (!result.success) {
			throw error(404, result.error || 'Paciente no encontrado');
		}

		return {
			paciente: result.data
		};
	} catch (err) {
		if (err.status === 303) {
			throw err; // Re-throw redirect
		}
		throw error(500, 'Error al cargar datos del paciente');
	}
}
