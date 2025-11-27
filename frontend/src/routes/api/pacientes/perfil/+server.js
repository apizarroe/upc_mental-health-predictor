import { json } from '@sveltejs/kit';
import * as pacientesService from '$lib/server/services/pacientes.js';

/**
 * PUT /api/pacientes/perfil
 * Actualizar perfil del paciente autenticado
 */
export async function PUT({ request, cookies }) {
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
		const data = await request.json();
		console.log('📝 Datos recibidos para actualizar perfil:', data);

		// Actualizar paciente
		const paciente = await pacientesService.updatePaciente(id_paciente, data);

		if (paciente) {
			console.log('✅ Perfil actualizado correctamente');
			return json({ success: true });
		} else {
			console.error('❌ No se pudo actualizar el perfil');
			return json(
				{ success: false, error: 'No se pudo actualizar el perfil' },
				{ status: 400 }
			);
		}
	} catch (error) {
		console.error('❌ Error en PUT /api/pacientes/perfil:', error);
		return json(
			{ success: false, error: 'Error al actualizar perfil' },
			{ status: 500 }
		);
	}
}
