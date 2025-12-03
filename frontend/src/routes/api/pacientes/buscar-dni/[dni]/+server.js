import { json } from '@sveltejs/kit';
import sql from '$lib/server/db/client.js';
import * as historiasService from '$lib/server/services/historias.js';

export async function GET({ params }) {
	try {
		const { dni } = params;

		// Buscar paciente por DNI
		const [paciente] = await sql`
			SELECT * FROM paciente
			WHERE dni = ${dni}
			AND flg_activo = true
		`;

		if (!paciente) {
			return json({
				success: false,
				error: 'No se encontró ningún paciente con ese DNI'
			}, { status: 404 });
		}

		// Verificar si ya tiene una historia clínica activa
		const historiaExistente = await historiasService.getHistoriaByPacienteId(paciente.id_paciente);

		return json({
			success: true,
			data: {
				paciente,
				tiene_historia_activa: !!historiaExistente,
				historia_existente: historiaExistente || null
			}
		});
	} catch (error) {
		console.error('Error al buscar paciente por DNI:', error);
		return json({
			success: false,
			error: 'Error al buscar paciente'
		}, { status: 500 });
	}
}
