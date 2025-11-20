import { json } from '@sveltejs/kit';
import { cambiarPasswordSchema } from '$lib/server/validators/auth.js';
import * as authService from '$lib/server/services/auth.js';

/**
 * POST /api/auth/cambiar-password
 * Cambiar contraseña (funciona para especialistas y pacientes)
 */
export async function POST({ request, cookies }) {
	try {
		// Verificar sesión activa
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
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = cambiarPasswordSchema.parse(body);

		// Cambiar contraseña usando el servicio unificado
		const result = await authService.cambiarPassword(
			sessionData.user_id,
			sessionData.user_type,
			validatedData.passwordActual,
			validatedData.passwordNueva
		);

		if (!result.success) {
			return json(
				{
					success: false,
					error: result.error
				},
				{ status: 400 }
			);
		}

		return json({
			success: true,
			message: result.message
		});
	} catch (error) {
		// Error de validación de Zod
		if (error.name === 'ZodError') {
			return json(
				{
					success: false,
					error: 'Datos inválidos',
					details: error.errors
				},
				{ status: 400 }
			);
		}

		// Otros errores
		console.error('Error cambiando contraseña:', error);
		return json(
			{
				success: false,
				error: 'Error al cambiar contraseña',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
