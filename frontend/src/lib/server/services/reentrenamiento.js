import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { getValidacionesPendientesReentrenamiento } from './validaciones.js';

const currentFile = fileURLToPath(import.meta.url);
const servicesDir = path.dirname(currentFile);
const frontendDir = path.resolve(servicesDir, '../../../..');
const projectRoot = path.resolve(frontendDir, '..');
const backendDir = path.join(projectRoot, 'backend');
const datasetsDir = path.join(backendDir, 'data', 'datasets');

const metadataPath = path.join(datasetsDir, 'specialist_validated_dataset_metadata.json');
const validatedDatasetPath = path.join(datasetsDir, 'specialist_validated_dataset.csv');
const mergedTrainingDatasetPath = path.join(datasetsDir, 'labeled_dataset_with_feedback.csv');
const baseTrainingDatasetPath = path.join(datasetsDir, 'labeled_dataset.csv');
const FEEDBACK_OVERSAMPLING_FACTOR = 20;

const LEGACY_SYSTEM_PROMPT =
	'actúa como un psicólogo especializado en consejos breves y prácticos para manejar desafíos emocionales y psicológicos.ofrece orientación concisa que sea comprensible y aplicable inmediatamente. enfócate en estrategias efectivas y técnicas de afrontamiento para promover el bienestar. tus respuestas deben ser directas, limitándose a unas pocas oraciones, y centrarse en soluciones prácticas y consejos accionables. comunica de forma clara y empática, con recomendaciones relevantes para las preocupaciones planteadas, manteniendo un tono amigable y profesional.';

const QUESTION_ASSISTANT_PROMPTS = [
	'¿cómo fue tu día hoy?',
	'¿cómo te sientes en este momento?',
	'¿cómo describirías tu estado de ánimo?',
	'¿qué situaciones te han afectado hoy?'
];

const DEFAULT_METADATA = {
	feedback_snapshot_timestamp: null,
	included_validation_ids: [],
	excluded_validation_ids: [],
	label_sources_summary: {}
};

const trainingState = {
	isRunning: false,
	lastStartedAt: null,
	lastFinishedAt: null,
	lastStartedBy: null,
	lastExitCode: null,
	lastError: null,
	logTail: '',
	activeValidationIds: []
};

function csvEscape(value) {
	const text = String(value ?? '');
	return `"${text.replaceAll('"', '""')}"`;
}

function appendLog(chunk) {
	trainingState.logTail = `${trainingState.logTail}${chunk}`.slice(-16000);
}

function escapePythonLikeString(value) {
	return String(value ?? '')
		.replaceAll('\\', '\\\\')
		.replaceAll("'", "\\'");
}

function buildLegacyConversationText(respuestas = {}) {
	const orderedAnswers = [
		respuestas.question1,
		respuestas.question2,
		respuestas.question3,
		respuestas.question4
	].map((answer) => String(answer ?? '').trim());

	const conversation = [{ content: LEGACY_SYSTEM_PROMPT, role: 'system' }];

	orderedAnswers.forEach((answer, index) => {
		if (!answer) return;

		conversation.push({
			content: answer,
			role: 'user'
		});

		if (QUESTION_ASSISTANT_PROMPTS[index]) {
			conversation.push({
				content: QUESTION_ASSISTANT_PROMPTS[index],
				role: 'assistant'
			});
		}
	});

	return `[${conversation
		.map(
			(message) =>
				`{'content': '${escapePythonLikeString(message.content)}', 'role': '${message.role}'}`
		)
		.join(' ')}]`;
}

function buildCombinedText(respuestas = {}) {
	return [respuestas.question1, respuestas.question2, respuestas.question3, respuestas.question4]
		.filter(Boolean)
		.join(' ')
		.replace(/\s+/g, ' ')
		.trim();
}

function mapTargetsToTrainingRow(validacion) {
	const diagnostico = validacion.diagnostico_especialista ?? {};
	const targetDepression = diagnostico.depression ? 1 : 0;
	const targetAnxiety = diagnostico.anxiety ? 1 : 0;
	const text = buildLegacyConversationText(validacion.respuestas);

	let label = 'neutral';
	if (targetDepression && targetAnxiety) label = 'depression';
	else if (targetDepression) label = 'depression';
	else if (targetAnxiety) label = 'anxiety';

	const labelId = label === 'depression' ? 0 : label === 'anxiety' ? 1 : 2;

	return {
		id_validacion: validacion.id_validacion,
		id_respuesta: validacion.id_respuesta,
		id_evaluacion: validacion.id_evaluacion,
		text,
		target_depression: targetDepression,
		target_anxiety: targetAnxiety,
		validation_confidence: validacion.nivel_confianza ?? '',
		label_source: 'specialist',
		util_para_entrenamiento: true,
		label,
		label_id: labelId,
		score_depression: targetDepression ? 2 : 0,
		score_anxiety: targetAnxiety ? 2 : 0,
		raw_text_preview: buildCombinedText(validacion.respuestas)
	};
}

async function readMetadata() {
	try {
		const raw = await fs.readFile(metadataPath, 'utf8');
		return { ...DEFAULT_METADATA, ...JSON.parse(raw) };
	} catch (error) {
		if (error.code === 'ENOENT') {
			return { ...DEFAULT_METADATA };
		}
		throw error;
	}
}

async function writeMetadata(metadata) {
	await fs.writeFile(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, 'utf8');
}

async function writeValidatedDatasets(rows) {
	const validatedHeader = [
		'id_validacion',
		'id_respuesta',
		'id_evaluacion',
		'text',
		'target_depression',
		'target_anxiety',
		'validation_confidence',
		'label_source',
		'util_para_entrenamiento'
	];
	const validatedLines = [
		validatedHeader.join(','),
		...rows.map((row) =>
			[
				row.id_validacion,
				row.id_respuesta,
				row.id_evaluacion,
				csvEscape(row.raw_text_preview),
				row.target_depression,
				row.target_anxiety,
				row.validation_confidence,
				row.label_source,
				row.util_para_entrenamiento
			].join(',')
		)
	];
	await fs.writeFile(validatedDatasetPath, `${validatedLines.join('\n')}\n`, 'utf8');

	const baseDataset = await fs.readFile(baseTrainingDatasetPath, 'utf8');
	const feedbackRows = rows.flatMap((row) => {
		const serializedRow = [
			csvEscape(row.text),
			row.label,
			row.label_id,
			row.score_depression,
			row.score_anxiety
		].join(',');

		return Array.from({ length: FEEDBACK_OVERSAMPLING_FACTOR }, () => serializedRow);
	});
	const baseNormalized = baseDataset.endsWith('\n') ? baseDataset : `${baseDataset}\n`;
	const mergedContent = `${baseNormalized}${feedbackRows.join('\n')}${feedbackRows.length ? '\n' : ''}`;

	await fs.writeFile(mergedTrainingDatasetPath, mergedContent, 'utf8');
}

async function finalizeTrainingSuccess(rows, metadata) {
	const includedIds = new Set((metadata.included_validation_ids ?? []).map((id) => String(id)));
	for (const row of rows) {
		includedIds.add(String(row.id_validacion));
	}

	await writeMetadata({
		feedback_snapshot_timestamp: new Date().toISOString(),
		included_validation_ids: [...includedIds],
		excluded_validation_ids: metadata.excluded_validation_ids ?? [],
		label_sources_summary: {
			specialist: rows.length
		}
	});
}

export async function getRetrainingStatus() {
	const metadata = await readMetadata();
	const pendientes = await getValidacionesPendientesReentrenamiento(metadata);

	return {
		...trainingState,
		pendingCount: pendientes.length,
		feedbackSnapshotTimestamp: metadata.feedback_snapshot_timestamp,
		includedValidationIds: metadata.included_validation_ids ?? []
	};
}

export async function startManualRetraining(sessionData) {
	if (trainingState.isRunning) {
		return {
			started: false,
			reason: 'running',
			status: await getRetrainingStatus()
		};
	}

	const metadata = await readMetadata();
	const pendientes = await getValidacionesPendientesReentrenamiento(metadata);

	if (pendientes.length === 0) {
		return {
			started: false,
			reason: 'no_pending',
			status: await getRetrainingStatus()
		};
	}

	const rows = pendientes.map(mapTargetsToTrainingRow).filter((row) => row.text);
	if (rows.length === 0) {
		return {
			started: false,
			reason: 'empty_rows',
			status: await getRetrainingStatus()
		};
	}

	await writeValidatedDatasets(rows);

	trainingState.isRunning = true;
	trainingState.lastStartedAt = new Date().toISOString();
	trainingState.lastFinishedAt = null;
	trainingState.lastStartedBy = sessionData.usuario || sessionData.nombres || 'admin';
	trainingState.lastExitCode = null;
	trainingState.lastError = null;
	trainingState.logTail = '';
	trainingState.activeValidationIds = rows.map((row) => row.id_validacion);

	const child = spawn(
		'bash',
		['./run_training.sh', '--data-path', 'data/datasets/labeled_dataset_with_feedback.csv'],
		{
			cwd: backendDir,
			env: {
				...process.env
			}
		}
	);

	child.stdout.on('data', (chunk) => appendLog(chunk.toString()));
	child.stderr.on('data', (chunk) => appendLog(chunk.toString()));

	child.on('error', (error) => {
		trainingState.isRunning = false;
		trainingState.lastFinishedAt = new Date().toISOString();
		trainingState.lastExitCode = -1;
		trainingState.lastError = error.message;
		appendLog(`\n[error] ${error.message}\n`);
	});

	child.on('close', async (code) => {
		trainingState.isRunning = false;
		trainingState.lastFinishedAt = new Date().toISOString();
		trainingState.lastExitCode = code;

		if (code === 0) {
			try {
				await finalizeTrainingSuccess(rows, metadata);
			} catch (error) {
				trainingState.lastError = `Modelo entrenado, pero no se pudo actualizar metadata: ${error.message}`;
				appendLog(`\n[metadata-error] ${error.message}\n`);
			}
			return;
		}

		trainingState.lastError = `El entrenamiento terminó con código ${code}`;
		appendLog(`\n[exit-code] ${code}\n`);
	});

	return {
		started: true,
		queuedValidations: rows.length,
		status: await getRetrainingStatus()
	};
}
