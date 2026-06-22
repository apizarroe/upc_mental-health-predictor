import postgres from 'postgres';
import { env } from '$env/dynamic/private';

const sql = postgres(env.DATABASE_URL, {
	max: 10,
	idle_timeout: 20,
	connect_timeout: 10,
	ssl: env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

export default sql;
