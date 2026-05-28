import { describe, expect, it } from 'vitest';
import {
	construirResumenPruebasRecomendadas,
	generarCsvReporte,
	validarRangoReporte
} from './system-reports.js';

describe('system-reports utils', () => {
	it('rechaza rangos mayores a 4 meses', () => {
		const result = validarRangoReporte('2026-01-01', '2026-05-02');

		expect(result.ok).toBe(false);
		expect(result.error).toContain('4 meses');
	});

	it('acepta rangos válidos y construye timestamps', () => {
		const result = validarRangoReporte('2026-01-01', '2026-04-30');

		expect(result.ok).toBe(true);
		expect(result.inicioTimestamp).toBe('2026-01-01 00:00:00');
		expect(result.finExclusiveTimestamp).toBe('2026-05-01 00:00:00');
	});

	it('agrega recomendaciones de pruebas por condición y por prueba', () => {
		const result = construirResumenPruebasRecomendadas([
			{ id_paciente: 1, promedio_depresion: 40, promedio_ansiedad: 10 },
			{ id_paciente: 2, promedio_depresion: 15, promedio_ansiedad: 60 },
			{ id_paciente: 3, promedio_depresion: 55, promedio_ansiedad: 70 }
		]);

		expect(result.pacientes_con_recomendacion).toBe(3);
		expect(result.por_condicion.depression.pacientes).toBe(2);
		expect(result.por_condicion.anxiety.pacientes).toBe(2);
		expect(result.total_recomendaciones).toBe(12);
		expect(result.por_prueba).toEqual(
			expect.arrayContaining([
				expect.objectContaining({
					nombre: 'Cuestionario de Salud del Paciente (PHQ-9)',
					total: 2
				}),
				expect.objectContaining({
					nombre: 'Escala de Ansiedad Generalizada (GAD-7)',
					total: 2
				})
			])
		);
	});

	it('genera CSV a partir del snapshot persistido', () => {
		const csv = generarCsvReporte({
			id_reporte: 9,
			fecha_generacion: '2026-05-27T10:00:00.000Z',
			fecha_inicio: '2026-05-01',
			fecha_fin: '2026-05-27',
			indicadores_json: {
				metadata: {
					usuario_solicitante: 'Maria Gonzalez'
				},
				totales: {
					pacientes_atendidos: 8,
					notas_analizadas: 12,
					diagnosticos_sugeridos: 6,
					diagnosticos_aceptados: 5
				},
				pruebas_psicologicas_recomendadas: {
					total_recomendaciones: 4,
					por_condicion: {
						depression: { pacientes: 1, recomendaciones: 2 },
						anxiety: { pacientes: 1, recomendaciones: 2 }
					},
					por_prueba: [{ condicion: 'depression', nombre: 'PHQ-9', total: 1 }]
				}
			}
		});

		expect(csv).toContain('metadata,id_reporte,9');
		expect(csv).toContain('totales,pacientes_atendidos,8');
		expect(csv).toContain('pruebas_por_prueba,depression:PHQ-9,1');
	});
});
