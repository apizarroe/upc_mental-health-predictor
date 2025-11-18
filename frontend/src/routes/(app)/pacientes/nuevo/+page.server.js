import { redirect } from '@sveltejs/kit';
import { canCreatePacientes } from '$lib/utils/permissions.js';

/**
 * Verificar permisos antes de mostrar la página de crear paciente
 */
export async function load({ parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para crear pacientes
	if (!canCreatePacientes(user.rol)) {
		// Redirigir a la lista de pacientes si no tiene permiso
		throw redirect(303, '/pacientes');
	}

	return {};
}
