import { json } from '@sveltejs/kit';
import { loginSchema } from '$lib/server/validators/auth.js';
import * as authService from '$lib/server/services/auth.js';

/**
 * POST /api/auth/login
 * Iniciar sesión
 */
export async function POST({ request, cookies }) {
	try {
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = loginSchema.parse(body);

		// Intentar login
		const result = await authService.login(validatedData.usuario, validatedData.password);

		if (!result.success) {
			return json(
				{
					success: false,
					error: result.error
				},
				{ status: 401 }
			);
		}

		// Login exitoso: crear sesión con cookie
		// La cookie expira en 30 minutos (política de seguridad)
		const sessionData = {
			id_especialista: result.user.id_especialista,
			usuario: result.user.usuario,
			rol: result.user.rol,
			loginTime: Date.now(),
			requiere_cambio_password: result.requiere_cambio_password || false
		};

		cookies.set('session', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.NODE_ENV === 'production',
			sameSite: 'strict',
			maxAge: 60 * 30 // 30 minutos en segundos
		});

		return json({
			success: true,
			user: result.user,
			requiere_cambio_password: result.requiere_cambio_password || false,
			message: 'Inicio de sesión exitoso'
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
		console.error('Error en login:', error);
		return json(
			{
				success: false,
				error: 'Error al iniciar sesión',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
