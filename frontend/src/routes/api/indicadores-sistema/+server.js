import { json } from '@sveltejs/kit';
import * as indicadoresService from '$lib/server/services/indicadores-sistema.js';
import { generarReporteIndicadoresSchema } from '$lib/server/validators/indicadores-sistema.js';

function getSessionData(cookies) {
	const sessionCookie = cookies.get('session');
	return sessionCookie ? JSON.parse(sessionCookie) : null;
}

function requireAdminSession(cookies) {
	const sessionData = getSessionData(cookies);

	if (!sessionData) {
		return { ok: false, status: 401, error: 'No autorizado' };
	}

	if (sessionData.rol !== 'admin') {
		return {
			ok: false,
			status: 403,
			error: 'Acceso denegado. Solo administradores pueden gestionar reportes del sistema.'
		};
	}

	return { ok: true, sessionData };
}

export async function GET({ url, cookies }) {
	try {
		const auth = requireAdminSession(cookies);
		if (!auth.ok) {
			return json({ success: false, error: auth.error }, { status: auth.status });
		}

		const limit = Number.parseInt(url.searchParams.get('limit') || '20', 10);
		const offset = Number.parseInt(url.searchParams.get('offset') || '0', 10);

		const result = await indicadoresService.listarReportesIndicadores({ limit, offset });

		return json({
			success: true,
			data: result.data,
			total: result.total,
			limit: result.limit,
			offset: result.offset
		});
	} catch (error) {
		console.error('❌ Error al listar reportes de indicadores:', error);
		return json(
			{ success: false, error: 'Error al obtener reportes de indicadores del sistema' },
			{ status: 500 }
		);
	}
}

export async function POST({ request, cookies }) {
	try {
		const auth = requireAdminSession(cookies);
		if (!auth.ok) {
			return json({ success: false, error: auth.error }, { status: auth.status });
		}

		const body = await request.json();
		const validatedData = generarReporteIndicadoresSchema.parse(body);

		const reporte = await indicadoresService.generarReporteIndicadores({
			fechaInicio: validatedData.fecha_inicio,
			fechaFin: validatedData.fecha_fin,
			user: auth.sessionData
		});

		return json(
			{
				success: true,
				data: reporte,
				message: 'Reporte generado correctamente'
			},
			{ status: 201 }
		);
	} catch (error) {
		if (error.name === 'ZodError') {
			return json(
				{
					success: false,
					error: 'Datos inválidos para generar el reporte.',
					details: error.issues || error.errors || []
				},
				{ status: 400 }
			);
		}

		const status = error.status || 500;
		console.error('❌ Error al generar reporte de indicadores:', error);
		return json(
			{
				success: false,
				error: error.message || 'Error al generar el reporte de indicadores del sistema'
			},
			{ status }
		);
	}
}
