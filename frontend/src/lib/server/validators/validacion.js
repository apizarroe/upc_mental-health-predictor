import { z } from 'zod';

export const decisionValidacionSchema = z.enum(['aceptar', 'rechazar', 'modificar']);

export const diagnosticoEspecialistaSchema = z.object({
	depression: z.boolean(),
	anxiety: z.boolean()
});

export const saveValidacionSchema = z.object({
	decision: decisionValidacionSchema,
	diagnosticoEspecialista: diagnosticoEspecialistaSchema,
	nivelConfianza: z.coerce.number().int().min(0).max(100).nullable().optional(),
	observaciones: z.string().max(2000).nullable().optional(),
	recomendacionPaciente: z.string().max(2000).nullable().optional(),
	requiereSeguimiento: z.boolean().optional().default(false)
});
