import { json } from '@sveltejs/kit';
import sql from '$lib/server/db/client.js';
import bcrypt from 'bcrypt';

/**
 * POST /api/pacientes/cambiar-password
 * Cambiar contraseña del paciente autenticado
 */
export async function POST({ request, cookies }) {
	try {
		// Obtener sesión del paciente
		const sessionCookie = cookies.get('session-paciente');

		if (!sessionCookie) {
			return json(
				{ success: false, error: 'No autenticado' },
				{ status: 401 }
			);
		}

		const sessionData = JSON.parse(sessionCookie);
		const id_paciente = sessionData.id_paciente;

		// Obtener datos del body
		const { passwordNueva } = await request.json();

		if (!passwordNueva || passwordNueva.length < 6) {
			return json(
				{ success: false, error: 'La contraseña debe tener al menos 6 caracteres' },
				{ status: 400 }
			);
		}

		// Hashear nueva contraseña
		const saltRounds = 10;
		const nuevoHash = await bcrypt.hash(passwordNueva, saltRounds);

		// Actualizar contraseña
		await sql`
			UPDATE paciente
			SET password_hash = ${nuevoHash}
			WHERE id_paciente = ${id_paciente}
		`;

		console.log('✅ Contraseña cambiada correctamente');
		return json({ success: true, message: 'Contraseña actualizada correctamente' });
	} catch (error) {
		console.error('❌ Error en POST /api/pacientes/cambiar-password:', error);
		return json(
			{ success: false, error: 'Error al cambiar contraseña' },
			{ status: 500 }
		);
	}
}
