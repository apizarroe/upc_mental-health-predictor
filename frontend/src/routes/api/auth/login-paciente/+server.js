import { json } from '@sveltejs/kit';
import { loginPacienteSchema } from '$lib/server/validators/auth-paciente.js';
import * as authPacienteService from '$lib/server/services/auth-paciente.js';

/**
 * POST /api/auth/login-paciente
 * Iniciar sesión como paciente usando DNI
 */
export async function POST({ request, cookies }) {
	try {
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = loginPacienteSchema.parse(body);

		// Intentar login de paciente
		const result = await authPacienteService.loginPaciente(
			validatedData.dni,
			validatedData.password
		);

		if (!result.success) {
			return json(
				{
					success: false,
					error: result.error
				},
				{ status: 401 }
			);
		}

		// Login exitoso: crear sesión con cookie separada para pacientes
		// La cookie expira en 30 minutos (política de seguridad)
		const sessionData = {
			id_paciente: result.user.id_paciente,
			dni: result.user.dni,
			tipo_usuario: 'paciente',
			loginTime: Date.now()
		};

		cookies.set('session-paciente', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.NODE_ENV === 'production',
			sameSite: 'strict',
			maxAge: 60 * 30 // 30 minutos en segundos
		});

		return json({
			success: true,
			user: result.user,
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
		console.error('Error en login de paciente:', error);
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
