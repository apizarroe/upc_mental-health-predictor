import { json } from '@sveltejs/kit';
import { createPacienteSchema } from '$lib/server/validators/paciente.js';
import * as pacientesService from '$lib/server/services/pacientes.js';

/**
 * GET /api/pacientes
 * Obtener todos los pacientes
 */
export async function GET() {
	try {
		const pacientes = await pacientesService.getAllPacientes();

		return json({
			success: true,
			data: pacientes,
			count: pacientes.length
		});
	} catch (error) {
		console.error('Error al obtener pacientes:', error);
		return json(
			{
				success: false,
				error: 'Error al obtener pacientes',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * POST /api/pacientes
 * Crear un nuevo paciente
 */
export async function POST({ request }) {
	try {
		const body = await request.json();

		// Validar datos con Zod
		const validatedData = createPacienteSchema.parse(body);

		// Crear paciente en la base de datos
		const paciente = await pacientesService.createPaciente(validatedData);

		return json(
			{
				success: true,
				data: paciente,
				message: 'Paciente creado exitosamente'
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
		console.error('Error al crear paciente:', error);
		return json(
			{
				success: false,
				error: 'Error al crear paciente',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
