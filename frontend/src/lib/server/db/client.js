import postgres from 'postgres';
import { DATABASE_URL } from '$env/static/private';

/**
 * Cliente de PostgreSQL usando postgres.js
 * Configurado para el pool de conexiones
 */
const sql = postgres(DATABASE_URL, {
	max: 10, // Máximo de conexiones en el pool
	idle_timeout: 20, // Timeout en segundos
	connect_timeout: 10
});

export default sql;
