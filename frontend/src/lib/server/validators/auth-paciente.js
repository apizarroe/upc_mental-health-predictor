import { z } from 'zod';

/**
 * Esquema de validación para login de pacientes
 * Los pacientes usan su DNI como usuario
 */
export const loginPacienteSchema = z.object({
	dni: z.string()
		.min(8, 'El DNI debe tener al menos 8 dígitos')
		.max(12, 'El DNI no puede tener más de 12 caracteres')
		.regex(/^[0-9]+$/, 'El DNI solo debe contener números'),
	password: z.string().min(1, 'Contraseña es requerida')
});

/**
 * Esquema de validación para contraseñas (reutilizable)
 * Mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número
 */
export const passwordSchema = z
	.string()
	.min(8, 'La contraseña debe tener al menos 8 caracteres')
	.regex(/[A-Z]/, 'La contraseña debe contener al menos una letra mayúscula')
	.regex(/[a-z]/, 'La contraseña debe contener al menos una letra minúscula')
	.regex(/[0-9]/, 'La contraseña debe contener al menos un número');

/**
 * Esquema de validación para cambio de contraseña de paciente
 */
export const cambiarPasswordPacienteSchema = z.object({
	passwordActual: z.string().min(1, 'Contraseña actual es requerida'),
	passwordNueva: passwordSchema,
	passwordConfirmacion: z.string().min(1, 'Confirmación de contraseña es requerida')
}).refine((data) => data.passwordNueva === data.passwordConfirmacion, {
	message: 'Las contraseñas no coinciden',
	path: ['passwordConfirmacion']
});
