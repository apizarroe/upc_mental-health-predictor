import { json } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as mlService from '$lib/server/services/ml-prediccion.js';

/**
 * POST /api/respuestas/[idRespuesta]/reprocesar
 * Reprocesa una respuesta del paciente enviándola nuevamente al modelo ML
 * Solo accesible para especialistas y administradores
 *
 * Este endpoint es SÍNCRONO: espera a que el ML procese y devuelve el resultado
 */
export async function POST({ params, cookies }) {
	try {
		const { idRespuesta } = params;

		// Verificar sesión de especialista
		const sessionCookie = cookies.get('session');
		if (!sessionCookie) {
			return json({ error: 'No autorizado' }, { status: 401 });
		}

		const sessionData = JSON.parse(sessionCookie);
		if (!sessionData.rol || (sessionData.rol !== 'admin' && sessionData.rol !== 'especialista')) {
			return json({
				error: 'Acceso denegado. Solo especialistas y administradores pueden reprocesar respuestas.'
			}, { status: 403 });
		}

		console.log(`🔄 Reprocesando respuesta ID: ${idRespuesta}`);
		console.log(`   Solicitado por: ${sessionData.usuario || sessionData.nombres} (${sessionData.rol})`);

		// 1. Obtener la respuesta existente
		const respuesta = await respuestasService.getRespuestaById(parseInt(idRespuesta));
		if (!respuesta) {
			return json({ error: 'Respuesta no encontrada' }, { status: 404 });
		}

		console.log(`   Paciente ID: ${respuesta.id_paciente}`);
		console.log(`   Estado actual: ${respuesta.estado_procesamiento}`);

		// 2. Reprocesar con ML (síncrono - esperamos el resultado)
		const result = await mlService.reprocesarRespuestaConML(
			parseInt(idRespuesta),
			respuesta.respuestas,
			sessionData
		);

		if (result.success) {
			console.log(`✅ Respuesta reprocesada exitosamente. Nueva evaluación ID: ${result.evaluacion.id_evaluacion}`);

			return json({
				success: true,
				message: 'Respuesta reprocesada exitosamente',
				evaluacion: result.evaluacion
			});
		} else {
			return json({
				success: false,
				error: 'Error al reprocesar la respuesta',
				details: result.error
			}, { status: 500 });
		}

	} catch (error) {
		console.error('❌ Error al reprocesar respuesta:', error);
		return json({
			success: false,
			error: 'Error interno al reprocesar la respuesta',
			details: error.message
		}, { status: 500 });
	}
}
