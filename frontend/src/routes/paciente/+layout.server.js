import { redirect } from '@sveltejs/kit';
import * as authPacienteService from '$lib/server/services/auth-paciente.js';

/**
 * Middleware de protección para el área de pacientes
 * Verifica que el paciente esté autenticado y su sesión sea válida
 */
export async function load({ cookies }) {
	const sessionCookie = cookies.get('session-paciente');

	if (!sessionCookie) {
		throw redirect(303, '/?expired=true');
	}

	let sessionData;

	try {
		sessionData = JSON.parse(sessionCookie);
	} catch (parseError) {
		throw redirect(303, '/?expired=true');
	}

	const loginTime = sessionData.loginTime || Date.now();
	const now = Date.now();
	const minutosTranscurridos = (now - loginTime) / 1000 / 60;

	// Sesión expirada (más de 30 minutos)
	if (minutosTranscurridos > 30) {
		throw redirect(303, '/?expired=true');
	}

	// Obtener datos actualizados del paciente
	let paciente;
	try {
		paciente = await authPacienteService.getPacienteByIdForAuth(
			sessionData.id_paciente
		);
	} catch (dbError) {
		console.error('Error al obtener datos del paciente:', dbError);
		throw redirect(303, '/?expired=true');
	}

	if (!paciente) {
		throw redirect(303, '/?invalid=true');
	}

	// Renovar cookie solo si han pasado más de 10 minutos (evita renovaciones constantes)
	if (minutosTranscurridos > 10) {
		sessionData.loginTime = Date.now();
		cookies.set('session-paciente', JSON.stringify(sessionData), {
			path: '/',
			httpOnly: true,
			secure: process.env.NODE_ENV === 'production',
			sameSite: 'strict',
			maxAge: 60 * 30
		});
	}

	return {
		user: {
			...paciente,
			tipo_usuario: 'paciente'
		}
	};
}
