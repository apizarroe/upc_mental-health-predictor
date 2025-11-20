import sql from '../db/client.js';
import bcrypt from 'bcrypt';

/**
 * Servicio de autenticación unificado para Especialistas y Pacientes
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
async function bloquearUsuario(usuario, userType) {
	const bloqueadoHasta = new Date(Date.now() + 15 * 60 * 1000); // 15 minutos
	const tabla = userType === 'especialista' ? 'especialista' : 'paciente';

	await sql`
		UPDATE ${sql(tabla)}
		SET bloqueado_hasta = ${bloqueadoHasta}
		WHERE usuario = ${usuario}
	`;
}

/**
 * Incrementar contador de intentos fallidos
 */
async function incrementarIntentosFallidos(usuario, userType) {
	const tabla = userType === 'especialista' ? 'especialista' : 'paciente';
	const idField = userType === 'especialista' ? 'id_especialista' : 'id_paciente';

	const result = await sql`
		UPDATE ${sql(tabla)}
		SET intentos_fallidos = intentos_fallidos + 1
		WHERE usuario = ${usuario}
		RETURNING intentos_fallidos
	`;

	const user = result[0];

	// Si llega a 5 intentos, bloquear cuenta
	if (user && user.intentos_fallidos >= 5) {
		await bloquearUsuario(usuario, userType);
	}

	return user ? user.intentos_fallidos : 0;
}

/**
 * Resetear intentos fallidos y desbloquear
 */
async function resetearIntentosFallidos(usuario, userType) {
	const tabla = userType === 'especialista' ? 'especialista' : 'paciente';

	await sql`
		UPDATE ${sql(tabla)}
		SET intentos_fallidos = 0,
		    bloqueado_hasta = NULL,
		    ultimo_acceso = NOW()
		WHERE usuario = ${usuario}
	`;
}

/**
 * Login unificado: Busca en ambas tablas (especialista y paciente)
 * y retorna datos del usuario con user_type
 */
export async function login(usuario, password) {
	// Primero intentar buscar en tabla especialista
	const [especialista] = await sql`
		SELECT * FROM especialista
		WHERE usuario = ${usuario}
	`;

	// Si no se encuentra, buscar en tabla paciente
	const [paciente] = !especialista ? await sql`
		SELECT * FROM paciente
		WHERE usuario = ${usuario}
	` : [null];

	// Determinar cuál tabla tiene el usuario
	const user = especialista || paciente;
	const userType = especialista ? 'especialista' : (paciente ? 'paciente' : null);

	if (!user) {
		return {
			success: false,
			error: 'Usuario o contraseña incorrectos'
		};
	}

	// Verificar si está activo
	if (!user.flg_activo) {
		return {
			success: false,
			error: 'Cuenta desactivada. Contacte al administrador'
		};
	}

	// Verificar si está bloqueado
	if (estaBloqueo(user.bloqueado_hasta)) {
		return {
			success: false,
			error: 'Cuenta bloqueada temporalmente. Intente en 15 minutos'
		};
	}

	// Verificar contraseña
	const passwordValida = await bcrypt.compare(password, user.password_hash);

	if (!passwordValida) {
		// Incrementar intentos fallidos
		const intentos = await incrementarIntentosFallidos(usuario, userType);
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
	await resetearIntentosFallidos(usuario, userType);

	// Retornar datos del usuario según el tipo
	if (userType === 'especialista') {
		return {
			success: true,
			user: {
				user_id: user.id_especialista,
				user_type: 'especialista',
				dni: user.dni,
				nombres: user.nombres,
				apellidos: user.apellidos,
				correo: user.correo,
				rol: user.rol,
				usuario: user.usuario
			}
		};
	} else {
		// Paciente
		return {
			success: true,
			user: {
				user_id: user.id_paciente,
				user_type: 'paciente',
				dni: user.dni,
				nombres: user.nombres,
				apellidos: user.apellidos,
				correo: user.correo,
				rol: user.rol || 'paciente',
				usuario: user.usuario
			}
		};
	}
}

/**
 * Obtener especialista por ID para verificar sesión
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

	return {
		...especialista,
		user_id: especialista.id_especialista,
		user_type: 'especialista'
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
			rol,
			usuario,
			flg_activo
		FROM paciente
		WHERE id_paciente = ${id}
	`;

	if (!paciente || !paciente.flg_activo) {
		return null;
	}

	return {
		...paciente,
		user_id: paciente.id_paciente,
		user_type: 'paciente'
	};
}

/**
 * Obtener usuario por ID y tipo (unificado para session validation)
 */
export async function getUserByIdForAuth(userId, userType) {
	if (userType === 'especialista') {
		return await getEspecialistaByIdForAuth(userId);
	} else if (userType === 'paciente') {
		return await getPacienteByIdForAuth(userId);
	}
	return null;
}

/**
 * Cambiar contraseña (funciona para especialistas y pacientes)
 */
export async function cambiarPassword(userId, userType, passwordActual, passwordNueva) {
	const tabla = userType === 'especialista' ? 'especialista' : 'paciente';
	const idField = userType === 'especialista' ? 'id_especialista' : 'id_paciente';

	// Obtener usuario con password_hash
	const result = await sql`
		SELECT password_hash FROM ${sql(tabla)}
		WHERE ${sql(idField)} = ${userId}
	`;

	const user = result[0];

	if (!user) {
		return {
			success: false,
			error: 'Usuario no encontrado'
		};
	}

	// Verificar contraseña actual
	const passwordValida = await bcrypt.compare(passwordActual, user.password_hash);

	if (!passwordValida) {
		return {
			success: false,
			error: 'Contraseña actual incorrecta'
		};
	}

	// Hashear nueva contraseña
	const saltRounds = 10;
	const nuevoHash = await bcrypt.hash(passwordNueva, saltRounds);

	// Actualizar contraseña
	await sql`
		UPDATE ${sql(tabla)}
		SET password_hash = ${nuevoHash}
		WHERE ${sql(idField)} = ${userId}
	`;

	return {
		success: true,
		message: 'Contraseña actualizada correctamente'
	};
}
