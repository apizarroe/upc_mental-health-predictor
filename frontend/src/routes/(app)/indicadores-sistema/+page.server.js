import { redirect } from '@sveltejs/kit';
import { canAccessIndicadoresSistema } from '$lib/utils/permissions.js';

export async function load({ parent }) {
	const { user } = await parent();

	if (!canAccessIndicadoresSistema(user.rol)) {
		throw redirect(303, '/');
	}

	return {};
}
