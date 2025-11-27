import { redirect } from '@sveltejs/kit';
import * as authService from '$lib/server/services/auth.js';

/**
 * Hook que verifica autenticación en todas las rutas protegidas (app)
 * Este layout envuelve todas las páginas que requieren autenticación
 */
export async function load({ cookies }) {
	const sessionCookie = cookies.get('session');

	// Si no hay cookie de sesión, redirigir a login de especialistas
	if (!sessionCookie) {
		throw redirect(303, '/login/especialista');
	}

	try {
		const sessionData = JSON.parse(sessionCookie);

		// Verificar expiración de sesión (30 minutos)
		const loginTime = sessionData.loginTime || Date.now();
		const now = Date.now();
		const minutosTranscurridos = (now - loginTime) / 1000 / 60;

		if (minutosTranscurridos > 30) {
			// Sesión expirada
			cookies.delete('session', { path: '/' });
			throw redirect(303, '/login/especialista?expired=true');
		}

		// Verificar que el usuario sigue activo
		const user = await authService.getEspecialistaByIdForAuth(sessionData.id_especialista);

		if (!user) {
			cookies.delete('session', { path: '/' });
			throw redirect(303, '/login/especialista?invalid=true');
		}

		// Renovar sesión actualizando el tiempo de actividad
		sessionData.loginTime = now;
		cookies.set('session', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.NODE_ENV === 'production',
			sameSite: 'strict',
			maxAge: 60 * 30 // 30 minutos
		});

		// Pasar datos del usuario a todas las páginas protegidas
		return {
			user: user,
			requiere_cambio_password: sessionData.requiere_cambio_password || false
		};
	} catch (error) {
		// Si hay error parseando la sesión, eliminar cookie y redirigir
		if (error.status === 303) {
			throw error; // Re-throw redirect
		}
		cookies.delete('session', { path: '/' });
		throw redirect(303, '/login/especialista');
	}
}
