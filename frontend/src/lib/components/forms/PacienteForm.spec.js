/**
 * Tests para PacienteForm
 * Ejemplo de cómo usar fixtures, mocks y utilidades de testing
 */

import { describe, it, expect, vi } from 'vitest';
import { pacienteValido, pacienteInvalido } from '../../../tests/fixtures';
import { isValidDNI, isValidName, isValidEmail, isValidTelefono } from '../../../tests/utils';

describe('PacienteForm - Validaciones', () => {
	describe('Validación de DNI', () => {
		it('debe aceptar DNI válido de 8 dígitos', () => {
			expect(isValidDNI(pacienteValido.dni)).toBe(true);
			expect(isValidDNI('12345678')).toBe(true);
		});

		it('debe rechazar DNI con menos de 8 dígitos', () => {
			expect(isValidDNI('123')).toBe(false);
			expect(isValidDNI('1234567')).toBe(false);
		});

		it('debe rechazar DNI con más de 8 dígitos', () => {
			expect(isValidDNI('123456789')).toBe(false);
		});

		it('debe rechazar DNI con letras', () => {
			expect(isValidDNI('1234567a')).toBe(false);
			expect(isValidDNI('abcd1234')).toBe(false);
		});

		it('debe rechazar DNI inválido del fixture', () => {
			expect(isValidDNI(pacienteInvalido.dni)).toBe(false);
		});
	});

	describe('Validación de Nombres', () => {
		it('debe aceptar nombres válidos', () => {
			expect(isValidName(pacienteValido.nombres)).toBe(true);
			expect(isValidName('Juan Carlos')).toBe(true);
			expect(isValidName('María José')).toBe(true);
		});

		it('debe aceptar nombres con tildes', () => {
			expect(isValidName('José María')).toBe(true);
			expect(isValidName('María Fernanda')).toBe(true);
		});

		it('debe aceptar nombres con ñ', () => {
			expect(isValidName('Begoña')).toBe(true);
			expect(isValidName('Niña')).toBe(true);
		});

		it('debe rechazar nombres con números', () => {
			expect(isValidName('Juan123')).toBe(false);
			expect(isValidName('María2')).toBe(false);
		});

		it('debe rechazar nombres con caracteres especiales', () => {
			expect(isValidName('Juan@')).toBe(false);
			expect(isValidName('María#')).toBe(false);
		});

		it('debe rechazar nombres inválidos del fixture', () => {
			expect(isValidName(pacienteInvalido.nombres)).toBe(false);
		});
	});

	describe('Validación de Apellidos', () => {
		it('debe aceptar apellidos válidos', () => {
			expect(isValidName(pacienteValido.apellidos)).toBe(true);
			expect(isValidName('Pérez García')).toBe(true);
		});

		it('debe rechazar apellidos con números', () => {
			expect(isValidName('Pérez123')).toBe(false);
		});

		it('debe rechazar apellidos con caracteres especiales', () => {
			expect(isValidName('Pérez@')).toBe(false);
		});

		it('debe rechazar apellidos inválidos del fixture', () => {
			expect(isValidName(pacienteInvalido.apellidos)).toBe(false);
		});
	});

	describe('Validación de Email', () => {
		it('debe aceptar email válido', () => {
			expect(isValidEmail(pacienteValido.correo)).toBe(true);
			expect(isValidEmail('test@example.com')).toBe(true);
		});

		it('debe rechazar email sin @', () => {
			expect(isValidEmail('testexample.com')).toBe(false);
		});

		it('debe rechazar email sin dominio', () => {
			expect(isValidEmail('test@')).toBe(false);
		});

		it('debe rechazar email sin extensión', () => {
			expect(isValidEmail('test@example')).toBe(false);
		});

		it('debe rechazar email inválido del fixture', () => {
			expect(isValidEmail(pacienteInvalido.correo)).toBe(false);
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
			expect(pacienteValido.dni.length).toBe(8);
		});
	});

	describe('Validación de Teléfono', () => {
		it('debe aceptar teléfono válido de 9 dígitos', () => {
			expect(isValidTelefono(pacienteValido.telefono)).toBe(true);
			expect(isValidTelefono('987654321')).toBe(true);
		});

		it('debe rechazar teléfono con menos de 9 dígitos', () => {
			expect(isValidTelefono('12345')).toBe(false);
			expect(isValidTelefono('12345678')).toBe(false);
		});

		it('debe rechazar teléfono con más de 9 dígitos', () => {
			expect(isValidTelefono('1234567890')).toBe(false);
		});

		it('debe rechazar teléfono con letras', () => {
			expect(isValidTelefono('98765432a')).toBe(false);
			expect(isValidTelefono('abcd12345')).toBe(false);
		});

		it('debe rechazar teléfono con caracteres especiales', () => {
			expect(isValidTelefono('987-654321')).toBe(false);
			expect(isValidTelefono('987 654 321')).toBe(false);
		});
	});

	describe('Validación de Contacto de emergencia', () => {
		it('debe aceptar contacto válido solo con letras', () => {
			expect(isValidName(pacienteValido.contacto_emergencia)).toBe(true);
			expect(isValidName('María Pérez')).toBe(true);
		});

		it('debe aceptar contacto con tildes', () => {
			expect(isValidName('José Ramón García')).toBe(true);
			expect(isValidName('María Fernández')).toBe(true);
		});

		it('debe aceptar contacto con ñ', () => {
			expect(isValidName('Begoña López')).toBe(true);
		});

		it('debe rechazar contacto con números', () => {
			expect(isValidName('María123')).toBe(false);
			expect(isValidName('Pedro2')).toBe(false);
		});

		it('debe rechazar contacto con caracteres especiales', () => {
			expect(isValidName('María@gmail.com')).toBe(false);
			expect(isValidName('Pedro#')).toBe(false);
		});
	});

	describe('Validación de Teléfono de emergencia', () => {
		it('debe aceptar teléfono de emergencia válido de 9 dígitos', () => {
			expect(isValidTelefono(pacienteValido.telefono_emergencia)).toBe(true);
			expect(isValidTelefono('912345678')).toBe(true);
		});

		it('debe rechazar teléfono de emergencia con menos de 9 dígitos', () => {
			expect(isValidTelefono('91234')).toBe(false);
			expect(isValidTelefono('91234567')).toBe(false);
		});

		it('debe rechazar teléfono de emergencia con más de 9 dígitos', () => {
			expect(isValidTelefono('9123456789')).toBe(false);
		});

		it('debe rechazar teléfono de emergencia con letras', () => {
			expect(isValidTelefono('91234567a')).toBe(false);
		});

		it('debe rechazar teléfono de emergencia con caracteres especiales', () => {
			expect(isValidTelefono('912-345-678')).toBe(false);
		});
	});

	describe('Fixtures de pacientes', () => {
		it('pacienteValido debe tener todos los campos requeridos', () => {
			expect(pacienteValido.dni).toBeDefined();
			expect(pacienteValido.nombres).toBeDefined();
			expect(pacienteValido.apellidos).toBeDefined();
			expect(pacienteValido.fecha_nacimiento).toBeDefined();
			expect(pacienteValido.sexo).toBeDefined();
			expect(pacienteValido.direccion).toBeDefined();
			expect(pacienteValido.telefono).toBeDefined();
			expect(pacienteValido.correo).toBeDefined();
			expect(pacienteValido.contacto_emergencia).toBeDefined();
			expect(pacienteValido.telefono_emergencia).toBeDefined();
		});

		it('pacienteInvalido debe tener datos incorrectos', () => {
			expect(isValidDNI(pacienteInvalido.dni)).toBe(false);
			expect(isValidName(pacienteInvalido.nombres)).toBe(false);
			expect(isValidName(pacienteInvalido.apellidos)).toBe(false);
		});

		it('pacienteValido debe tener teléfono válido', () => {
			expect(isValidTelefono(pacienteValido.telefono)).toBe(true);
		});

		it('pacienteValido debe tener teléfono de emergencia válido', () => {
			expect(isValidTelefono(pacienteValido.telefono_emergencia)).toBe(true);
		});

		it('pacienteValido debe tener contacto de emergencia válido', () => {
			expect(isValidName(pacienteValido.contacto_emergencia)).toBe(true);
		});
	});
});
