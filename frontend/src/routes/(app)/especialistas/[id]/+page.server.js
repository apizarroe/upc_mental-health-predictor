import { error, redirect } from '@sveltejs/kit';
import { canUpdateEspecialistas } from '$lib/utils/permissions.js';

export async function load({ params, fetch, parent }) {
	const { user } = await parent();

	// Verificar si el usuario tiene permiso para editar especialistas
	if (!canUpdateEspecialistas(user.rol)) {
		// Redirigir al dashboard si no tiene permiso
		throw redirect(303, '/');
	}

	try {
		const response = await fetch(`/api/especialistas/${params.id}`);
		const result = await response.json();

		if (!result.success) {
			throw error(404, result.error || 'Especialista no encontrado');
		}

		return {
			especialista: result.data
		};
	} catch (err) {
		if (err.status === 303) {
			throw err; // Re-throw redirect
		}
		throw error(500, 'Error al cargar datos del especialista');
	}
}
