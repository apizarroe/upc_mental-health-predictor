import { error } from '@sveltejs/kit';

export async function load({ params, fetch }) {
	try {
		const response = await fetch(`/api/especialistas/${params.id}`);
		const result = await response.json();

		if (!result.success) {
			throw error(404, result.error || 'Especialista no encontrado');
		}

		return {
			especialista: result.data
		};
	} catch (err) {
		throw error(500, 'Error al cargar datos del especialista');
	}
}
