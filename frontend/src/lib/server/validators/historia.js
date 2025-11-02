import { z } from 'zod';

export const historiaClinicaSchema = z.object({
	id_paciente: z.number().int().positive('ID de paciente debe ser positivo'),
	especialista_apertura: z.number().int().positive('ID de especialista debe ser positivo'),
	servicio_origen: z.string().max(100).optional(),
	antecedentes_personales: z.string().optional(),
	antecedentes_familiares: z.string().optional(),
	antecedentes_psicosociales: z.string().optional(),
	habitos_personales: z.string().optional(),
	situacion_familiar: z.string().optional(),
	situacion_laboral: z.string().optional(),
	evaluacion_inicial: z.string().optional(),
	diagnostico_inicial: z.string().optional(),
	tratamientos_previos: z.string().optional(),
	situacion_historia: z.string().max(20).optional()
});

export const updateHistoriaSchema = z.object({
	servicio_origen: z.string().max(100).optional(),
	antecedentes_personales: z.string().optional(),
	antecedentes_familiares: z.string().optional(),
	antecedentes_psicosociales: z.string().optional(),
	habitos_personales: z.string().optional(),
	situacion_familiar: z.string().optional(),
	situacion_laboral: z.string().optional(),
	evaluacion_inicial: z.string().optional(),
	diagnostico_inicial: z.string().optional(),
	tratamientos_previos: z.string().optional(),
	situacion_historia: z.string().max(20).optional()
});

export const cerrarHistoriaSchema = z.object({
	motivo_cierre: z.string().min(1, 'El motivo de cierre es requerido')
});

export const medicacionSchema = z.object({
	id_historia: z.number().int().positive(),
	medicacion: z.string().min(1, 'El nombre del medicamento es requerido').max(150),
	concentracion: z.string().max(50).optional(),
	forma_farmaceutica: z.string().max(50).optional(),
	dosis: z.string().max(50).optional(),
	frecuencia: z.string().max(50).optional(),
	anio_inicio: z.number().int().min(1900).max(new Date().getFullYear()).optional(),
	tipo_medicacion: z.string().max(50).optional(),
	prescrito_por: z.string().max(100).optional(),
	observaciones: z.string().optional()
});
