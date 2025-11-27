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
 * Calcula el nivel de riesgo global basado en las probabilidades
 * @param {Object} predictions - Predicciones del ML
 * @returns {string} - 'bajo', 'moderado', 'alto'
 */
function calcularNivelRiesgo(predictions) {
	const depProb = predictions.depression?.probability || 0;
	const anxProb = predictions.anxiety?.probability || 0;
	const maxProb = Math.max(depProb, anxProb);

	if (maxProb >= 0.7) return 'alto';
	if (maxProb >= 0.5) return 'moderado';
	return 'bajo';
}

/**
 * Determina si requiere atención basado en las predicciones
 * @param {Object} predictions - Predicciones del ML
 * @returns {boolean}
 */
function requiereAtencion(predictions) {
	return predictions.depression?.has_condition || predictions.anxiety?.has_condition;
}

/**
 * Crea un registro de evaluación ML en la base de datos
 * @param {number} idRespuesta - ID de la respuesta
 * @param {Object} mlResult - Resultado completo del ML
 * @returns {Promise<Object>} - Evaluación creada
 */
export async function crearEvaluacionML(idRespuesta, mlResult) {
	console.log('💾 Guardando evaluación ML en base de datos...');

	const { predictions, summary, analysis, model_info } = mlResult;

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
		}
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
			${model_info.model_name},
			${model_info.model_type},
			${model_info.bert_model},
			${sql.json(trastornosDetectados)},
			${summary.conditions_detected},
			${calcularNivelRiesgo(predictions)},
			${summary.interpretation},
			${requiereAtencion(predictions)},
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
