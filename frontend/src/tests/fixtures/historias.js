/**
 * Fixtures para testing de Historias Clínicas
 * Datos de prueba reutilizables para tests
 */

export const historiaValida = {
	id_paciente: 1,
	id_especialista: 1,
	fecha_apertura: '2024-01-15',
	diagnostico: 'Trastorno de ansiedad generalizada',
	tratamiento: 'Terapia cognitivo-conductual semanal',
	observaciones: 'Paciente muestra progreso significativo',
	situacion_historia: 'Abierta'
};

export const historiaCompleta = {
	id_historia: 1,
	id_paciente: 1,
	id_especialista: 1,
	fecha_apertura: '2024-01-15',
	diagnostico: 'Trastorno de ansiedad generalizada',
	tratamiento: 'Terapia cognitivo-conductual semanal',
	observaciones: 'Paciente muestra progreso significativo',
	situacion_historia: 'Abierta',
	flg_activo: true
};

export const historiaCerrada = {
	id_historia: 2,
	id_paciente: 2,
	id_especialista: 2,
	fecha_apertura: '2023-06-10',
	diagnostico: 'Depresión mayor',
	tratamiento: 'Psicoterapia y medicación',
	observaciones: 'Alta por mejoría completa',
	situacion_historia: 'Cerrada',
	flg_activo: true
};

export const historiaEnProceso = {
	id_historia: 3,
	id_paciente: 3,
	id_especialista: 3,
	fecha_apertura: '2024-03-20',
	diagnostico: 'Trastorno adaptativo',
	tratamiento: 'Sesiones de terapia familiar',
	observaciones: 'En proceso de evaluación',
	situacion_historia: 'En Proceso',
	flg_activo: true
};

export const listaHistorias = [
	historiaCompleta,
	historiaCerrada,
	historiaEnProceso,
	{
		id_historia: 4,
		id_paciente: 4,
		id_especialista: 4,
		fecha_apertura: '2024-02-05',
		diagnostico: 'Trastorno del sueño',
		tratamiento: 'Higiene del sueño y terapia',
		observaciones: 'Mejora gradual en patrones de sueño',
		situacion_historia: 'Abierta',
		flg_activo: true
	}
];

export const historiaInvalida = {
	id_paciente: null,
	id_especialista: null,
	fecha_apertura: '',
	diagnostico: '',
	tratamiento: '',
	observaciones: '',
	situacion_historia: ''
};
