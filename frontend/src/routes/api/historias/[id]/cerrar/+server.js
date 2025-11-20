import { json } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';
import { cerrarHistoriaSchema } from '$lib/server/validators/historia.js';

export async function POST({ params, request, cookies }) {
	try {
		const body = await request.json();

		// Obtener especialista de la sesión
		const sessionCookie = cookies.get('session');
		if (!sessionCookie) {
			return json({ success: false, error: 'No hay sesión activa' }, { status: 401 });
		}

		const sessionData = JSON.parse(sessionCookie);

		// Validar datos
		const validatedData = cerrarHistoriaSchema.parse(body);

		const historia = await historiasService.cerrarHistoria(
			params.id,
			validatedData.motivo_cierre,
			sessionData.user_id
		);

		if (!historia) {
			return json({ success: false, error: 'Historia clínica no encontrada' }, { status: 404 });
		}

		return json({ success: true, data: historia });
	} catch (error) {
		if (error.name === 'ZodError') {
			return json({
				success: false,
				error: 'Datos inválidos',
				details: error.errors
			}, { status: 400 });
		}

		console.error('Error al cerrar historia:', error);
		return json({ success: false, error: 'Error al cerrar historia clínica' }, { status: 500 });
	}
}
