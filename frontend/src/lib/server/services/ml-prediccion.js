import sql from '../db/client.js';

// URL del API de ML (configurable)
const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

/**
 * Envía las respuestas del paciente al API de ML para predicción
 * @param {number} idRespuesta - ID de la respuesta guardada
 * @param {Object} respuestas - Objeto con las 4 respuestas
 * @returns {Promise<Object>} - Resultado de la predicción
 */
export async function enviarPrediccion(idRespuesta, respuestas) {
	console.log('🤖 Enviando respuesta al API de ML...');
	console.log('📝 ID Respuesta:', idRespuesta);

	try {
		const payload = {
			patient_id: `RESP-${idRespuesta}`,
			answers: {
				question1: respuestas.question1,
				question2: respuestas.question2,
				question3: respuestas.question3,
				question4: respuestas.question4
			}
		};

		console.log('📤 Payload:', JSON.stringify(payload, null, 2));

		const response = await fetch(`${ML_API_URL}/api/v1/predict/mental-health`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(payload),
			signal: AbortSignal.timeout(30000) // 30 segundos timeout
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(`ML API Error: ${errorData.detail || response.statusText}`);
		}

		const result = await response.json();

		console.log('✅ ML procesado exitosamente');
		console.log('📊 Predicciones completas:', JSON.stringify(result, null, 2));

		return result;
	} catch (error) {
		console.error('❌ Error en ML:', error.message);
		throw error;
	}
}

/**
 * Resuelve el nivel de riesgo global priorizando el detector de crisis
 * sobre el cálculo basado en probabilidades.
 * @param {Object} predictions
 * @param {Object|null} riskAssessment - Resultado de risk_detector del backend
 * @returns {string} - 'bajo', 'moderado', 'alto'
 */
function calcularNivelRiesgo(predictions, riskAssessment = null) {
	// El detector de crisis tiene prioridad absoluta
	if (riskAssessment?.nivel_riesgo === 'alto') return 'alto';
	if (riskAssessment?.nivel_riesgo === 'medio') return 'moderado';

	// Fallback: cálculo basado en probabilidades del clasificador
	const depProb = predictions.depression?.probability || 0;
	const anxProb = predictions.anxiety?.probability || 0;
	const maxProb = Math.max(depProb, anxProb);

	if (maxProb >= 0.7) return 'alto';
	if (maxProb >= 0.5) return 'moderado';
	return 'bajo';
}

/**
 * Determina si requiere atención priorizando el detector de crisis.
 * @param {Object} predictions
 * @param {Object|null} riskAssessment
 * @returns {boolean}
 */
function requiereAtencion(predictions, riskAssessment = null) {
	if (riskAssessment?.requiere_atencion === true) return true;
	return calcularNivelRiesgo(predictions) === 'alto';
}

/**
 * Crea un registro de evaluación ML en la base de datos
 * @param {number} idRespuesta - ID de la respuesta
 * @param {Object} mlResult - Resultado completo del ML
 * @returns {Promise<Object>} - Evaluación creada
 */
export async function crearEvaluacionML(idRespuesta, mlResult) {
	console.log('💾 Guardando evaluación ML en base de datos...');

	const { predictions, summary, analysis, model_info, risk_assessment } = mlResult;

	// Preparar datos para JSONB
	const trastornosDetectados = {
		depression: {
			has_condition: predictions.depression.has_condition,
			probability: predictions.depression.probability,
			confidence: predictions.depression.confidence,
			label: predictions.depression.label
		},
		anxiety: {
			has_condition: predictions.anxiety.has_condition,
			probability: predictions.anxiety.probability,
			confidence: predictions.anxiety.confidence,
			label: predictions.anxiety.label
		},
		risk_assessment: risk_assessment ?? null
	};

	const palabrasClave = {
		depression: analysis.depression_keywords || [],
		anxiety: analysis.anxiety_keywords || []
	};

	const metricasModelo = {
		depression: model_info.metrics?.depression || {},
		anxiety: model_info.metrics?.anxiety || {},
		overall: model_info.metrics?.overall || {}
	};

	const [evaluacion] = await sql`
		INSERT INTO evaluacion_ml (
			id_respuesta,
			fecha_evaluacion,
			modelo_nombre,
			modelo_tipo,
			modelo_version,
			trastornos_detectados,
			condiciones_detectadas,
			nivel_riesgo_global,
			interpretacion,
			requiere_atencion,
			palabras_clave,
			metricas_modelo
		) VALUES (
			${idRespuesta},
			NOW() AT TIME ZONE 'America/Lima',
			${model_info.model_name},
			${model_info.model_type},
			${model_info.bert_model},
			${sql.json(trastornosDetectados)},
			${summary.conditions_detected},
			${calcularNivelRiesgo(predictions, risk_assessment)},
			${summary.interpretation},
			${requiereAtencion(predictions, risk_assessment)},
			${sql.json(palabrasClave)},
			${sql.json(metricasModelo)}
		)
		RETURNING *
	`;

	console.log('✅ Evaluación ML guardada con ID:', evaluacion.id_evaluacion);
	return evaluacion;
}

/**
 * Actualiza el estado de procesamiento de una respuesta
 * @param {number} idRespuesta - ID de la respuesta
 * @param {string} estado - 'procesado' o 'error'
 * @param {number|null} idEvaluacion - ID de la evaluación (si fue exitosa)
 * @param {string|null} errorMensaje - Mensaje de error (si falló)
 */
export async function actualizarEstadoRespuesta(idRespuesta, estado, idEvaluacion = null, errorMensaje = null) {
	await sql`
		UPDATE paciente_respuesta
		SET
			estado_procesamiento = ${estado},
			id_evaluacion = ${idEvaluacion},
			error_mensaje = ${errorMensaje}
		WHERE id_respuesta = ${idRespuesta}
	`;

	console.log(`🔄 Estado actualizado a: ${estado}`);
}

/**
 * Procesa una respuesta completa con el ML
 * Flujo: Enviar al ML → Guardar evaluación → Actualizar estado
 * @param {number} idRespuesta - ID de la respuesta guardada
 * @param {Object} respuestas - Las 4 respuestas del paciente
 */
export async function procesarRespuestaConML(idRespuesta, respuestas) {
	try {
		// 1. Enviar al ML
		const mlResult = await enviarPrediccion(idRespuesta, respuestas);

		// 2. Guardar evaluación en BD
		const evaluacion = await crearEvaluacionML(idRespuesta, mlResult);

		// 3. Actualizar estado de la respuesta
		await actualizarEstadoRespuesta(idRespuesta, 'procesado', evaluacion.id_evaluacion);

		console.log('🎉 Procesamiento ML completado exitosamente');
		return { success: true, evaluacion };

	} catch (error) {
		console.error('❌ Error en procesamiento ML:', error);

		// Actualizar estado a error
		await actualizarEstadoRespuesta(idRespuesta, 'error', null, error.message);

		return { success: false, error: error.message };
	}
}

/**
 * Reprocesa una respuesta existente con el ML
 * Elimina la evaluación anterior y crea una nueva
 * @param {number} idRespuesta - ID de la respuesta a reprocesar
 * @param {Object} respuestas - Las 4 respuestas del paciente
 * @param {Object} sessionData - Datos del especialista que solicita el reprocesamiento
 */
export async function reprocesarRespuestaConML(idRespuesta, respuestas, sessionData) {
	try {
		console.log('🔄 Iniciando reprocesamiento...');

		// 1. Actualizar estado a 'pendiente' mientras se reprocesa
		await actualizarEstadoRespuesta(idRespuesta, 'pendiente', null, null);

		// 2. Eliminar evaluación anterior si existe
		await sql`
			DELETE FROM evaluacion_ml
			WHERE id_respuesta = ${idRespuesta}
		`;
		console.log('🗑️  Evaluación anterior eliminada');

		// 3. Enviar al ML
		const mlResult = await enviarPrediccion(idRespuesta, respuestas);

		// 4. Guardar nueva evaluación en BD
		const evaluacion = await crearEvaluacionML(idRespuesta, mlResult);

		// 5. Agregar nota de auditoría en la evaluación
		const usuario = sessionData.usuario || sessionData.nombres || 'Especialista';
		const rol = sessionData.rol || 'especialista';
		const timestamp = new Date().toLocaleString('es-PE', {
			timeZone: 'America/Lima',
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});

		await sql`
			UPDATE evaluacion_ml
			SET notas_sistema = ${`Reprocesado por ${usuario} (${rol}) el ${timestamp}`}
			WHERE id_evaluacion = ${evaluacion.id_evaluacion}
		`;

		// 6. Actualizar estado de la respuesta
		await actualizarEstadoRespuesta(idRespuesta, 'procesado', evaluacion.id_evaluacion);

		console.log('🎉 Reprocesamiento completado exitosamente');
		return { success: true, evaluacion };

	} catch (error) {
		console.error('❌ Error en reprocesamiento ML:', error);

		// Actualizar estado a error
		await actualizarEstadoRespuesta(idRespuesta, 'error', null, `Error al reprocesar: ${error.message}`);

		return { success: false, error: error.message };
	}
}
