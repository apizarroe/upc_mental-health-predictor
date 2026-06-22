import { json } from '@sveltejs/kit';

/**
 * POST /api/auth/logout
 * Cerrar sesión
 */
export async function POST({ cookies }) {
	try {
		// Eliminar cookie de sesión
		cookies.delete('session', {
			path: '/',
			httpOnly: true,
			secure: process.env.COOKIE_SECURE === 'true',
			sameSite: 'strict'
		});

		return json({
			success: true,
			message: 'Sesión cerrada exitosamente'
		});
	} catch (error) {
		console.error('Error en logout:', error);
		return json(
			{
				success: false,
				error: 'Error al cerrar sesión',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
