<script>
	let { questionId, onTranscriptionComplete } = $props();

	let isRecording = $state(false);
	let isProcessing = $state(false);
	let recordingTime = $state(0);
	let transcribedText = $state('');
	let errorMessage = $state('');

	let mediaRecorder = null;
	let audioChunks = [];
	let timerInterval = null;

	async function startRecording() {
		try {
			errorMessage = '';
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

			mediaRecorder = new MediaRecorder(stream);
			audioChunks = [];

			mediaRecorder.ondataavailable = (event) => {
				if (event.data.size > 0) {
					audioChunks.push(event.data);
				}
			};

			mediaRecorder.onstop = async () => {
				const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
				await processAudio(audioBlob);

				// Detener todas las pistas de audio
				stream.getTracks().forEach(track => track.stop());
			};

			mediaRecorder.start();
			isRecording = true;
			recordingTime = 0;

			// Iniciar temporizador
			timerInterval = setInterval(() => {
				recordingTime++;
			}, 1000);

		} catch (error) {
			console.error('Error al acceder al micrófono:', error);
			errorMessage = 'No se pudo acceder al micrófono. Por favor, verifica los permisos.';
		}
	}

	function stopRecording() {
		if (mediaRecorder && isRecording) {
			mediaRecorder.stop();
			isRecording = false;

			if (timerInterval) {
				clearInterval(timerInterval);
				timerInterval = null;
			}
		}
	}

	async function processAudio(audioBlob) {
		isProcessing = true;
		errorMessage = '';

		try {
			// Crear FormData para enviar el audio
			const formData = new FormData();
			formData.append('audio', audioBlob, 'recording.webm');
			formData.append('questionId', questionId);

			// Enviar al endpoint de SvelteKit
			const response = await fetch('/api/pacientes/transcribir', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (result.success) {
				transcribedText = result.transcription;
				// Llamar callback con la transcripción
				if (onTranscriptionComplete) {
					onTranscriptionComplete(result.transcription);
				}
			} else {
				errorMessage = result.error || 'Error al procesar el audio';
			}
		} catch (error) {
			console.error('Error al procesar audio:', error);
			errorMessage = 'Error de conexión al procesar el audio';
		} finally {
			isProcessing = false;
		}
	}

	function formatTime(seconds) {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function clearTranscription() {
		transcribedText = '';
		recordingTime = 0;
		if (onTranscriptionComplete) {
			onTranscriptionComplete('');
		}
	}
</script>

<div class="audio-recorder-container">
	{#if transcribedText}
		<!-- Mostrar transcripción -->
		<div class="transcription-result">
			<div class="flex justify-between items-start mb-2">
				<span class="text-sm font-medium text-green-700">Transcripción:</span>
				<button
					type="button"
					onclick={clearTranscription}
					class="text-sm text-red-600 hover:text-red-800 underline"
				>
					Borrar y grabar de nuevo
				</button>
			</div>
			<p class="text-gray-800 bg-green-50 p-3 rounded-lg border border-green-200">
				{transcribedText}
			</p>
		</div>
	{:else}
		<!-- Controles de grabación -->
		<div class="recording-controls">
			{#if isRecording}
				<div class="recording-active">
					<div class="flex items-center gap-3 mb-3">
						<div class="recording-indicator">
							<span class="recording-dot"></span>
						</div>
						<span class="text-red-600 font-semibold">Grabando...</span>
						<span class="text-gray-600 font-mono">{formatTime(recordingTime)}</span>
					</div>
					<button
						type="button"
						onclick={stopRecording}
						class="w-full px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
					>
						<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
						</svg>
						Detener Grabación
					</button>
				</div>
			{:else if isProcessing}
				<div class="processing-state">
					<div class="flex items-center justify-center gap-3">
						<svg class="animate-spin h-6 w-6 text-purple-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						<span class="text-purple-600 font-semibold">Procesando audio...</span>
					</div>
				</div>
			{:else}
				<button
					type="button"
					onclick={startRecording}
					class="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
				>
					<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
					</svg>
					Iniciar Grabación
				</button>
			{/if}
		</div>
	{/if}

	{#if errorMessage}
		<div class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
			<p class="text-sm text-red-800">{errorMessage}</p>
		</div>
	{/if}
</div>

<style>
	.audio-recorder-container {
		width: 100%;
	}

	.recording-indicator {
		display: flex;
		align-items: center;
	}

	.recording-dot {
		display: inline-block;
		width: 12px;
		height: 12px;
		background-color: #dc2626;
		border-radius: 50%;
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.5;
			transform: scale(1.1);
		}
	}

	.processing-state {
		padding: 1rem;
		background-color: rgba(147, 51, 234, 0.05);
		border-radius: 0.5rem;
	}
</style>
