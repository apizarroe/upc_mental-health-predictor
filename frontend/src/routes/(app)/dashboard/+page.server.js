import * as pacientesService from '$lib/server/services/pacientes.js';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as atencionesService from '$lib/server/services/atenciones.js';
import { getConteoAlertasTotal } from '$lib/server/services/alertas.js';

export async function load() {
	const pacientes = await pacientesService.getAllPacientes();
	const pacientesActivos = pacientes.filter((p) => p.flg_activo).length;

	const notasDiarias = await respuestasService.contarTodasRespuestas();

	const atenciones = await atencionesService.contarTodasAtenciones();
	const atencionesRecientes = await atencionesService.getAtencionesRecientes(7);

	const alertasCriticas = await getConteoAlertasTotal();

	return {
		pacientesActivos,
		notasDiarias,
		atenciones,
		atencionesRecientes,
		alertasCriticas
	};
}
