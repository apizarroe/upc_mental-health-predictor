import { z } from 'zod';

// Función para contar palabras en un texto
function contarPalabras(texto) {
	return texto.trim().split(/\s+/).filter(palabra => palabra.length > 0).length;
}

// Validador personalizado para respuestas con mínimo de palabras
const validarRespuesta = z.string()
	.min(1, 'La respuesta es obligatoria')
	.refine(
		(texto) => contarPalabras(texto) >= 10,
		{ message: 'La respuesta debe tener al menos 10 palabras' }
	)
	.refine(
		(texto) => texto.length <= 1000,
		{ message: 'La respuesta no puede exceder 1000 caracteres' }
	);

// Schema para las respuestas del cuestionario
const respuestasSchema = z.object({
	question1: validarRespuesta,
	question2: validarRespuesta,
	question3: validarRespuesta,
	question4: validarRespuesta
});

export const pacienteRespuestaSchema = z.object({
	id_paciente: z.number().int().positive('ID de paciente debe ser positivo'),
	respuestas: respuestasSchema
});
