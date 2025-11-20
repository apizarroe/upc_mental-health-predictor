import { json } from '@sveltejs/kit';
import * as notasService from '$lib/server/services/notas.js';
import { canAccessOwnData } from '$lib/utils/permissions.js';

/**
 * GET /api/notas/grouped?id_paciente=123
 * Obtener notas agrupadas por fecha
 */
export async function GET({ url, locals }) {
	const user = locals.user;

	if (!user) {
		return json({ success: false, error: 'No autenticado' }, { status: 401 });
	}

	const idPaciente = parseInt(url.searchParams.get('id_paciente'));

	if (!idPaciente) {
		return json({ success: false, error: 'ID de paciente requerido' }, { status: 400 });
	}

	// Verificar permisos
	if (!canAccessOwnData(user, idPaciente)) {
		return json({ success: false, error: 'No tiene permisos para ver estas notas', user, idPaciente }, { status: 403 });
	}

	try {
		const notasGrouped = await notasService.getNotasGroupedByDate(idPaciente);

		return json({
			success: true,
			data: notasGrouped
		});
	} catch (error) {
		console.error('Error al obtener notas agrupadas:', error);
		return json({ success: false, error: 'Error al obtener notas' }, { status: 500 });
	}
}
