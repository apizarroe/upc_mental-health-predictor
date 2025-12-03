import { z } from 'zod';

/**
 * Esquema de validación para crear un especialista
 * Basado en la tabla 'especialista' de la base de datos
 * El campo flg_activo se setea automáticamente en el servicio
 */
export const createEspecialistaSchema = z.object({
	dni: z.string().max(12),
	nombres: z.string().max(80),
	apellidos: z.string().max(80),
	especialidad: z.string().max(50),
	colegiatura: z.string().max(20),
	correo: z.string().email().max(50),
	telefono: z.string().max(20),
	cargo: z.string().max(50)
});

/**
 * Esquema de validación para actualizar un especialista
 * Todos los campos son opcionales en la actualización
 */
export const updateEspecialistaSchema = z.object({
	dni: z.string().max(12).optional(),
	nombres: z.string().max(80).optional(),
	apellidos: z.string().max(80).optional(),
	especialidad: z.string().max(50).optional(),
	colegiatura: z.string().max(20).optional(),
	correo: z.string().email().max(50).optional(),
	telefono: z.string().max(20).optional(),
	cargo: z.string().max(50).optional(),
	flg_activo: z.boolean().optional()
});
