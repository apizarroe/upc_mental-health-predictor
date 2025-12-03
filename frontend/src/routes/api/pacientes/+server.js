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
		const pacientesConHistoria = await pacientesService.getPacientesConHistoriaClinica();

		return json({
			success: true,
			data: pacientes,
			pacientesConHistoria: pacientesConHistoria,
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

		// Log para depuración
		console.log('📝 Datos recibidos para crear paciente:', JSON.stringify(body, null, 2));

		// Validar datos con Zod
		const validatedData = createPacienteSchema.parse(body);

		// Crear paciente en la base de datos
		const paciente = await pacientesService.createPaciente(validatedData);

		console.log(`✅ Paciente creado exitosamente con ID: ${paciente.id_paciente}`);
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
			console.error('❌ Error de validación Zod en creación de paciente:');
			console.error(error.issues || error.errors || error);
			return json(
				{
					success: false,
					error: 'Datos inválidos. Por favor revise los campos marcados.',
					details: error.issues || error.errors || []
				},
				{ status: 400 }
			);
		}

		// Otros errores
		console.error('❌ Error al crear paciente:', error);
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
