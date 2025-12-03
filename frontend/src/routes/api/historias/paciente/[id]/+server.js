import { json } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';

/**
 * GET /api/historias/paciente/[id]
 * Obtener la historia clínica de un paciente por su ID
 */
export async function GET({ params }) {
	try {
		const { id } = params;
		const historia = await historiasService.getHistoriaByPacienteId(id);

		if (!historia) {
			return json({
				success: false,
				data: null,
				message: 'El paciente no tiene historia clínica'
			});
		}

		return json({
			success: true,
			data: historia
		});
	} catch (error) {
		console.error('Error al obtener historia clínica del paciente:', error);
		return json(
			{
				success: false,
				error: 'Error al obtener historia clínica',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
