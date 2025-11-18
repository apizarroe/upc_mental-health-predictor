import { redirect } from '@sveltejs/kit';
import { canCreateEspecialistas } from '$lib/utils/permissions.js';

/**
 * Verificar permisos antes de mostrar la página de crear especialista
 */
export async function load({ parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para crear especialistas
	if (!canCreateEspecialistas(user.rol)) {
		// Redirigir al dashboard si no tiene permiso
		throw redirect(303, '/');
	}

	return {};
}
