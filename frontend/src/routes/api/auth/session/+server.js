import { json } from '@sveltejs/kit';
import * as authService from '$lib/server/services/auth.js';

/**
 * GET /api/auth/session
 * Verificar sesión actual
 */
export async function GET({ cookies }) {
	try {
		const sessionCookie = cookies.get('session');

		if (!sessionCookie) {
			return json(
				{
					success: false,
					error: 'No hay sesión activa'
				},
				{ status: 401 }
			);
		}

		const sessionData = JSON.parse(sessionCookie);

		// Verificar expiración de sesión (30 minutos de inactividad)
		const loginTime = sessionData.loginTime || Date.now();
		const now = Date.now();
		const minutosTranscurridos = (now - loginTime) / 1000 / 60;

		if (minutosTranscurridos > 30) {
			// Sesión expirada
			cookies.delete('session', { path: '/' });
			return json(
				{
					success: false,
					error: 'Sesión expirada. Por favor, inicie sesión nuevamente'
				},
				{ status: 401 }
			);
		}

		// Verificar que el usuario sigue activo en la base de datos
		const user = await authService.getEspecialistaByIdForAuth(sessionData.id_especialista);

		if (!user) {
			cookies.delete('session', { path: '/' });
			return json(
				{
					success: false,
					error: 'Usuario no encontrado o desactivado'
				},
				{ status: 401 }
			);
		}

		// Renovar cookie (actualizar maxAge)
		sessionData.loginTime = now; // Actualizar tiempo de actividad
		cookies.set('session', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.COOKIE_SECURE === 'true',
			sameSite: 'strict',
			maxAge: 60 * 30 // 30 minutos en segundos
		});

		return json({
			success: true,
			user: user
		});
	} catch (error) {
		console.error('Error verificando sesión:', error);
		return json(
			{
				success: false,
				error: 'Error al verificar sesión',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
