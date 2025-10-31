import { json } from '@sveltejs/kit';
import { createEspecialistaSchema } from '$lib/server/validators/especialista.js';
import * as especialistasService from '$lib/server/services/especialistas.js';

/**
 * GET /api/especialistas
 * Obtener todos los especialistas
 */
export async function GET() {
	try {
		const especialistas = await especialistasService.getAllEspecialistas();

		return json({
			success: true,
			data: especialistas,
			count: especialistas.length
		});
	} catch (error) {
		console.error('Error al obtener especialistas:', error);
		return json(
			{
				success: false,
				error: 'Error al obtener especialistas',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * POST /api/especialistas
 * Crear un nuevo especialista
 */
export async function POST({ request }) {
	try {
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = createEspecialistaSchema.parse(body);

		// Crear especialista en la base de datos
		const especialista = await especialistasService.createEspecialista(validatedData);

		return json(
			{
				success: true,
				data: especialista,
				message: 'Especialista creado exitosamente'
			},
			{ status: 201 }
		);
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
		console.error('Error al crear especialista:', error);
		return json(
			{
				success: false,
				error: 'Error al crear especialista',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
