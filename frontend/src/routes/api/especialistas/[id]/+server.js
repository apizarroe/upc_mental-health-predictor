import { json } from '@sveltejs/kit';
import { updateEspecialistaSchema } from '$lib/server/validators/especialista.js';
import * as especialistasService from '$lib/server/services/especialistas.js';

/**
 * GET /api/especialistas/[id]
 * Obtener un especialista por ID
 */
export async function GET({ params }) {
	try {
		const { id } = params;
		const especialista = await especialistasService.getEspecialistaById(id);

		if (!especialista) {
			return json(
				{
					success: false,
					error: 'Especialista no encontrado'
				},
				{ status: 404 }
			);
		}

		return json({
			success: true,
			data: especialista
		});
	} catch (error) {
		console.error('Error al obtener especialista:', error);
		return json(
			{
				success: false,
				error: 'Error al obtener especialista',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * PUT /api/especialistas/[id]
 * Actualizar un especialista existente
 */
export async function PUT({ params, request }) {
	try {
		const { id } = params;
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = updateEspecialistaSchema.parse(body);

		// Actualizar especialista
		const especialista = await especialistasService.updateEspecialista(id, validatedData);

		if (!especialista) {
			return json(
				{
					success: false,
					error: 'Especialista no encontrado'
				},
				{ status: 404 }
			);
		}

		return json({
			success: true,
			data: especialista,
			message: 'Especialista actualizado exitosamente'
		});
	} catch (error) {
		// Error de validación de Zod
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

		// Otros errores
		console.error('Error al actualizar especialista:', error);
		return json(
			{
				success: false,
				error: 'Error al actualizar especialista',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * DELETE /api/especialistas/[id]
 * Eliminar (desactivar) un especialista
 * No elimina físicamente, solo setea flg_activo = false
 */
export async function DELETE({ params }) {
	try {
		const { id } = params;
		const especialista = await especialistasService.deleteEspecialista(id);

		if (!especialista) {
			return json(
				{
					success: false,
					error: 'Especialista no encontrado'
				},
				{ status: 404 }
			);
		}

		return json({
			success: true,
			data: especialista,
			message: 'Especialista desactivado exitosamente'
		});
	} catch (error) {
		console.error('Error al eliminar especialista:', error);
		return json(
			{
				success: false,
				error: 'Error al eliminar especialista',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
