import { json } from '@sveltejs/kit';
import { updatePacienteSchema } from '$lib/server/validators/paciente.js';
import * as pacientesService from '$lib/server/services/pacientes.js';
import * as historiasService from '$lib/server/services/historias.js';

/**
 * GET /api/pacientes/[id]
 * Obtener un paciente por ID
 */
export async function GET({ params }) {
	try {
		const { id } = params;
		const paciente = await pacientesService.getPacienteById(id);

		if (!paciente) {
			return json(
				{
					success: false,
					error: 'Paciente no encontrado'
				},
				{ status: 404 }
			);
		}

		return json({
			success: true,
			data: paciente
		});
	} catch (error) {
		console.error('Error al obtener paciente:', error);
		return json(
			{
				success: false,
				error: 'Error al obtener paciente',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * PUT /api/pacientes/[id]
 * Actualizar un paciente existente
 */
export async function PUT({ params, request, locals }) {
	try {
		const { id } = params;
		const body = await request.json();

		// Log para depuración
		console.log(`📝 Datos recibidos para actualizar paciente ${id}:`, JSON.stringify(body, null, 2));

		// Validar datos con Zod
		const validatedData = updatePacienteSchema.parse(body);

		// Si se está desactivando el paciente (flg_activo = false), cerrar historia clínica si está activa
		let historiaClinicaCerrada = false;
		if (validatedData.flg_activo === false) {
			const historiaActiva = await historiasService.getHistoriaByPacienteId(id);

			if (historiaActiva && (!historiaActiva.situacion_historia || historiaActiva.situacion_historia === 'Abierta')) {
				const idEspecialista = locals.user?.id_especialista || null;
				await historiasService.updateHistoria(
					historiaActiva.id_historia,
					{
						situacion_historia: 'Cierre Temporal',
						motivo_cierre: 'Paciente dado de baja del sistema'
					},
					idEspecialista
				);
				historiaClinicaCerrada = true;
				console.log(`✅ Historia clínica ${historiaActiva.id_historia} cerrada temporalmente por desactivación de paciente ${id}`);
			}
		}

		// Actualizar paciente
		const paciente = await pacientesService.updatePaciente(id, validatedData);

		if (!paciente) {
			return json(
				{
					success: false,
					error: 'Paciente no encontrado'
				},
				{ status: 404 }
			);
		}

		console.log(`✅ Paciente ${id} actualizado exitosamente`);
		return json({
			success: true,
			data: paciente,
			message: 'Paciente actualizado exitosamente',
			historiaClinicaCerrada
		});
	} catch (error) {
		// Error de validación de Zod
		if (error.name === 'ZodError') {
			console.error(`❌ Error de validación Zod en actualización de paciente ${params.id}:`);
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
		console.error('❌ Error al actualizar paciente:', error);
		return json(
			{
				success: false,
				error: 'Error al actualizar paciente',
				message: error.message
			},
			{ status: 500 }
		);
	}
}

/**
 * DELETE /api/pacientes/[id]
 * Eliminar (desactivar) un paciente
 * No elimina físicamente, solo setea flg_activo = false
 * Si tiene historia clínica activa, la cierra temporalmente
 */
export async function DELETE({ params, locals }) {
	try {
		const { id } = params;

		// Verificar si el paciente tiene historia clínica activa
		const historiaActiva = await historiasService.getHistoriaByPacienteId(id);

		// Si tiene historia clínica activa (estado "Abierta"), cerrarla temporalmente
		if (historiaActiva && (!historiaActiva.situacion_historia || historiaActiva.situacion_historia === 'Abierta')) {
			const idEspecialista = locals.user?.id_especialista || null;
			await historiasService.updateHistoria(
				historiaActiva.id_historia,
				{
					situacion_historia: 'Cierre Temporal',
					motivo_cierre: 'Paciente dado de baja del sistema'
				},
				idEspecialista
			);
			console.log(`✅ Historia clínica ${historiaActiva.id_historia} cerrada temporalmente por baja de paciente ${id}`);
		}

		// Desactivar al paciente
		const paciente = await pacientesService.deletePaciente(id);

		if (!paciente) {
			return json(
				{
					success: false,
					error: 'Paciente no encontrado'
				},
				{ status: 404 }
			);
		}

		return json({
			success: true,
			data: paciente,
			message: 'Paciente desactivado exitosamente',
			historiaClinicaCerrada: !!historiaActiva
		});
	} catch (error) {
		console.error('Error al eliminar paciente:', error);
		return json(
			{
				success: false,
				error: 'Error al eliminar paciente',
				message: error.message
			},
			{ status: 500 }
		);
	}
}
