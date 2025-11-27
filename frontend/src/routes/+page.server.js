import { redirect } from '@sveltejs/kit';

/**
 * Si el paciente ya está autenticado, redirigir a su área
 * Si el especialista ya está autenticado, redirigir al dashboard
 */
export async function load({ cookies }) {
	// Verificar sesión de paciente
	const sessionPacienteCookie = cookies.get('session-paciente');
	if (sessionPacienteCookie) {
		try {
			const sessionData = JSON.parse(sessionPacienteCookie);
			const loginTime = sessionData.loginTime || Date.now();
			const now = Date.now();
			const minutosTranscurridos = (now - loginTime) / 1000 / 60;

			// Si la sesión es válida (menos de 30 minutos), redirigir al área de pacientes
			if (minutosTranscurridos <= 30) {
				throw redirect(303, '/paciente');
			}
		} catch (error) {
			if (error.status === 303) {
				throw error;
			}
			// Si hay error, eliminar cookie y permitir login
			cookies.delete('session-paciente', { path: '/' });
		}
	}

	// Verificar sesión de especialista
	const sessionEspecialistaCookie = cookies.get('session');
	if (sessionEspecialistaCookie) {
		try {
			const sessionData = JSON.parse(sessionEspecialistaCookie);
			const loginTime = sessionData.loginTime || Date.now();
			const now = Date.now();
			const minutosTranscurridos = (now - loginTime) / 1000 / 60;

			// Si la sesión es válida, redirigir al dashboard de especialistas
			if (minutosTranscurridos <= 30) {
				throw redirect(303, '/inicio');
			}
		} catch (error) {
			if (error.status === 303) {
				throw error;
			}
			// Si hay error, eliminar cookie y permitir login
			cookies.delete('session', { path: '/' });
		}
	}

	return {};
}
