import { error } from '@sveltejs/kit';

export async function load({ params, fetch }) {
	try {
		const response = await fetch(`/api/pacientes/${params.id}`);
		const result = await response.json();

		if (!result.success) {
			throw error(404, result.error || 'Paciente no encontrado');
		}

		return {
			paciente: result.data
		};
	} catch (err) {
		throw error(500, 'Error al cargar datos del paciente');
	}
}
