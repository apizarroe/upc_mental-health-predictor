import { json } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';

/**
 * POST /api/respuestas/[idRespuesta]/observaciones
 * Reemplaza las observaciones de una respuesta
 * Solo accesible para especialistas y administradores
 */
export async function POST({ params, request, cookies }) {
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
						'Acceso denegado. Solo especialistas y administradores pueden editar observaciones.'
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

		const body = await request.json();
		const observaciones = Array.isArray(body?.observaciones) ? body.observaciones : null;

		if (
			!observaciones ||
			observaciones.some(
				(item) => typeof item !== 'object' || typeof item.descripcion !== 'string'
			)
		) {
			return json({ error: 'Formato de observaciones inválido' }, { status: 400 });
		}

		const idEspecialista = sessionData.id_especialista ? parseInt(sessionData.id_especialista) : null;

		await respuestasService.replaceObservacionesByRespuesta(idRespuesta, observaciones, idEspecialista);

		const observacionesGuardadas = await respuestasService.getObservacionesByRespuesta(idRespuesta);

		return json({
			success: true,
			observaciones: observacionesGuardadas
		});
	} catch (error) {
		if (error.message === 'LIMITE_OBSERVACIONES') {
			return json({ error: 'No se pueden registrar más de 3 observaciones por nota.' }, { status: 422 });
		}
		console.error('❌ Error al guardar observaciones:', error);
		return json(
			{ error: 'Error interno al guardar observaciones', details: error.message },
			{ status: 500 }
		);
	}
}
