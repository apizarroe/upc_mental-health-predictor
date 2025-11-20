import { redirect } from '@sveltejs/kit';

/**
 * Hook que verifica autenticación en todas las rutas protegidas (app)
 * Este layout envuelve todas las páginas que requieren autenticación
 * Ahora usa event.locals.user poblado por hooks.server.js
 */
export async function load({ locals }) {
	// El middleware en hooks.server.js ya pobló locals.user
	// Si no hay user, significa que no hay sesión válida
	if (!locals.user) {
		throw redirect(303, '/login');
	}

	// Pasar datos del usuario a todas las páginas protegidas
	return {
		user: locals.user
	};
}
