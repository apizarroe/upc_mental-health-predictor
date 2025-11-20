import { json } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';
import { historiaClinicaSchema } from '$lib/server/validators/historia.js';

export async function GET() {
	try {
		const historias = await historiasService.getAllHistorias();
		return json({ success: true, data: historias });
	} catch (error) {
		console.error('Error al obtener historias:', error);
		return json({ success: false, error: 'Error al obtener historias clínicas' }, { status: 500 });
	}
}

export async function POST({ request, cookies }) {
	try {
		const body = await request.json();

		// Obtener especialista de la sesión
		const sessionCookie = cookies.get('session');
		if (!sessionCookie) {
			return json({ success: false, error: 'No hay sesión activa' }, { status: 401 });
		}

		const sessionData = JSON.parse(sessionCookie);

		// Agregar el especialista de la sesión (convertir a número)
		body.especialista_apertura = Number(sessionData.user_id);

		// Convertir id_paciente a número si viene como string
		if (body.id_paciente) {
			body.id_paciente = Number(body.id_paciente);
		}

		// Log para depuración
		console.log('📝 Datos recibidos para crear historia clínica:', JSON.stringify(body, null, 2));

		// Validar datos
		const validatedData = historiaClinicaSchema.parse(body);

		// Verificar si el paciente ya tiene una historia clínica activa
		const historiaExistente = await historiasService.getHistoriaByPacienteId(validatedData.id_paciente);
		if (historiaExistente) {
			return json({
				success: false,
				error: 'El paciente ya tiene una historia clínica activa'
			}, { status: 400 });
		}

		const historia = await historiasService.createHistoria(validatedData);
		return json({ success: true, data: historia }, { status: 201 });
	} catch (error) {
		if (error.name === 'ZodError') {
			console.error('❌ Error de validación Zod:');
			console.error(error.issues || error.errors || error);
			return json({
				success: false,
				error: 'Datos inválidos. Por favor revise los campos marcados.',
				details: error.issues || error.errors || []
			}, { status: 400 });
		}

		console.error('❌ Error al crear historia clínica:', error);
		return json({ success: false, error: 'Error al crear historia clínica' }, { status: 500 });
	}
}
