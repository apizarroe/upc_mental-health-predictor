import { json } from '@sveltejs/kit';
import * as atencionesService from '$lib/server/services/atenciones.js';

const TIPOS_VALIDOS = ['Presencial', 'Virtual', 'Telefónica'];

function getSession(cookies) {
	const cookie = cookies.get('session');
	if (!cookie) return null;
	try { return JSON.parse(cookie); } catch { return null; }
}

export async function PUT({ params, request, cookies }) {
	try {
		const session = getSession(cookies);
		if (!session) return json({ success: false, error: 'No autorizado' }, { status: 401 });

		const body = await request.json();

		if (!body.tipo_atencion || !TIPOS_VALIDOS.includes(body.tipo_atencion)) {
			return json({ success: false, error: 'Tipo de atención inválido' }, { status: 400 });
		}

		const atencion = await atencionesService.updateAtencion(
			parseInt(params.id),
			parseInt(session.id_especialista),
			body
		);

		if (!atencion) {
			return json({ success: false, error: 'Atención no encontrada o sin permiso' }, { status: 404 });
		}

		return json({ success: true, data: atencion });
	} catch (error) {
		console.error('Error al actualizar atención:', error);
		return json({ success: false, error: 'Error al actualizar atención' }, { status: 500 });
	}
}
