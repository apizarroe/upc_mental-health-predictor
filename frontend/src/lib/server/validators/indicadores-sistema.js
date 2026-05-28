import { z } from 'zod';

export const generarReporteIndicadoresSchema = z.object({
	fecha_inicio: z
		.string()
		.regex(/^\d{4}-\d{2}-\d{2}$/, 'La fecha de inicio debe tener formato YYYY-MM-DD'),
	fecha_fin: z
		.string()
		.regex(/^\d{4}-\d{2}-\d{2}$/, 'La fecha de fin debe tener formato YYYY-MM-DD')
});
