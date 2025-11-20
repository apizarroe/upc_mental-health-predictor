/**
 * Mocks para llamadas a la API
 * Simula respuestas de los endpoints de la aplicación
 */

import { vi } from 'vitest';

/**
 * Mock genérico de fetch con respuesta exitosa
 * @param {*} data - Datos a retornar
 * @param {boolean} success - Si la respuesta es exitosa
 * @returns {Function} Mock de fetch
 */
export function createMockFetch(data, success = true) {
	return vi.fn(() =>
		Promise.resolve({
			ok: success,
			status: success ? 200 : 400,
			json: () => Promise.resolve({ success, data })
		})
	);
}

/**
 * Mock de fetch con error
 * @param {string} error - Mensaje de error
 * @returns {Function} Mock de fetch
 */
export function createMockFetchError(error = 'Error en la petición') {
	return vi.fn(() =>
		Promise.resolve({
			ok: false,
			status: 500,
			json: () => Promise.resolve({ success: false, error })
		})
	);
}

/**
 * Mock de fetch que falla en la conexión
 * @returns {Function} Mock de fetch
 */
export function createMockFetchNetworkError() {
	return vi.fn(() => Promise.reject(new Error('Network error')));
}

/**
 * Mock del servicio de Pacientes
 */
export const mockPacientesAPI = {
	getAll: (data) => createMockFetch(data),
	getById: (paciente) => createMockFetch(paciente),
	create: (paciente) => createMockFetch(paciente),
	update: (paciente) => createMockFetch(paciente),
	delete: (paciente) => createMockFetch(paciente)
};

/**
 * Mock del servicio de Especialistas
 */
export const mockEspecialistasAPI = {
	getAll: (data) => createMockFetch(data),
	getById: (especialista) => createMockFetch(especialista),
	create: (especialista) => createMockFetch(especialista),
	update: (especialista) => createMockFetch(especialista),
	delete: (especialista) => createMockFetch(especialista)
};

/**
 * Mock del servicio de Historias Clínicas
 */
export const mockHistoriasAPI = {
	getAll: (data) => createMockFetch(data),
	getById: (historia) => createMockFetch(historia),
	create: (historia) => createMockFetch(historia),
	update: (historia) => createMockFetch(historia),
	delete: (historia) => createMockFetch(historia)
};

/**
 * Mock de respuesta de validación con errores
 * @param {Object} errors - Objeto con errores de validación
 * @returns {Function} Mock de fetch
 */
export function createMockValidationError(errors) {
	return vi.fn(() =>
		Promise.resolve({
			ok: false,
			status: 400,
			json: () =>
				Promise.resolve({
					success: false,
					error: 'Datos inválidos',
					details: errors
				})
		})
	);
}

/**
 * Mock global de fetch para testing
 * Restaura el fetch original después del test
 */
export function setupFetchMock() {
	const originalFetch = global.fetch;

	return {
		mock: (mockFn) => {
			global.fetch = mockFn;
		},
		restore: () => {
			global.fetch = originalFetch;
		}
	};
}
