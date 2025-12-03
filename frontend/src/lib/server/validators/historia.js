import { z } from 'zod';

// Schema para antecedentes familiares (JSONB)
const antecedentesFamiliaresSchema = z.object({
	depresion: z.boolean().optional(),
	ansiedad: z.boolean().optional(),
	bipolaridad: z.boolean().optional(),
	esquizofrenia: z.boolean().optional(),
	tdah: z.boolean().optional(),
	toc: z.boolean().optional(),
	adicciones: z.boolean().optional(),
	suicidio: z.boolean().optional(),
	otros: z.string().optional()
}).optional();

// Schema para hábitos personales (JSONB)
const habitosPersonalesSchema = z.object({
	alcohol: z.string().optional(),
	alcohol_frecuencia: z.string().optional(),
	tabaco: z.string().optional(),
	tabaco_frecuencia: z.string().optional(),
	drogas: z.string().optional(),
	drogas_frecuencia: z.string().optional(),
	sueño_horas: z.string().optional(),
	sueño_calidad: z.string().optional(),
	alimentacion: z.string().optional(),
	ejercicio: z.string().optional(),
	otros: z.string().optional()
}).optional();

export const historiaClinicaSchema = z.object({
	id_paciente: z.number().int().positive('ID de paciente debe ser positivo'),
	especialista_apertura: z.number().int().positive('ID de especialista debe ser positivo'),
	servicio_origen: z.string().max(100).optional(),
	antecedentes_personales: z.string().optional(),
	antecedentes_familiares: antecedentesFamiliaresSchema,
	antecedentes_psicosociales: z.string().optional(),
	habitos_personales: habitosPersonalesSchema,
	situacion_familiar: z.string().optional(),
	situacion_laboral: z.string().optional(),
	evaluacion_inicial: z.string().optional(),
	diagnostico_inicial: z.string().optional(),
	tratamientos_previos: z.string().optional(),
	situacion_historia: z.string().max(30).optional()
});

export const updateHistoriaSchema = z.object({
	servicio_origen: z.string().max(100).optional(),
	antecedentes_personales: z.string().optional(),
	antecedentes_familiares: antecedentesFamiliaresSchema,
	antecedentes_psicosociales: z.string().optional(),
	habitos_personales: habitosPersonalesSchema,
	situacion_familiar: z.string().optional(),
	situacion_laboral: z.string().optional(),
	evaluacion_inicial: z.string().optional(),
	diagnostico_inicial: z.string().optional(),
	tratamientos_previos: z.string().optional(),
	situacion_historia: z.string().max(30).optional(),
	motivo_cierre: z.string().optional().nullable()
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
