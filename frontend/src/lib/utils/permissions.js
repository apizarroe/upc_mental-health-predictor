/**
 * Sistema de permisos basado en roles
 * Define qué acciones puede realizar cada rol
 */

export const ROLES = {
	ADMIN: 'admin',
	ESPECIALISTA: 'especialista',
	PACIENTE: 'paciente'
};

export const PERMISSIONS = {
	// Permisos de Pacientes
	PACIENTES_READ: 'pacientes:read',
	PACIENTES_CREATE: 'pacientes:create',
	PACIENTES_UPDATE: 'pacientes:update',
	PACIENTES_DELETE: 'pacientes:delete',

	// Permisos de Especialistas
	ESPECIALISTAS_READ: 'especialistas:read',
	ESPECIALISTAS_CREATE: 'especialistas:create',
	ESPECIALISTAS_UPDATE: 'especialistas:update',
	ESPECIALISTAS_DELETE: 'especialistas:delete',

	// Permisos de Historias Clínicas
	HISTORIAS_READ: 'historias:read',
	HISTORIAS_CREATE: 'historias:create',
	HISTORIAS_UPDATE: 'historias:update',
	HISTORIAS_DELETE: 'historias:delete',

	// Permisos de Notas
	NOTAS_READ: 'notas:read',
	NOTAS_CREATE: 'notas:create',
	NOTAS_UPDATE: 'notas:update',
	NOTAS_DELETE: 'notas:delete'
};

// Mapeo de permisos por rol
const rolePermissions = {
	[ROLES.ADMIN]: [
		// Admin tiene acceso completo a todo
		PERMISSIONS.PACIENTES_READ,
		PERMISSIONS.PACIENTES_CREATE,
		PERMISSIONS.PACIENTES_UPDATE,
		PERMISSIONS.PACIENTES_DELETE,
		PERMISSIONS.ESPECIALISTAS_READ,
		PERMISSIONS.ESPECIALISTAS_CREATE,
		PERMISSIONS.ESPECIALISTAS_UPDATE,
		PERMISSIONS.ESPECIALISTAS_DELETE,
		PERMISSIONS.HISTORIAS_READ,
		PERMISSIONS.HISTORIAS_CREATE,
		PERMISSIONS.HISTORIAS_UPDATE,
		PERMISSIONS.HISTORIAS_DELETE,
		PERMISSIONS.NOTAS_READ
	],
	[ROLES.ESPECIALISTA]: [
		// Especialista solo puede ver pacientes
		PERMISSIONS.PACIENTES_READ,

		// Especialista NO tiene acceso a módulo de especialistas
		// (no incluimos ningún permiso de especialistas)

		// Especialista tiene acceso completo a historias clínicas
		PERMISSIONS.HISTORIAS_READ,
		PERMISSIONS.HISTORIAS_CREATE,
		PERMISSIONS.HISTORIAS_UPDATE,
		PERMISSIONS.HISTORIAS_DELETE,

		// Especialista puede leer notas de pacientes
		PERMISSIONS.NOTAS_READ
	],
	[ROLES.PACIENTE]: [
		// Pacientes pueden crear y leer sus propias notas
		PERMISSIONS.NOTAS_CREATE,
		PERMISSIONS.NOTAS_READ
	]
};

/**
 * Verifica si un usuario tiene un permiso específico
 * @param {string} userRole - Rol del usuario (admin | especialista)
 * @param {string} permission - Permiso a verificar
 * @returns {boolean}
 */
export function hasPermission(userRole, permission) {
	if (!userRole || !permission) return false;
	const permissions = rolePermissions[userRole] || [];
	return permissions.includes(permission);
}

/**
 * Verifica si un usuario puede acceder al módulo de pacientes
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canAccessPacientes(userRole) {
	return hasPermission(userRole, PERMISSIONS.PACIENTES_READ);
}

/**
 * Verifica si un usuario puede crear pacientes
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canCreatePacientes(userRole) {
	return hasPermission(userRole, PERMISSIONS.PACIENTES_CREATE);
}

/**
 * Verifica si un usuario puede editar pacientes
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canUpdatePacientes(userRole) {
	return hasPermission(userRole, PERMISSIONS.PACIENTES_UPDATE);
}

/**
 * Verifica si un usuario puede eliminar pacientes
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canDeletePacientes(userRole) {
	return hasPermission(userRole, PERMISSIONS.PACIENTES_DELETE);
}

/**
 * Verifica si un usuario puede acceder al módulo de especialistas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canAccessEspecialistas(userRole) {
	return hasPermission(userRole, PERMISSIONS.ESPECIALISTAS_READ);
}

/**
 * Verifica si un usuario puede crear especialistas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canCreateEspecialistas(userRole) {
	return hasPermission(userRole, PERMISSIONS.ESPECIALISTAS_CREATE);
}

/**
 * Verifica si un usuario puede editar especialistas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canUpdateEspecialistas(userRole) {
	return hasPermission(userRole, PERMISSIONS.ESPECIALISTAS_UPDATE);
}

/**
 * Verifica si un usuario puede eliminar especialistas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canDeleteEspecialistas(userRole) {
	return hasPermission(userRole, PERMISSIONS.ESPECIALISTAS_DELETE);
}

/**
 * Verifica si un usuario puede acceder al módulo de historias clínicas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canAccessHistorias(userRole) {
	return hasPermission(userRole, PERMISSIONS.HISTORIAS_READ);
}

/**
 * Verifica si un usuario puede crear historias clínicas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canCreateHistorias(userRole) {
	return hasPermission(userRole, PERMISSIONS.HISTORIAS_CREATE);
}

/**
 * Verifica si un usuario puede editar historias clínicas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canUpdateHistorias(userRole) {
	return hasPermission(userRole, PERMISSIONS.HISTORIAS_UPDATE);
}

/**
 * Verifica si un usuario puede eliminar historias clínicas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canDeleteHistorias(userRole) {
	return hasPermission(userRole, PERMISSIONS.HISTORIAS_DELETE);
}

/**
 * Verifica si un usuario es paciente
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function isPaciente(userRole) {
	return userRole === ROLES.PACIENTE;
}

/**
 * Verifica si un usuario es especialista (admin o especialista)
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function isEspecialista(userRole) {
	return (
		userRole === ROLES.ADMIN ||
		userRole === ROLES.ESPECIALISTA
	);
}

/**
 * Verifica si un usuario puede leer notas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canReadNotas(userRole) {
	return hasPermission(userRole, PERMISSIONS.NOTAS_READ);
}

/**
 * Verifica si un usuario puede crear notas
 * @param {string} userRole - Rol del usuario
 * @returns {boolean}
 */
export function canCreateNotas(userRole) {
	return hasPermission(userRole, PERMISSIONS.NOTAS_CREATE);
}

/**
 * Verifica si un usuario puede acceder a datos específicos
 * Los pacientes solo pueden acceder a sus propios datos
 * Los especialistas pueden acceder a cualquier dato
 * @param {object} user - Usuario actual con { user_id, user_type, rol }
 * @param {number} resourceOwnerId - ID del propietario del recurso
 * @returns {boolean}
 */
export function canAccessOwnData(user, resourceOwnerId) {
	if (!user) return false;

	// Especialistas pueden acceder a cualquier dato
	if (isEspecialista(user.rol)) {
		return true;
	}

	// Pacientes solo pueden acceder a sus propios datos
	if (isPaciente(user.rol)) {
		return +user.user_id === resourceOwnerId;
	}

	return false;
}
