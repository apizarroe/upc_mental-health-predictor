import * as authService from '$lib/server/services/auth.js';

/**
 * Middleware global de SvelteKit
 * Se ejecuta en cada request del servidor
 * Pobla event.locals.user con datos del usuario autenticado
 */
export async function handle({ event, resolve }) {
	// Leer cookie de sesión
	const sessionCookie = event.cookies.get('session');

	if (sessionCookie) {
		try {
			const sessionData = JSON.parse(sessionCookie);

			// Verificar expiración (30 minutos)
			const loginTime = sessionData.loginTime || Date.now();
			const now = Date.now();
			const minutosTranscurridos = (now - loginTime) / 1000 / 60;

			if (minutosTranscurridos <= 30) {
				// Sesión válida - obtener datos del usuario
				const user = await authService.getUserByIdForAuth(
					sessionData.user_id,
					sessionData.user_type
				);

				if (user) {
					// Poblar locals.user para que esté disponible en todos los endpoints
					event.locals.user = user;

					// Renovar sesión actualizando el loginTime
					sessionData.loginTime = now;
					event.cookies.set('session', JSON.stringify(sessionData), {
						path: '/',
						httpOnly: true,
						secure: process.env.NODE_ENV === 'production',
						sameSite: 'strict',
						maxAge: 60 * 30 // 30 minutos
					});
				} else {
					// Usuario no encontrado o inactivo - eliminar sesión
					event.cookies.delete('session', { path: '/' });
				}
			} else {
				// Sesión expirada - eliminar cookie
				event.cookies.delete('session', { path: '/' });
			}
		} catch (error) {
			// Error parseando sesión - eliminar cookie corrupta
			console.error('Error en hooks.server.js:', error);
			event.cookies.delete('session', { path: '/' });
		}
	}

	// Continuar con el request
	const response = await resolve(event);
	return response;
}
