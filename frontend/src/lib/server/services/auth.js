import sql from '../db/client.js';
import bcrypt from 'bcrypt';

/**
 * Servicio de autenticación
 */

/**
 * Verificar si un usuario está bloqueado
 */
function estaBloqueo(bloqueado_hasta) {
	if (!bloqueado_hasta) return false;
	return new Date(bloqueado_hasta) > new Date();
}

/**
 * Bloquear usuario por 15 minutos
 */
async function bloquearUsuario(usuario) {
	const bloqueadoHasta = new Date(Date.now() + 15 * 60 * 1000); // 15 minutos
	await sql`
		UPDATE especialista
		SET bloqueado_hasta = ${bloqueadoHasta}
		WHERE usuario = ${usuario}
	`;
}

/**
 * Incrementar contador de intentos fallidos
 */
async function incrementarIntentosFallidos(usuario) {
	const [especialista] = await sql`
		UPDATE especialista
		SET intentos_fallidos = intentos_fallidos + 1
		WHERE usuario = ${usuario}
		RETURNING intentos_fallidos
	`;

	// Si llega a 5 intentos, bloquear cuenta
	if (especialista.intentos_fallidos >= 5) {
		await bloquearUsuario(usuario);
	}

	return especialista.intentos_fallidos;
}

/**
 * Resetear intentos fallidos y desbloquear
 */
async function resetearIntentosFallidos(usuario) {
	await sql`
		UPDATE especialista
		SET intentos_fallidos = 0,
		    bloqueado_hasta = NULL,
		    ultimo_acceso = NOW()
		WHERE usuario = ${usuario}
	`;
}

/**
 * Login: Validar credenciales y retornar datos del usuario
 */
export async function login(usuario, password) {
	// Buscar usuario
	const [especialista] = await sql`
		SELECT * FROM especialista
		WHERE usuario = ${usuario}
	`;

	if (!especialista) {
		return {
			success: false,
			error: 'Usuario o contraseña incorrectos'
		};
	}

	// Verificar si está activo
	if (!especialista.flg_activo) {
		return {
			success: false,
			error: 'Cuenta desactivada. Contacte al administrador'
		};
	}

	// Verificar si está bloqueado
	if (estaBloqueo(especialista.bloqueado_hasta)) {
		return {
			success: false,
			error: 'Cuenta bloqueada temporalmente. Intente en 15 minutos'
		};
	}

	// Verificar contraseña
	const passwordValida = await bcrypt.compare(password, especialista.password_hash);

	if (!passwordValida) {
		// Incrementar intentos fallidos
		const intentos = await incrementarIntentosFallidos(usuario);
		const intentosRestantes = 5 - intentos;

		if (intentosRestantes <= 0) {
			return {
				success: false,
				error: 'Cuenta bloqueada por 15 minutos debido a múltiples intentos fallidos'
			};
		}

		return {
			success: false,
			error: `Usuario o contraseña incorrectos. Intentos restantes: ${intentosRestantes}`
		};
	}

	// Login exitoso: resetear intentos y actualizar último acceso
	await resetearIntentosFallidos(usuario);

	// Verificar si es primer login (password_cambiado_en es NULL)
	const esPrimerLogin = especialista.password_cambiado_en === null;

	// Retornar datos del usuario (sin password_hash)
	return {
		success: true,
		requiere_cambio_password: esPrimerLogin,
		user: {
			id_especialista: especialista.id_especialista,
			dni: especialista.dni,
			nombres: especialista.nombres,
			apellidos: especialista.apellidos,
			correo: especialista.correo,
			rol: especialista.rol,
			usuario: especialista.usuario
		}
	};
}

/**
 * Obtener usuario por ID para verificar sesión
 */
export async function getEspecialistaByIdForAuth(id) {
	const [especialista] = await sql`
		SELECT
			id_especialista,
			dni,
			nombres,
			apellidos,
			correo,
			rol,
			usuario,
			flg_activo
		FROM especialista
		WHERE id_especialista = ${id}
	`;

	if (!especialista || !especialista.flg_activo) {
		return null;
	}

	return especialista;
}

/**
 * Cambiar contraseña
 */
export async function cambiarPassword(id_especialista, passwordActual, passwordNueva) {
	// Obtener usuario con password_hash
	const [especialista] = await sql`
		SELECT password_hash FROM especialista
		WHERE id_especialista = ${id_especialista}
	`;

	if (!especialista) {
		return {
			success: false,
			error: 'Usuario no encontrado'
		};
	}

	// Verificar contraseña actual
	const passwordValida = await bcrypt.compare(passwordActual, especialista.password_hash);

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
		UPDATE especialista
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NOW()
		WHERE id_especialista = ${id_especialista}
	`;

	return {
		success: true,
		message: 'Contraseña actualizada correctamente'
	};
}

/**
 * Recuperar contraseña: resetear al DNI del especialista si el correo coincide
 */
export async function recuperarPasswordEspecialista(correo) {
	// Buscar especialista por correo
	const [especialista] = await sql`
		SELECT id_especialista, correo, dni, flg_activo FROM especialista
		WHERE correo = ${correo}
	`;

	if (!especialista) {
		return {
			success: false,
			error: 'No existe una cuenta registrada con ese correo electrónico'
		};
	}

	if (!especialista.flg_activo) {
		return {
			success: false,
			error: 'Cuenta desactivada. Contacte al administrador'
		};
	}

	// Hashear el DNI como nueva contraseña por defecto
	const saltRounds = 10;
	const nuevoHash = await bcrypt.hash(especialista.dni, saltRounds);

	// Actualizar contraseña y marcar como no cambiada (forzar cambio en siguiente login)
	await sql`
		UPDATE especialista
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NULL,
		    intentos_fallidos = 0,
		    bloqueado_hasta = NULL
		WHERE id_especialista = ${especialista.id_especialista}
	`;

	return {
		success: true,
		message: 'Contraseña restablecida correctamente. Su nueva contraseña es su número de DNI.'
	};
}

/**
 * Cambiar contraseña en primer login (sin validar contraseña actual)
 */
export async function cambiarPasswordPrimerLogin(id_especialista, passwordNueva) {
	// Verificar que el usuario realmente esté en primer login
	const [especialista] = await sql`
		SELECT password_cambiado_en FROM especialista
		WHERE id_especialista = ${id_especialista}
	`;

	if (!especialista) {
		return {
			success: false,
			error: 'Usuario no encontrado'
		};
	}

	// Solo permitir si password_cambiado_en es NULL (primer login)
	if (especialista.password_cambiado_en !== null) {
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
		UPDATE especialista
		SET password_hash = ${nuevoHash},
		    password_cambiado_en = NOW()
		WHERE id_especialista = ${id_especialista}
	`;

	return {
		success: true,
		message: 'Contraseña actualizada correctamente'
	};
}
