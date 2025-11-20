import { json } from '@sveltejs/kit';
import * as notasService from '$lib/server/services/notas.js';
import { canAccessOwnData, isEspecialista } from '$lib/utils/permissions.js';

/**
 * GET /api/notas?id_paciente=123
 * Obtener todas las notas de un paciente
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

	// Verificar permisos: solo el mismo paciente o especialistas
	if (!canAccessOwnData(user, idPaciente)) {
		return json({ success: false, error: 'No tiene permisos para ver estas notas' }, { status: 403 });
	}

	try {
		const notas = await notasService.getNotasByPaciente(idPaciente);

		return json({
			success: true,
			data: notas
		});
	} catch (error) {
		console.error('Error al obtener notas:', error);
		return json({ success: false, error: 'Error al obtener notas' }, { status: 500 });
	}
}

/**
 * POST /api/notas
 * Crear una o múltiples notas
 * Body: { id_paciente, notas: [{pregunta, respuesta}, ...] }
 */
export async function POST({ request, locals }) {
	const user = locals.user;

	if (!user) {
		return json({ success: false, error: 'No autenticado' }, { status: 401 });
	}

	try {
		const body = await request.json();
		const { id_paciente, notas } = body;

		if (!id_paciente || !notas || !Array.isArray(notas) || notas.length === 0) {
			return json({
				success: false,
				error: 'ID de paciente y array de notas requeridos'
			}, { status: 400 });
		}

		// Solo los pacientes pueden crear sus propias notas
		if (user.user_type !== 'paciente' || user.user_id !== id_paciente) {
			return json({
				success: false,
				error: 'Solo puede crear sus propias notas'
			}, { status: 403 });
		}

		// Validar que todas las notas tengan pregunta y respuesta
		const notasValidas = notas.every(nota => nota.pregunta && nota.respuesta);
		if (!notasValidas) {
			return json({
				success: false,
				error: 'Todas las notas deben tener pregunta y respuesta'
			}, { status: 400 });
		}

		// Crear notas en batch
		const notasCreadas = await notasService.createNotasBatch(id_paciente, notas);

		return json({
			success: true,
			data: notasCreadas,
			message: `${notasCreadas.length} nota(s) creada(s) exitosamente`
		}, { status: 201 });
	} catch (error) {
		console.error('Error al crear notas:', error);
		return json({ success: false, error: 'Error al crear notas' }, { status: 500 });
	}
}
