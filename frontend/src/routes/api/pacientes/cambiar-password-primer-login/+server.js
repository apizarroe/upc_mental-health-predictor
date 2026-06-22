import { json } from '@sveltejs/kit';
import { cambiarPasswordPacientePrimerLogin } from '$lib/server/services/auth-paciente.js';

export async function POST({ request, cookies }) {
	// Obtener datos de sesión desde la cookie de paciente
	const sessionCookie = cookies.get('session-paciente');

	if (!sessionCookie) {
		return json({ error: 'No autorizado' }, { status: 401 });
	}

	let sessionData;
	try {
		sessionData = JSON.parse(sessionCookie);
	} catch (parseError) {
		return json({ error: 'Sesión inválida' }, { status: 401 });
	}

	if (!sessionData.id_paciente) {
		return json({ error: 'No autorizado' }, { status: 401 });
	}

	try {
		const { passwordNueva } = await request.json();

		// Validar que se envió la contraseña nueva
		if (!passwordNueva) {
			return json({ error: 'La nueva contraseña es requerida' }, { status: 400 });
		}

		// Validar formato de contraseña
		if (passwordNueva.length < 8) {
			return json(
				{ error: 'La contraseña debe tener al menos 8 caracteres' },
				{ status: 400 }
			);
		}

		if (!/[A-Z]/.test(passwordNueva)) {
			return json(
				{ error: 'La contraseña debe contener al menos una letra mayúscula' },
				{ status: 400 }
			);
		}

		if (!/[a-z]/.test(passwordNueva)) {
			return json(
				{ error: 'La contraseña debe contener al menos una letra minúscula' },
				{ status: 400 }
			);
		}

		if (!/[0-9]/.test(passwordNueva)) {
			return json({ error: 'La contraseña debe contener al menos un número' }, { status: 400 });
		}

		// Cambiar contraseña
		const result = await cambiarPasswordPacientePrimerLogin(sessionData.id_paciente, passwordNueva);

		if (!result.success) {
			return json({ error: result.error }, { status: 400 });
		}

		// Actualizar la cookie de sesión para quitar el flag de cambio obligatorio
		sessionData.requiere_cambio_password = false;
		cookies.set('session-paciente', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.COOKIE_SECURE === 'true',
			sameSite: 'strict',
			maxAge: 60 * 30
		});

		return json({ message: result.message });
	} catch (error) {
		console.error('Error en cambiar-password-primer-login (paciente):', error);
		return json({ error: 'Error al cambiar la contraseña' }, { status: 500 });
	}
}
