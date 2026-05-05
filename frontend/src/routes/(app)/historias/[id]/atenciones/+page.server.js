import { error } from '@sveltejs/kit';
import * as historiasService from '$lib/server/services/historias.js';
import * as atencionesService from '$lib/server/services/atenciones.js';

export async function load({ params, parent }) {
	const { user } = await parent();
	const idHistoria = parseInt(params.id);

	const historia = await historiasService.getHistoriaById(idHistoria);
	if (!historia) throw error(404, 'Historia clínica no encontrada');

	const atenciones = await atencionesService.getAtencionesByHistoria(idHistoria);

	return {
		historia,
		atenciones,
		currentUserId: user?.id_especialista ?? null
	};
}
