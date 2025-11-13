/**
 * Fixtures para testing de Pacientes
 * Datos de prueba reutilizables para tests
 */

export const pacienteValido = {
	dni: '12345678',
	nombres: 'Juan Carlos',
	apellidos: 'Pérez García',
	fecha_nacimiento: '1990-01-15',
	sexo: 'M',
	direccion: 'Av. Principal 123, Lima',
	telefono: '987654321',
	correo: 'juan.perez@email.com',
	contacto_emergencia: 'María Pérez',
	telefono_emergencia: '912345678'
};

export const pacienteCompleto = {
	id_paciente: 1,
	dni: '12345678',
	nombres: 'Juan Carlos',
	apellidos: 'Pérez García',
	fecha_nacimiento: '1990-01-15',
	sexo: 'M',
	direccion: 'Av. Principal 123, Lima',
	telefono: '987654321',
	correo: 'juan.perez@email.com',
	contacto_emergencia: 'María Pérez',
	telefono_emergencia: '912345678',
	flg_activo: true
};

export const pacienteInactivo = {
	id_paciente: 2,
	dni: '87654321',
	nombres: 'Ana María',
	apellidos: 'López Rodríguez',
	fecha_nacimiento: '1985-05-20',
	sexo: 'F',
	direccion: 'Jr. Los Álamos 456, Lima',
	telefono: '976543210',
	correo: 'ana.lopez@email.com',
	contacto_emergencia: 'Carlos López',
	telefono_emergencia: '923456789',
	flg_activo: false
};

export const pacienteConNombreLargo = {
	id_paciente: 3,
	dni: '11223344',
	nombres: 'María Fernanda Gabriela Valentina',
	apellidos: 'Rodríguez Martínez González',
	fecha_nacimiento: '1995-03-10',
	sexo: 'F',
	direccion: 'Calle Las Flores 789, Lima',
	telefono: '965432109',
	correo: 'maria.rodriguez@email.com',
	contacto_emergencia: 'Pedro Rodríguez',
	telefono_emergencia: '934567890',
	flg_activo: true
};

export const listaPacientes = [
	pacienteCompleto,
	pacienteInactivo,
	pacienteConNombreLargo,
	{
		id_paciente: 4,
		dni: '55667788',
		nombres: 'Carlos Alberto',
		apellidos: 'Sánchez Torres',
		fecha_nacimiento: '1988-11-25',
		sexo: 'M',
		direccion: 'Av. Los Pinos 321, Lima',
		telefono: '954321098',
		correo: 'carlos.sanchez@email.com',
		contacto_emergencia: 'Laura Sánchez',
		telefono_emergencia: '945678901',
		flg_activo: true
	}
];

export const pacienteInvalido = {
	dni: '123', // DNI inválido (menos de 8 dígitos)
	nombres: 'Juan123', // Contiene números
	apellidos: 'Pérez@', // Contiene caracteres especiales
	fecha_nacimiento: '',
	sexo: 'M',
	direccion: '',
	telefono: '',
	correo: 'email-invalido',
	contacto_emergencia: '',
	telefono_emergencia: ''
};
