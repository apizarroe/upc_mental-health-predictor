/**
 * Utilidades para testing de validaciones
 * Helpers específicos para validar datos de formularios
 */

/**
 * Valida que un DNI sea válido (8 dígitos numéricos)
 * @param {string} dni - DNI a validar
 * @returns {boolean}
 */
export function isValidDNI(dni) {
	return /^\d{8}$/.test(dni);
}

/**
 * Valida que un nombre/apellido contenga solo letras y espacios
 * @param {string} text - Texto a validar
 * @returns {boolean}
 */
export function isValidName(text) {
	return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(text);
}

/**
 * Valida que un email sea válido
 * @param {string} email - Email a validar
 * @returns {boolean}
 */
export function isValidEmail(email) {
	return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Valida que un teléfono sea válido (9 dígitos numéricos)
 * @param {string} telefono - Teléfono a validar
 * @returns {boolean}
 */
export function isValidTelefono(telefono) {
	return /^\d{9}$/.test(telefono);
}

/**
 * Valida la longitud de un texto
 * @param {string} text - Texto a validar
 * @param {number} max - Longitud máxima
 * @param {number} min - Longitud mínima
 * @returns {boolean}
 */
export function isValidLength(text, max, min = 0) {
	const length = text.length;
	return length >= min && length <= max;
}

/**
 * Valida que una fecha sea válida y no sea futura
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @returns {boolean}
 */
export function isValidBirthDate(date) {
	if (!date) return false;
	const birthDate = new Date(date);
	const today = new Date();
	return birthDate <= today && !isNaN(birthDate.getTime());
}

/**
 * Genera errores de validación esperados para un paciente inválido
 * @param {Object} paciente - Datos del paciente
 * @returns {Object} Objeto con errores esperados
 */
export function getExpectedPacienteErrors(paciente) {
	const errors = {};

	if (!paciente.dni || !isValidDNI(paciente.dni)) {
		errors.dni = 'DNI debe tener exactamente 8 dígitos numéricos';
	}

	if (!paciente.nombres) {
		errors.nombres = 'Nombres son requeridos';
	} else if (!isValidName(paciente.nombres)) {
		errors.nombres = 'Los nombres solo pueden contener letras y espacios';
	} else if (!isValidLength(paciente.nombres, 80)) {
		errors.nombres = 'Los nombres no pueden superar los 80 caracteres';
	}

	if (!paciente.apellidos) {
		errors.apellidos = 'Apellidos son requeridos';
	} else if (!isValidName(paciente.apellidos)) {
		errors.apellidos = 'Los apellidos solo pueden contener letras y espacios';
	} else if (!isValidLength(paciente.apellidos, 80)) {
		errors.apellidos = 'Los apellidos no pueden superar los 80 caracteres';
	}

	if (!paciente.fecha_nacimiento) {
		errors.fecha_nacimiento = 'Fecha de nacimiento es requerida';
	}

	if (!paciente.direccion) {
		errors.direccion = 'Dirección es requerida';
	}

	if (!paciente.telefono) {
		errors.telefono = 'Teléfono es requerido';
	} else if (!isValidTelefono(paciente.telefono)) {
		errors.telefono = 'El teléfono debe tener exactamente 9 dígitos numéricos';
	}

	if (!paciente.correo) {
		errors.correo = 'Correo es requerido';
	} else if (!isValidEmail(paciente.correo)) {
		errors.correo = 'Correo inválido';
	}

	if (!paciente.contacto_emergencia) {
		errors.contacto_emergencia = 'Contacto de emergencia es requerido';
	} else if (!isValidName(paciente.contacto_emergencia)) {
		errors.contacto_emergencia = 'El contacto de emergencia solo puede contener letras y espacios';
	}

	if (!paciente.telefono_emergencia) {
		errors.telefono_emergencia = 'Teléfono de emergencia es requerido';
	} else if (!isValidTelefono(paciente.telefono_emergencia)) {
		errors.telefono_emergencia = 'El teléfono de emergencia debe tener exactamente 9 dígitos numéricos';
	}

	return errors;
}

/**
 * Genera errores de validación esperados para un especialista inválido
 * @param {Object} especialista - Datos del especialista
 * @returns {Object} Objeto con errores esperados
 */
export function getExpectedEspecialistaErrors(especialista) {
	const errors = {};

	if (!especialista.dni || !isValidDNI(especialista.dni)) {
		errors.dni = 'DNI debe tener exactamente 8 dígitos numéricos';
	}

	if (!especialista.nombres) {
		errors.nombres = 'Nombres son requeridos';
	} else if (!isValidName(especialista.nombres)) {
		errors.nombres = 'Los nombres solo pueden contener letras y espacios';
	} else if (!isValidLength(especialista.nombres, 80)) {
		errors.nombres = 'Los nombres no pueden superar los 80 caracteres';
	}

	if (!especialista.apellidos) {
		errors.apellidos = 'Apellidos son requeridos';
	} else if (!isValidName(especialista.apellidos)) {
		errors.apellidos = 'Los apellidos solo pueden contener letras y espacios';
	} else if (!isValidLength(especialista.apellidos, 80)) {
		errors.apellidos = 'Los apellidos no pueden superar los 80 caracteres';
	}

	if (!especialista.especialidad) {
		errors.especialidad = 'Especialidad es requerida';
	}

	if (!especialista.colegiatura) {
		errors.colegiatura = 'Colegiatura es requerida';
	}

	if (!especialista.telefono) {
		errors.telefono = 'Teléfono es requerido';
	} else if (!isValidTelefono(especialista.telefono)) {
		errors.telefono = 'El teléfono debe tener exactamente 9 dígitos numéricos';
	}

	if (!especialista.correo) {
		errors.correo = 'Correo es requerido';
	} else if (!isValidEmail(especialista.correo)) {
		errors.correo = 'Correo inválido';
	}

	if (!especialista.cargo) {
		errors.cargo = 'Cargo es requerido';
	}

	return errors;
}
