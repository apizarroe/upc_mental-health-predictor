import { json } from '@sveltejs/kit';
import { recuperarPasswordPaciente } from '$lib/server/services/auth-paciente.js';

export async function POST({ request }) {
	try {
		const { correo } = await request.json();

		if (!correo || !correo.trim()) {
			return json({ success: false, error: 'El correo es requerido' }, { status: 400 });
		}

		const resultado = await recuperarPasswordPaciente(correo.trim().toLowerCase());

		if (!resultado.success) {
			return json({ success: false, error: resultado.error }, { status: 400 });
		}

		return json({ success: true, message: resultado.message });
	} catch (error) {
		console.error('Error al recuperar contraseña de paciente:', error);
		return json({ success: false, error: 'Error interno del servidor' }, { status: 500 });
	}
}
