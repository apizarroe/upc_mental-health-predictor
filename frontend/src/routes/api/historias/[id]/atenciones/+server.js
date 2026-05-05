import { json } from '@sveltejs/kit';
import * as atencionesService from '$lib/server/services/atenciones.js';

const TIPOS_VALIDOS = ['Presencial', 'Virtual', 'Telefónica'];

function getSession(cookies) {
	const cookie = cookies.get('session');
	if (!cookie) return null;
	try { return JSON.parse(cookie); } catch { return null; }
}

export async function GET({ params }) {
	try {
		const atenciones = await atencionesService.getAtencionesByHistoria(parseInt(params.id));
		return json({ success: true, data: atenciones });
	} catch (error) {
		console.error('Error al obtener atenciones:', error);
		return json({ success: false, error: 'Error al obtener atenciones' }, { status: 500 });
	}
}

export async function POST({ params, request, cookies }) {
	try {
		const session = getSession(cookies);
		if (!session) return json({ success: false, error: 'No autorizado' }, { status: 401 });

		const body = await request.json();

		if (!body.tipo_atencion || !TIPOS_VALIDOS.includes(body.tipo_atencion)) {
			return json({ success: false, error: 'Tipo de atención inválido' }, { status: 400 });
		}

		const atencion = await atencionesService.createAtencion(
			parseInt(params.id),
			parseInt(session.id_especialista),
			body
		);

		return json({ success: true, data: atencion }, { status: 201 });
	} catch (error) {
		console.error('Error al crear atención:', error);
		return json({ success: false, error: 'Error al crear atención' }, { status: 500 });
	}
}
