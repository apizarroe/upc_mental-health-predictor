import { getAlertasRiesgo } from '$lib/server/services/alertas.js';

export async function load({ parent }) {
	const { user } = await parent();
	const alertas = await getAlertasRiesgo(user.id_especialista);
	return { alertas };
}
