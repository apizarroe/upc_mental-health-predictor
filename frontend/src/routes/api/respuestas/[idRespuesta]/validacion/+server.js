import { json } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as validacionesService from '$lib/server/services/validaciones.js';
import { saveValidacionSchema } from '$lib/server/validators/validacion.js';

function getSessionData(cookies) {
	const sessionCookie = cookies.get('session');
	return sessionCookie ? JSON.parse(sessionCookie) : null;
}

export async function POST({ params, request, cookies }) {
	try {
		const sessionData = getSessionData(cookies);
		if (!sessionData) {
			return json({ success: false, error: 'No autorizado' }, { status: 401 });
		}

		if (!sessionData.rol || (sessionData.rol !== 'admin' && sessionData.rol !== 'especialista')) {
			return json(
				{
					success: false,
					error:
						'Acceso denegado. Solo especialistas y administradores pueden validar diagnósticos.'
				},
				{ status: 403 }
			);
		}

		const idRespuesta = Number.parseInt(params.idRespuesta, 10);
		if (Number.isNaN(idRespuesta)) {
			return json({ success: false, error: 'ID de respuesta inválido' }, { status: 400 });
		}

		const respuesta = await respuestasService.getRespuestaDetalle(idRespuesta);
		if (!respuesta) {
			return json({ success: false, error: 'Respuesta no encontrada' }, { status: 404 });
		}

		if (!respuesta.id_evaluacion || !respuesta.trastornos_detectados) {
			return json(
				{
					success: false,
					error: 'La respuesta aún no tiene una evaluación ML lista para validar.'
				},
				{ status: 409 }
			);
		}

		const body = await request.json();
		const validatedData = saveValidacionSchema.parse(body);
		const diagnosticoModelo = validacionesService.getDiagnosticoModelo(
			respuesta.trastornos_detectados
		);

		let diagnosticoEspecialista = validatedData.diagnosticoEspecialista;
		if (validatedData.decision === 'aceptar') {
			diagnosticoEspecialista = diagnosticoModelo;
		}

		const comparacion = validacionesService.calcularComparacionDiagnosticos(
			diagnosticoModelo,
			diagnosticoEspecialista
		);

		if (validatedData.decision !== 'aceptar' && comparacion.esCoincidenteTotal) {
			return json(
				{
					success: false,
					error:
						'Para rechazar o modificar el diagnóstico debe existir al menos una diferencia frente al modelo.'
				},
				{ status: 422 }
			);
		}

		const validacion = await validacionesService.saveValidacion({
			idEvaluacion: respuesta.id_evaluacion,
			idEspecialista: sessionData.id_especialista,
			decision: validatedData.decision,
			diagnosticoModelo,
			diagnosticoEspecialista,
			nivelConfianza: validatedData.nivelConfianza ?? null,
			observaciones: validatedData.observaciones ?? null,
			recomendacionPaciente: validatedData.recomendacionPaciente ?? null,
			requiereSeguimiento: validatedData.requiereSeguimiento ?? false
		});

		return json({
			success: true,
			message: 'Validación guardada correctamente',
			validacion
		});
	} catch (error) {
		if (error.name === 'ZodError') {
			return json(
				{
					success: false,
					error: 'Datos inválidos. Revisa la validación ingresada.',
					details: error.issues || error.errors || []
				},
				{ status: 400 }
			);
		}

		console.error('❌ Error al guardar validación:', error);
		return json(
			{
				success: false,
				error: 'Error interno al guardar la validación',
				details: error.message
			},
			{ status: 500 }
		);
	}
}
