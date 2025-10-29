import { z } from 'zod';

/**
 * Esquema de validación para crear un paciente
 * Basado en la tabla 'paciente' de la base de datos
 * Los campos fecha_registro y flg_activo se setean automáticamente en el servicio
 */
export const createPacienteSchema = z.object({
	dni: z.string().max(12),
	nombres: z.string().max(80),
	apellidos: z.string().max(80),
	fecha_nacimiento: z.string(), // Formato: YYYY-MM-DD
	sexo: z.enum(['M', 'F']),
	direccion: z.string().max(255),
	telefono: z.string().max(20),
	correo: z.string().email().max(50),
	contacto_emergencia: z.string().max(150),
	telefono_emergencia: z.string().max(20)
});

/**
 * Esquema de validación para actualizar un paciente
 * Todos los campos son opcionales en la actualización
 */
export const updatePacienteSchema = z.object({
	dni: z.string().max(12).optional(),
	nombres: z.string().max(80).optional(),
	apellidos: z.string().max(80).optional(),
	fecha_nacimiento: z.string().optional(),
	sexo: z.enum(['M', 'F']).optional(),
	direccion: z.string().max(255).optional(),
	telefono: z.string().max(20).optional(),
	correo: z.string().email().max(50).optional(),
	contacto_emergencia: z.string().max(150).optional(),
	telefono_emergencia: z.string().max(20).optional(),
	flg_activo: z.boolean().optional()
});
