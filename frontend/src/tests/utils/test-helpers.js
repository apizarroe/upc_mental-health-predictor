/**
 * Utilidades para testing
 * Funciones helper para facilitar la escritura de tests
 */

import { tick } from 'svelte';

/**
 * Simula el llenado de un formulario
 * @param {HTMLElement} container - Contenedor del formulario
 * @param {Object} data - Datos a llenar en el formulario
 */
export async function fillForm(container, data) {
	for (const [name, value] of Object.entries(data)) {
		const input = container.querySelector(`[name="${name}"], #${name}`);
		if (input) {
			input.value = value;
			input.dispatchEvent(new Event('input', { bubbles: true }));
			await tick();
		}
	}
}

/**
 * Simula el envío de un formulario
 * @param {HTMLElement} form - Elemento del formulario
 */
export async function submitForm(form) {
	form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
	await tick();
}

/**
 * Simula un click en un elemento
 * @param {HTMLElement} element - Elemento a hacer click
 */
export async function clickElement(element) {
	element.dispatchEvent(new MouseEvent('click', { bubbles: true }));
	await tick();
}

/**
 * Espera a que una condición se cumpla
 * @param {Function} condition - Función que retorna true cuando la condición se cumple
 * @param {number} timeout - Tiempo máximo de espera en ms
 * @param {number} interval - Intervalo de verificación en ms
 */
export async function waitFor(condition, timeout = 3000, interval = 50) {
	const startTime = Date.now();

	while (Date.now() - startTime < timeout) {
		if (condition()) {
			return true;
		}
		await new Promise((resolve) => setTimeout(resolve, interval));
	}

	throw new Error('Timeout: La condición no se cumplió en el tiempo esperado');
}

/**
 * Espera un tiempo específico
 * @param {number} ms - Milisegundos a esperar
 */
export function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Obtiene el texto de un elemento ignorando espacios extra
 * @param {HTMLElement} element - Elemento del cual obtener el texto
 * @returns {string} Texto normalizado
 */
export function getTextContent(element) {
	return element.textContent.trim().replace(/\s+/g, ' ');
}

/**
 * Verifica si un elemento tiene una clase CSS
 * @param {HTMLElement} element - Elemento a verificar
 * @param {string} className - Nombre de la clase
 * @returns {boolean}
 */
export function hasClass(element, className) {
	return element.classList.contains(className);
}

/**
 * Obtiene todos los mensajes de error en un formulario
 * @param {HTMLElement} container - Contenedor del formulario
 * @returns {Array<string>} Array de mensajes de error
 */
export function getFormErrors(container) {
	const errorElements = container.querySelectorAll('.text-red-500, .error-message');
	return Array.from(errorElements).map((el) => getTextContent(el));
}

/**
 * Verifica si un input tiene un error
 * @param {HTMLElement} input - Input a verificar
 * @returns {boolean}
 */
export function hasInputError(input) {
	return hasClass(input, 'border-red-500') || hasClass(input, 'error');
}

/**
 * Limpia todos los inputs de un formulario
 * @param {HTMLElement} container - Contenedor del formulario
 */
export async function clearForm(container) {
	const inputs = container.querySelectorAll('input, textarea, select');
	for (const input of inputs) {
		if (input.type === 'checkbox' || input.type === 'radio') {
			input.checked = false;
		} else {
			input.value = '';
		}
		input.dispatchEvent(new Event('input', { bubbles: true }));
	}
	await tick();
}

/**
 * Simula escribir texto en un input con delay
 * @param {HTMLElement} input - Input donde escribir
 * @param {string} text - Texto a escribir
 * @param {number} delay - Delay entre caracteres en ms
 */
export async function typeText(input, text, delay = 50) {
	input.value = '';
	for (const char of text) {
		input.value += char;
		input.dispatchEvent(new Event('input', { bubbles: true }));
		await sleep(delay);
	}
}

/**
 * Obtiene el valor de un input por su name o id
 * @param {HTMLElement} container - Contenedor
 * @param {string} identifier - Name o id del input
 * @returns {string|null}
 */
export function getInputValue(container, identifier) {
	const input = container.querySelector(`[name="${identifier}"], #${identifier}`);
	return input ? input.value : null;
}

/**
 * Verifica si un botón está deshabilitado
 * @param {HTMLElement} button - Botón a verificar
 * @returns {boolean}
 */
export function isButtonDisabled(button) {
	return button.disabled || button.hasAttribute('disabled');
}
