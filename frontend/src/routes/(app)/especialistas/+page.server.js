import { redirect } from '@sveltejs/kit';
import { canAccessEspecialistas } from '$lib/utils/permissions.js';

/**
 * Verificar permisos antes de mostrar la lista de especialistas
 * Solo los administradores pueden acceder al módulo de especialistas
 */
export async function load({ parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para ver especialistas
	if (!canAccessEspecialistas(user.rol)) {
		// Redirigir al dashboard si no tiene permiso
		throw redirect(303, '/');
	}

	return {};
}
