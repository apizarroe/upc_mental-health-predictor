import { json } from '@sveltejs/kit';
import {
	getRetrainingStatus,
	startManualRetraining
} from '$lib/server/services/reentrenamiento.js';

function getSessionData(cookies) {
	const sessionCookie = cookies.get('session');
	return sessionCookie ? JSON.parse(sessionCookie) : null;
}

function validarAdmin(sessionData) {
	return sessionData?.rol === 'admin';
}

export async function GET({ cookies }) {
	const sessionData = getSessionData(cookies);
	if (!sessionData) {
		return json({ success: false, error: 'No autorizado' }, { status: 401 });
	}

	if (!validarAdmin(sessionData)) {
		return json(
			{
				success: false,
				error: 'Acceso denegado. Solo el usuario admin puede consultar el reentrenamiento.'
			},
			{ status: 403 }
		);
	}

	return json({
		success: true,
		status: await getRetrainingStatus()
	});
}

export async function POST({ cookies }) {
	try {
		const sessionData = getSessionData(cookies);
		if (!sessionData) {
			return json({ success: false, error: 'No autorizado' }, { status: 401 });
		}

		if (!validarAdmin(sessionData)) {
			return json(
				{
					success: false,
					error: 'Acceso denegado. Solo el usuario admin puede gatillar el reentrenamiento.'
				},
				{ status: 403 }
			);
		}

		const result = await startManualRetraining(sessionData);

		if (!result.started) {
			const statusCode = result.reason === 'running' ? 409 : 200;
			const message =
				result.reason === 'running'
					? 'Ya hay un reentrenamiento en curso.'
					: result.reason === 'empty_rows'
						? 'No se encontraron ejemplos válidos para construir el dataset de reentrenamiento.'
						: 'No hay validaciones pendientes de reentrenamiento.';

			return json(
				{
					success: result.reason === 'no_pending',
					message,
					status: result.status
				},
				{ status: statusCode }
			);
		}

		return json({
			success: true,
			message: 'Reentrenamiento iniciado correctamente.',
			queuedValidations: result.queuedValidations,
			status: result.status
		});
	} catch (error) {
		console.error('❌ Error al iniciar reentrenamiento:', error);
		return json(
			{
				success: false,
				error: 'No se pudo iniciar el reentrenamiento',
				details: error.message
			},
			{ status: 500 }
		);
	}
}
