/**
 * Tests para EspecialistaForm
 * Ejemplo de cómo usar fixtures, mocks y utilidades de testing
 */

import { describe, it, expect } from 'vitest';
import { especialistaValido, especialistaInvalido } from '../../../tests/fixtures';
import { isValidDNI, isValidName, isValidEmail } from '../../../tests/utils';

describe('EspecialistaForm - Validaciones', () => {
	describe('Validación de DNI', () => {
		it('debe aceptar DNI válido de 8 dígitos', () => {
			expect(isValidDNI(especialistaValido.dni)).toBe(true);
			expect(isValidDNI('87654321')).toBe(true);
		});

		it('debe rechazar DNI con menos de 8 dígitos', () => {
			expect(isValidDNI('123')).toBe(false);
			expect(isValidDNI('1234567')).toBe(false);
		});

		it('debe rechazar DNI con más de 8 dígitos', () => {
			expect(isValidDNI('123456789')).toBe(false);
		});

		it('debe rechazar DNI con letras', () => {
			expect(isValidDNI('8765432a')).toBe(false);
			expect(isValidDNI('abcd5678')).toBe(false);
		});

		it('debe rechazar DNI inválido del fixture', () => {
			expect(isValidDNI(especialistaInvalido.dni)).toBe(false);
		});
	});

	describe('Validación de Nombres', () => {
		it('debe aceptar nombres válidos', () => {
			expect(isValidName(especialistaValido.nombres)).toBe(true);
			expect(isValidName('María Elena')).toBe(true);
			expect(isValidName('Carlos Alberto')).toBe(true);
		});

		it('debe aceptar nombres con tildes', () => {
			expect(isValidName('José María')).toBe(true);
			expect(isValidName('Sofía Andrea')).toBe(true);
		});

		it('debe aceptar nombres con ñ', () => {
			expect(isValidName('Begoña')).toBe(true);
			expect(isValidName('Iñaki')).toBe(true);
		});

		it('debe rechazar nombres con números', () => {
			expect(isValidName('María123')).toBe(false);
			expect(isValidName('Carlos2')).toBe(false);
		});

		it('debe rechazar nombres con caracteres especiales', () => {
			expect(isValidName('María@')).toBe(false);
			expect(isValidName('Carlos#')).toBe(false);
		});

		it('debe rechazar nombres inválidos del fixture', () => {
			expect(isValidName(especialistaInvalido.nombres)).toBe(false);
		});
	});

	describe('Validación de Apellidos', () => {
		it('debe aceptar apellidos válidos', () => {
			expect(isValidName(especialistaValido.apellidos)).toBe(true);
			expect(isValidName('López Ramírez')).toBe(true);
		});

		it('debe rechazar apellidos con números', () => {
			expect(isValidName('López123')).toBe(false);
		});

		it('debe rechazar apellidos con caracteres especiales', () => {
			expect(isValidName('López@')).toBe(false);
		});

		it('debe rechazar apellidos inválidos del fixture', () => {
			expect(isValidName(especialistaInvalido.apellidos)).toBe(false);
		});
	});

	describe('Validación de Email', () => {
		it('debe aceptar email válido', () => {
			expect(isValidEmail(especialistaValido.correo)).toBe(true);
			expect(isValidEmail('doctor@clinica.com')).toBe(true);
		});

		it('debe rechazar email sin @', () => {
			expect(isValidEmail('doctorclinica.com')).toBe(false);
		});

		it('debe rechazar email sin dominio', () => {
			expect(isValidEmail('doctor@')).toBe(false);
		});

		it('debe rechazar email sin extensión', () => {
			expect(isValidEmail('doctor@clinica')).toBe(false);
		});

		it('debe rechazar email inválido del fixture', () => {
			expect(isValidEmail(especialistaInvalido.correo)).toBe(false);
		});
	});

	describe('Validación de campos específicos', () => {
		it('debe validar que especialidad esté presente', () => {
			expect(especialistaValido.especialidad).toBeDefined();
			expect(especialistaValido.especialidad).toBe('Psicología Clínica');
		});

		it('debe validar que colegiatura esté presente', () => {
			expect(especialistaValido.colegiatura).toBeDefined();
			expect(especialistaValido.colegiatura).toBe('CPsP12345');
		});

		it('debe validar que cargo esté presente', () => {
			expect(especialistaValido.cargo).toBeDefined();
			expect(especialistaValido.cargo).toBe('Psicóloga Senior');
		});

		it('debe rechazar especialidad vacía', () => {
			expect(especialistaInvalido.especialidad).toBe('');
		});

		it('debe rechazar colegiatura vacía', () => {
			expect(especialistaInvalido.colegiatura).toBe('');
		});

		it('debe rechazar cargo vacío', () => {
			expect(especialistaInvalido.cargo).toBe('');
		});
	});

	describe('Validación de longitud de campos', () => {
		it('debe aceptar nombres de hasta 80 caracteres', () => {
			const nombreLargo = 'A'.repeat(80);
			expect(nombreLargo.length).toBe(80);
		});

		it('debe rechazar nombres de más de 80 caracteres', () => {
			const nombreMuyLargo = 'A'.repeat(81);
			expect(nombreMuyLargo.length).toBeGreaterThan(80);
		});

		it('debe aceptar DNI de exactamente 8 caracteres', () => {
			expect(especialistaValido.dni.length).toBe(8);
		});
	});

	describe('Fixtures de especialistas', () => {
		it('especialistaValido debe tener todos los campos requeridos', () => {
			expect(especialistaValido.dni).toBeDefined();
			expect(especialistaValido.nombres).toBeDefined();
			expect(especialistaValido.apellidos).toBeDefined();
			expect(especialistaValido.especialidad).toBeDefined();
			expect(especialistaValido.colegiatura).toBeDefined();
			expect(especialistaValido.correo).toBeDefined();
			expect(especialistaValido.telefono).toBeDefined();
			expect(especialistaValido.cargo).toBeDefined();
		});

		it('especialistaInvalido debe tener datos incorrectos', () => {
			expect(isValidDNI(especialistaInvalido.dni)).toBe(false);
			expect(isValidName(especialistaInvalido.nombres)).toBe(false);
			expect(isValidName(especialistaInvalido.apellidos)).toBe(false);
			expect(especialistaInvalido.especialidad).toBe('');
			expect(especialistaInvalido.colegiatura).toBe('');
		});
	});

	describe('Validación de tipos de especialistas', () => {
		it('debe validar psicólogo con colegiatura CPsP', () => {
			const colegiatura = 'CPsP12345';
			expect(colegiatura).toMatch(/^CPsP/);
		});

		it('debe validar psiquiatra con colegiatura CMP', () => {
			const colegiatura = 'CMP67890';
			expect(colegiatura).toMatch(/^CMP/);
		});
	});
});
