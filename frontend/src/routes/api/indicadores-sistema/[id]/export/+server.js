import { json } from '@sveltejs/kit';
import * as indicadoresService from '$lib/server/services/indicadores-sistema.js';

function getSessionData(cookies) {
	const sessionCookie = cookies.get('session');
	return sessionCookie ? JSON.parse(sessionCookie) : null;
}

export async function GET({ params, cookies }) {
	try {
		const sessionData = getSessionData(cookies);
		if (!sessionData) {
			return json({ success: false, error: 'No autorizado' }, { status: 401 });
		}

		if (sessionData.rol !== 'admin') {
			return json(
				{
					success: false,
					error: 'Acceso denegado. Solo administradores pueden exportar reportes del sistema.'
				},
				{ status: 403 }
			);
		}

		const idReporte = Number.parseInt(params.id, 10);
		if (Number.isNaN(idReporte)) {
			return json({ success: false, error: 'ID de reporte inválido' }, { status: 400 });
		}

		const resultado = await indicadoresService.exportarReporteIndicadoresCsv(idReporte);
		if (!resultado) {
			return json({ success: false, error: 'Reporte no encontrado' }, { status: 404 });
		}

		const fechaGeneracion = new Date(resultado.reporte.fecha_generacion);
		const stamp = [
			fechaGeneracion.getFullYear(),
			String(fechaGeneracion.getMonth() + 1).padStart(2, '0'),
			String(fechaGeneracion.getDate()).padStart(2, '0'),
			String(fechaGeneracion.getHours()).padStart(2, '0'),
			String(fechaGeneracion.getMinutes()).padStart(2, '0'),
			String(fechaGeneracion.getSeconds()).padStart(2, '0')
		].join('');

		return new Response(resultado.csv, {
			status: 200,
			headers: {
				'Content-Type': 'text/csv; charset=utf-8',
				'Content-Disposition': `attachment; filename="reporte-indicadores-sistema-${stamp}.csv"`
			}
		});
	} catch (error) {
		console.error('❌ Error al exportar reporte de indicadores:', error);
		return json(
			{ success: false, error: 'Error al exportar el reporte de indicadores del sistema' },
			{ status: 500 }
		);
	}
}
