import { redirect } from '@sveltejs/kit';

/**
 * Si el usuario ya está autenticado, redirigir al dashboard
 */
export async function load({ cookies }) {
	const sessionCookie = cookies.get('session');

	if (sessionCookie) {
		try {
			const sessionData = JSON.parse(sessionCookie);
			const loginTime = sessionData.loginTime || Date.now();
			const now = Date.now();
			const minutosTranscurridos = (now - loginTime) / 1000 / 60;

			// Si la sesión es válida (menos de 30 minutos), redirigir al dashboard
			if (minutosTranscurridos <= 30) {
				throw redirect(303, '/');
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
