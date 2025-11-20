/**
 * Mocks para navegación de SvelteKit
 * Simula funciones de navegación como goto
 */

import { vi } from 'vitest';

/**
 * Mock de la función goto de SvelteKit
 * @returns {Function} Mock de goto
 */
export function createMockGoto() {
	return vi.fn((url) => Promise.resolve());
}

/**
 * Mock del módulo $app/navigation completo
 */
export const mockNavigation = {
	goto: createMockGoto(),
	invalidate: vi.fn(),
	invalidateAll: vi.fn(),
	preloadData: vi.fn(),
	preloadCode: vi.fn()
};

/**
 * Helper para configurar mocks de navegación en tests
 */
export function setupNavigationMocks() {
	vi.mock('$app/navigation', () => ({
		goto: createMockGoto(),
		invalidate: vi.fn(),
		invalidateAll: vi.fn(),
		preloadData: vi.fn(),
		preloadCode: vi.fn()
	}));
}
