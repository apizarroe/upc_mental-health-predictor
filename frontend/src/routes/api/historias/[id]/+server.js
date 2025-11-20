import { json } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';
import * as pacientesService from '$lib/server/services/pacientes.js';
import { updateHistoriaSchema, cerrarHistoriaSchema } from '$lib/server/validators/historia.js';

export async function GET({ params }) {
	try {
		const historia = await historiasService.getHistoriaById(params.id);

		if (!historia) {
			return json({ success: false, error: 'Historia clínica no encontrada' }, { status: 404 });
		}

		return json({ success: true, data: historia });
	} catch (error) {
		console.error('Error al obtener historia:', error);
		return json({ success: false, error: 'Error al obtener historia clínica' }, { status: 500 });
	}
}

export async function PUT({ params, request, cookies }) {
	try {
		const body = await request.json();

		// Obtener especialista de la sesión
		const sessionCookie = cookies.get('session');
		if (!sessionCookie) {
			return json({ success: false, error: 'No hay sesión activa' }, { status: 401 });
		}

		const sessionData = JSON.parse(sessionCookie);

		// Log para depuración
		console.log(`📝 Datos recibidos para actualizar historia ${params.id}:`, JSON.stringify(body, null, 2));

		// Validar datos
		const validatedData = updateHistoriaSchema.parse(body);

		// Si se está intentando reabrir la historia (cambiar a "Abierta"), validar que el paciente esté activo
		if (validatedData.situacion_historia === 'Abierta') {
			const historiaActual = await historiasService.getHistoriaById(params.id);
			if (!historiaActual) {
				return json({ success: false, error: 'Historia clínica no encontrada' }, { status: 404 });
			}

			const paciente = await pacientesService.getPacienteById(historiaActual.id_paciente);
			if (!paciente) {
				return json({ success: false, error: 'Paciente no encontrado' }, { status: 404 });
			}

			if (!paciente.flg_activo) {
				return json({
					success: false,
					error: 'No se puede reabrir la historia clínica porque el paciente no se encuentra activo en el sistema'
				}, { status: 400 });
			}
		}

		const historia = await historiasService.updateHistoria(
			params.id,
			validatedData,
			sessionData.user_id
		);

		if (!historia) {
			return json({ success: false, error: 'Historia clínica no encontrada' }, { status: 404 });
		}

		console.log(`✅ Historia ${params.id} actualizada exitosamente`);
		return json({ success: true, data: historia });
	} catch (error) {
		if (error.name === 'ZodError') {
			console.error('❌ Error de validación Zod en actualización de historia:');
			console.error(error.issues || error.errors || error);
			return json({
				success: false,
				error: 'Datos inválidos. Por favor revise los campos marcados.',
				details: error.issues || error.errors || []
			}, { status: 400 });
		}

		console.error('❌ Error al actualizar historia:', error);
		return json({ success: false, error: 'Error al actualizar historia clínica' }, { status: 500 });
	}
}
