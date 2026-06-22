import { json } from '@sveltejs/kit';

/**
 * POST /api/auth/logout-paciente
 * Cerrar sesión de paciente
 */
export async function POST({ cookies }) {
	// Eliminar cookie de sesión de paciente
	cookies.delete('session-paciente', {
		path: '/',
		httpOnly: true,
		secure: process.env.COOKIE_SECURE === 'true',
		sameSite: 'strict'
	});

	return json({
		success: true,
		message: 'Sesión cerrada correctamente'
	});
}
