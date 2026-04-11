import sql from '../db/client.js';
import bcrypt from 'bcrypt';

/**
 * Servicio de autenticación para pacientes
 * Los pacientes inician sesión con su DNI como usuario
 */

/**
 * Verificar si un paciente está bloqueado
 */
function estaBloqueo(bloqueado_hasta) {
	if (!bloqueado_hasta) return false;
	return new Date(bloqueado_hasta) > new Date();
}

/**
 * Bloquear paciente por 15 minutos
 */
async function bloquearPaciente(dni) {
	const bloqueadoHasta = new Date(Date.now() + 15 * 60 * 1000); // 15 minutos
	await sql`
		UPDATE paciente
		SET bloqueado_hasta = ${bloqueadoHasta}
		WHERE dni = ${dni}
	`;
}

/**
 * Incrementar contador de intentos fallidos
 */
async function incrementarIntentosFallidos(dni) {
	const [paciente] = await sql`
		UPDATE paciente
		SET intentos_fallidos = intentos_fallidos + 1
		WHERE dni = ${dni}
		RETURNING intentos_fallidos
	`;

	// Si llega a 5 intentos, bloquear cuenta
	if (paciente.intentos_fallidos >= 5) {
		await bloquearPaciente(dni);
	}

	return paciente.intentos_fallidos;
}

/**
 * Resetear intentos fallidos y desbloquear
 */
async function resetearIntentosFallidos(dni) {
	await sql`
		UPDATE paciente
		SET intentos_fallidos = 0,
		    bloqueado_hasta = NULL,
		    ultimo_acceso = NOW()
		WHERE dni = ${dni}
	`;
}

/**
 * Login: Validar credenciales de paciente usando DNI como usuario
 */
export async function loginPaciente(dni, password) {
	// Buscar paciente por DNI
	const [paciente] = await sql`
		SELECT * FROM paciente
		WHERE dni = ${dni}
	`;

	if (!paciente) {
		return {
			success: false,
			error: 'DNI o contraseña incorrectos'
		};
	}

	// Verificar si está activo
	if (!paciente.flg_activo) {
		return {
			success: false,
			error: 'Cuenta desactivada. Contacte al administrador'
		};
	}

	// Verificar si está bloqueado
	if (estaBloqueo(paciente.bloqueado_hasta)) {
		return {
			success: false,
			error: 'Cuenta bloqueada temporalmente. Intente en 15 minutos'
		};
	}

	// Verificar contraseña
	const passwordValida = await bcrypt.compare(password, paciente.password_hash);

	if (!passwordValida) {
		// Incrementar intentos fallidos
		const intentos = await incrementarIntentosFallidos(dni);
		const intentosRestantes = 5 - intentos;

		if (intentosRestantes <= 0) {
			return {
				success: false,
				error: 'Cuenta bloqueada por 15 minutos debido a múltiples intentos fallidos'
			};
		}

		return {
			success: false,
			error: `DNI o contraseña incorrectos. Intentos restantes: ${intentosRestantes}`
		};
	}

	// Login exitoso: resetear intentos y actualizar último acceso
	await resetearIntentosFallidos(dni);

	// Verificar si es primer login (password_cambiado_en es NULL)
	const esPrimerLogin = paciente.password_cambiado_en === null;

	// Retornar datos del paciente (sin password_hash)
	return {
		success: true,
		requiere_cambio_password: esPrimerLogin,
		user: {
			id_paciente: paciente.id_paciente,
			dni: paciente.dni,
			nombres: paciente.nombres,
			apellidos: paciente.apellidos,
			correo: paciente.correo,
			fecha_nacimiento: paciente.fecha_nacimiento,
			sexo: paciente.sexo,
			telefono: paciente.telefono,
			tipo_usuario: 'paciente' // Identificador para distinguir del especialista
		}
	};
}

/**
 * Obtener paciente por ID para verificar sesión
 */
export async function getPacienteByIdForAuth(id) {
	const [paciente] = await sql`
		SELECT
			id_paciente,
			dni,
			nombres,
			apellidos,
			correo,
			fecha_nacimiento,
			sexo,
			telefono,
			direccion,
			contacto_emergencia,
			telefono_emergencia,
			flg_activo
		FROM paciente
		WHERE id_paciente = ${id}
	`;

	if (!paciente || !paciente.flg_activo) {
		return null;
	}

	return paciente;
}

/**
 * Cambiar contraseña de paciente
 */
export async function cambiarPasswordPaciente(id_paciente, passwordActual, passwordNueva) {
	// Obtener paciente con password_hash
	const [paciente] = await sql`
		SELECT password_hash FROM paciente
		WHERE id_paciente = ${id_paciente}
	`;

	if (!paciente) {
		return {
			success: false,
			error: 'Paciente no encontrado'
		};
	}

	// Verificar contraseña actual
	const passwordValida = await bcrypt.compare(passwordActual, paciente.password_hash);

	if (!passwordValida) {
		return {
			success: false,
			error: 'Contraseña actual incorrecta'
		};
	}

	// Hashear nueva contraseña
	const saltRounds = 10;
	const nuevoHash = await bcrypt.hash(passwordNueva, saltRounds);

	// Actualizar contraseña y registrar fecha de cambio
	await sql`
		UPDATE paciente
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NOW()
		WHERE id_paciente = ${id_paciente}
	`;

	return {
		success: true,
		message: 'Contraseña actualizada correctamente'
	};
}

/**
 * Recuperar contraseña: resetear al DNI del paciente si el correo coincide
 */
export async function recuperarPasswordPaciente(correo) {
	// Buscar paciente por correo
	const [paciente] = await sql`
		SELECT id_paciente, correo, dni, flg_activo FROM paciente
		WHERE correo = ${correo}
	`;

	if (!paciente) {
		return {
			success: false,
			error: 'No existe una cuenta registrada con ese correo electrónico'
		};
	}

	if (!paciente.flg_activo) {
		return {
			success: false,
			error: 'Cuenta desactivada. Contacte al administrador'
		};
	}

	// Hashear el DNI como nueva contraseña por defecto
	const saltRounds = 10;
	const nuevoHash = await bcrypt.hash(paciente.dni, saltRounds);

	// Actualizar contraseña y marcar como no cambiada (forzar cambio en siguiente login)
	await sql`
		UPDATE paciente
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NULL,
		    intentos_fallidos = 0,
		    bloqueado_hasta = NULL
		WHERE id_paciente = ${paciente.id_paciente}
	`;

	return {
		success: true,
		message: 'Contraseña restablecida correctamente. Su nueva contraseña es su número de DNI.'
	};
}

/**
 * Cambiar contraseña de paciente en primer login (sin validar contraseña actual)
 */
export async function cambiarPasswordPacientePrimerLogin(id_paciente, passwordNueva) {
	// Verificar que el paciente realmente esté en primer login
	const [paciente] = await sql`
		SELECT password_cambiado_en FROM paciente
		WHERE id_paciente = ${id_paciente}
	`;

	if (!paciente) {
		return {
			success: false,
			error: 'Paciente no encontrado'
		};
	}

	// Solo permitir si password_cambiado_en es NULL (primer login)
	if (paciente.password_cambiado_en !== null) {
		return {
			success: false,
			error: 'Esta funcionalidad solo está disponible en el primer inicio de sesión'
		};
	}

	// Hashear nueva contraseña
	const saltRounds = 10;
	const nuevoHash = await bcrypt.hash(passwordNueva, saltRounds);

	// Actualizar contraseña y registrar fecha de cambio
	await sql`
		UPDATE paciente
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NOW()
		WHERE id_paciente = ${id_paciente}
	`;

	return {
		success: true,
		message: 'Contraseña actualizada correctamente'
	};
}
