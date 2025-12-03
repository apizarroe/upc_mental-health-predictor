import * as historiasService from '$lib/server/services/historias.js';
import { error } from '@sveltejs/kit';

export async function load({ params }) {
	try {
		const historia = await historiasService.getHistoriaById(params.id);
		const medicaciones = await historiasService.getMedicacionesByHistoria(params.id);

		if (!historia) {
			throw error(404, 'Historia clínica no encontrada');
		}

		return {
			historia,
			medicaciones
		};
	} catch (err) {
		console.error('Error al cargar historia:', err);
		throw error(500, 'Error al cargar los datos de la historia clínica');
	}
}
