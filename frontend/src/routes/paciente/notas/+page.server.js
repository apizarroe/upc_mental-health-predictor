import { redirect } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';

export async function load({ cookies }) {
	// Verificar sesión del paciente
	const sessionCookie = cookies.get('session-paciente');

	if (!sessionCookie) {
		throw redirect(302, '/login/paciente');
	}

	const sessionData = JSON.parse(sessionCookie);
	const id_paciente = parseInt(sessionData.id_paciente);

	// Verificar si el paciente tiene historia clínica activa
	const historiaClinica = await historiasService.getHistoriaByPacienteId(id_paciente);

	return {
		tieneHistoriaClinica: !!historiaClinica
	};
}
