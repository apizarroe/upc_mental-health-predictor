import { json } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';

/**
 * POST /api/respuestas/[idRespuesta]/riesgo-atendido
 * Marca una nota diaria como atendida respecto a las señales de riesgo detectadas.
 * El valor nace en NULL y solo puede pasar a TRUE (no existe estado FALSE).
 * Solo accesible para especialistas y administradores.
 */
export async function POST({ params, cookies }) {
	try {
		const sessionCookie = cookies.get('session');
		if (!sessionCookie) {
			return json({ error: 'No autorizado' }, { status: 401 });
		}

		const sessionData = JSON.parse(sessionCookie);
		if (!sessionData.rol || (sessionData.rol !== 'admin' && sessionData.rol !== 'especialista')) {
			return json(
				{
					error:
						'Acceso denegado. Solo especialistas y administradores pueden marcar el riesgo como atendido.'
				},
				{ status: 403 }
			);
		}

		const idRespuesta = parseInt(params.idRespuesta);
		if (Number.isNaN(idRespuesta)) {
			return json({ error: 'ID de respuesta inválido' }, { status: 400 });
		}

		const respuesta = await respuestasService.getRespuestaById(idRespuesta);
		if (!respuesta) {
			return json({ error: 'Respuesta no encontrada' }, { status: 404 });
		}

		const observaciones = await respuestasService.getObservacionesByRespuesta(idRespuesta);
		if (observaciones.length === 0) {
			return json(
				{ error: 'Debes registrar al menos una observación antes de marcar esta acción.' },
				{ status: 422 }
			);
		}

		const actualizada = await respuestasService.marcarRiesgoAtendido(idRespuesta);

		return json({
			success: true,
			riesgo_atendido: actualizada.riesgo_atendido === true
		});
	} catch (error) {
		console.error('❌ Error al marcar riesgo atendido:', error);
		return json(
			{ error: 'Error interno al marcar el riesgo como atendido', details: error.message },
			{ status: 500 }
		);
	}
}
