/**
 * Fixtures para testing de Especialistas
 * Datos de prueba reutilizables para tests
 */

export const especialistaValido = {
	dni: '87654321',
	nombres: 'María Elena',
	apellidos: 'López Ramírez',
	especialidad: 'Psicología Clínica',
	colegiatura: 'CPsP12345',
	correo: 'maria.lopez@clinica.com',
	telefono: '987654321',
	cargo: 'Psicóloga Senior'
};

export const especialistaCompleto = {
	id_especialista: 1,
	dni: '87654321',
	nombres: 'María Elena',
	apellidos: 'López Ramírez',
	especialidad: 'Psicología Clínica',
	colegiatura: 'CPsP12345',
	correo: 'maria.lopez@clinica.com',
	telefono: '987654321',
	cargo: 'Psicóloga Senior',
	flg_activo: true
};

export const especialistaInactivo = {
	id_especialista: 2,
	dni: '11223344',
	nombres: 'Carlos Alberto',
	apellidos: 'Fernández Torres',
	especialidad: 'Psiquiatría',
	colegiatura: 'CMP67890',
	correo: 'carlos.fernandez@clinica.com',
	telefono: '976543210',
	cargo: 'Psiquiatra',
	flg_activo: false
};

export const especialistaPsicologo = {
	id_especialista: 3,
	dni: '22334455',
	nombres: 'Laura Patricia',
	apellidos: 'Gómez Silva',
	especialidad: 'Psicología Infantil',
	colegiatura: 'CPsP23456',
	correo: 'laura.gomez@clinica.com',
	telefono: '965432109',
	cargo: 'Psicóloga Infantil',
	flg_activo: true
};

export const especialistaPsiquiatra = {
	id_especialista: 4,
	dni: '33445566',
	nombres: 'Roberto Miguel',
	apellidos: 'Vargas Mendoza',
	especialidad: 'Psiquiatría General',
	colegiatura: 'CMP78901',
	correo: 'roberto.vargas@clinica.com',
	telefono: '954321098',
	cargo: 'Director Médico',
	flg_activo: true
};

export const listaEspecialistas = [
	especialistaCompleto,
	especialistaInactivo,
	especialistaPsicologo,
	especialistaPsiquiatra,
	{
		id_especialista: 5,
		dni: '44556677',
		nombres: 'Ana Sofía',
		apellidos: 'Rojas Castro',
		especialidad: 'Psicología Familiar',
		colegiatura: 'CPsP34567',
		correo: 'ana.rojas@clinica.com',
		telefono: '943210987',
		cargo: 'Coordinadora de Terapias',
		flg_activo: true
	}
];

export const especialistaInvalido = {
	dni: '123', // DNI inválido (menos de 8 dígitos)
	nombres: 'María123', // Contiene números
	apellidos: 'López@', // Contiene caracteres especiales
	especialidad: '',
	colegiatura: '',
	correo: 'email-invalido',
	telefono: '',
	cargo: ''
};
