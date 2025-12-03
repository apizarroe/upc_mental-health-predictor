import { redirect } from '@sveltejs/kit';

/**
 * Redirigir /paciente a /paciente/inicio
 */
export async function load() {
	throw redirect(303, '/paciente/inicio');
}
