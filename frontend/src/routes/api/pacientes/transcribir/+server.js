import { json } from '@sveltejs/kit';

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

export async function POST({ request, cookies }) {
	try {
		// Verificar sesión del paciente
		const sessionCookie = cookies.get('session-paciente');

		if (!sessionCookie) {
			return json({ success: false, error: 'No autorizado' }, { status: 401 });
		}

		// Obtener FormData con el audio
		const formData = await request.formData();
		const audioFile = formData.get('audio');
		const questionId = formData.get('questionId');

		if (!audioFile) {
			return json({ success: false, error: 'No se recibió el archivo de audio' }, { status: 400 });
		}

		console.log('Recibido audio para pregunta:', questionId);
		console.log('Tamaño del archivo:', audioFile.size, 'bytes');

		// Crear FormData para enviar al backend de Python
		const pythonFormData = new FormData();
		pythonFormData.append('audio', audioFile);

		// Enviar al endpoint de Python para transcripción
		const response = await fetch(`${ML_API_URL}/api/v1/transcribe`, {
			method: 'POST',
			body: pythonFormData,
			signal: AbortSignal.timeout(60000) // 60 segundos timeout
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(`Error en transcripción: ${errorData.detail || response.statusText}`);
		}

		const result = await response.json();

		console.log('Transcripción exitosa:', result.transcription.substring(0, 50) + '...');

		return json({
			success: true,
			transcription: result.transcription
		});

	} catch (error) {
		console.error('Error al procesar audio:', error);
		return json({
			success: false,
			error: error.message || 'Error al procesar el audio'
		}, { status: 500 });
	}
}
