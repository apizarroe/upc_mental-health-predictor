import * as pacientesService from '$lib/server/services/pacientes.js';
import * as respuestasService from '$lib/server/services/respuestas.js';
import * as atencionesService from '$lib/server/services/atenciones.js';
import { getConteoAlertasMisPacientes } from '$lib/server/services/alertas.js';

export async function load({ parent }) {
	const { user } = await parent();

	const pacientes = await pacientesService.getAllPacientes();
	const pacientesActivos = pacientes.filter((p) => p.flg_activo).length;

	const notasDiariasHoy = await respuestasService.contarRespuestasDeHoy();

	const atencionesHoy = await atencionesService.contarAtencionesDeHoy();

	const alertasCriticas = await getConteoAlertasMisPacientes(user.id_especialista);

	return {
		pacientesActivos,
		notasDiariasHoy,
		atencionesHoy,
		alertasCriticas
	};
}
