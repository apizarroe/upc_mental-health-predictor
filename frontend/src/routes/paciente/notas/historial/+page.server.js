import { redirect } from '@sveltejs/kit';
import * as respuestasService from '$lib/server/services/respuestas.js';

export async function load({ cookies }) {
	// Verificar sesión del paciente
	const sessionCookie = cookies.get('session-paciente');

	if (!sessionCookie) {
		throw redirect(302, '/login/paciente');
	}

	const sessionData = JSON.parse(sessionCookie);
	const id_paciente = parseInt(sessionData.id_paciente);

	// Obtener solo las respuestas del día actual (GMT-5)
	const respuestas = await respuestasService.getRespuestasDelDia(id_paciente);

	return {
		respuestas
	};
}
