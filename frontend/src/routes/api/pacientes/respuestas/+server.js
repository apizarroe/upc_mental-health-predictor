import { json } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as mlService from '$lib/server/services/ml-prediccion.js';
import { pacienteRespuestaSchema } from '$lib/server/validators/respuesta.js';

/**
 * POST /api/pacientes/respuestas
 * Crear una nueva respuesta del paciente al cuestionario diario
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
		const id_paciente = parseInt(sessionData.id_paciente);

		// Verificar si ya respondió 2 veces hoy (GMT-5 Lima/Peru)
		const yaRespondio = await respuestasService.yaRespondioDobleHoy(id_paciente);

		if (yaRespondio) {
			return json(
				{
					success: false,
					error: 'Ya has completado el cuestionario 2 veces hoy. Puedes volver a responder mañana.'
				},
				{ status: 400 }
			);
		}

		// Obtener datos del body
		const data = await request.json();

		// Validar datos con Zod
		const validatedData = pacienteRespuestaSchema.parse({
			id_paciente,
			respuestas: data.respuestas
		});

		// Crear respuesta
		const respuesta = await respuestasService.createRespuesta(validatedData);

		if (respuesta) {
			console.log('✅ Respuesta guardada correctamente:', respuesta.id_respuesta);

			// Procesar con ML en segundo plano (no bloqueante)
			// Si falla el ML, la respuesta ya está guardada
			mlService.procesarRespuestaConML(respuesta.id_respuesta, validatedData.respuestas)
				.then(result => {
					if (result.success) {
						console.log('✅ ML procesado en segundo plano exitosamente');
					} else {
						console.warn('⚠️ ML falló, pero respuesta fue guardada:', result.error);
					}
				})
				.catch(error => {
					console.error('⚠️ Error procesando ML en segundo plano:', error);
				});

			return json({
				success: true,
				id_respuesta: respuesta.id_respuesta,
				message: 'Tus respuestas han sido guardadas correctamente'
			});
		} else {
			console.error('❌ No se pudo guardar la respuesta');
			return json(
				{ success: false, error: 'No se pudo guardar la respuesta' },
				{ status: 400 }
			);
		}
	} catch (error) {
		console.error('❌ Error en POST /api/pacientes/respuestas:', error);

		// Errores de validación de Zod
		if (error.name === 'ZodError') {
			return json(
				{
					success: false,
					error: 'Datos inválidos',
					details: error.errors
				},
				{ status: 400 }
			);
		}

		return json(
			{ success: false, error: 'Error al guardar la respuesta' },
			{ status: 500 }
		);
	}
}

/**
 * GET /api/pacientes/respuestas
 * Obtener historial de respuestas del paciente autenticado
 */
export async function GET({ cookies, url }) {
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
		const id_paciente = parseInt(sessionData.id_paciente);

		// Obtener parámetros de paginación
		const limite = parseInt(url.searchParams.get('limite') || '10');
		const offset = parseInt(url.searchParams.get('offset') || '0');

		// Obtener respuestas con paginación
		const respuestas = await respuestasService.getRespuestasPaginadas(id_paciente, limite, offset);
		const total = await respuestasService.contarRespuestas(id_paciente);

		return json({
			success: true,
			respuestas,
			total,
			limite,
			offset
		});
	} catch (error) {
		console.error('❌ Error en GET /api/pacientes/respuestas:', error);
		return json(
			{ success: false, error: 'Error al obtener respuestas' },
			{ status: 500 }
		);
	}
}
