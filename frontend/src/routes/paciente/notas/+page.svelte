<script>
	let { data } = $props();

	let formData = $state({
		question1: '',
		question2: '',
		question3: '',
		question4: ''
	});

	let isSaving = $state(false);
	let message = $state({ type: '', text: '' });

	// Función para contar palabras
	function contarPalabras(texto) {
		return texto.trim().split(/\s+/).filter(palabra => palabra.length > 0).length;
	}

	// Obtener contador de palabras reactivo
	function getWordCount(key) {
		return contarPalabras(formData[key]);
	}

	async function handleSubmit(e) {
		e.preventDefault();
		isSaving = true;
		message = { type: '', text: '' };

		try {
			const response = await fetch('/api/pacientes/respuestas', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ respuestas: formData })
			});

			const result = await response.json();

			if (result.success) {
				message = { type: 'success', text: result.message || 'Tus respuestas han sido guardadas correctamente' };
				// Limpiar formulario
				formData = {
					question1: '',
					question2: '',
					question3: '',
					question4: ''
				};
			} else {
				message = { type: 'error', text: result.error || 'Error al guardar las respuestas' };
			}
		} catch (error) {
			console.error('Error:', error);
			message = { type: 'error', text: 'Error de conexión. Por favor, intente nuevamente.' };
		} finally {
			isSaving = false;
		}
	}

	function handleClear() {
		formData = {
			question1: '',
			question2: '',
			question3: '',
			question4: ''
		};
		message = { type: '', text: '' };
	}
</script>

<svelte:head>
	<title>Notas Diarias - Portal de Pacientes</title>
</svelte:head>

<div class="p-8">
	<div class="max-w-5xl mx-auto">
		<!-- Header -->
		<div class="mb-8 flex justify-between items-center">
			<div>
				<h1 class="text-3xl font-bold text-white mb-2">Notas Diarias</h1>
				<p class="text-white/80">Comparte tus pensamientos y emociones del día</p>
			</div>
			{#if data.tieneHistoriaClinica}
				<button
					onclick={() => window.location.href = '/paciente/notas/historial'}
					class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					Ver Historial
				</button>
			{/if}
		</div>

		{#if !data.tieneHistoriaClinica}
			<!-- Mensaje cuando no tiene historia clínica -->
			<div class="bg-white rounded-2xl shadow-2xl overflow-hidden p-12 text-center">
				<div class="max-w-2xl mx-auto">
					<svg class="w-24 h-24 mx-auto mb-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
					<h2 class="text-2xl font-bold text-gray-800 mb-4">Historia Clínica No Disponible</h2>
					<p class="text-gray-600 mb-6 text-lg leading-relaxed">
						Para poder utilizar el cuestionario de notas diarias, primero necesitas contar con una historia clínica activa en nuestro sistema.
					</p>
					<div class="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6 text-left">
						<h3 class="text-blue-800 font-semibold mb-2 flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
							</svg>
							¿Qué hacer a continuación?
						</h3>
						<ul class="text-blue-700 space-y-2 ml-7">
							<li>• Comunícate con nuestro equipo de atención al paciente</li>
							<li>• Un especialista debe crear tu historia clínica</li>
							<li>• Una vez creada, podrás acceder a todas las funcionalidades</li>
						</ul>
					</div>
					<div class="flex flex-col sm:flex-row gap-4 justify-center">
						<a
							href="/paciente/inicio"
							class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors inline-flex items-center justify-center gap-2"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
							</svg>
							Volver al Inicio
						</a>
						<button
							onclick={() => window.location.href = 'tel:+51999999999'}
							class="px-6 py-3 bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50 rounded-lg font-semibold transition-colors inline-flex items-center justify-center gap-2"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
							</svg>
							Contactar Atención
						</button>
					</div>
				</div>
			</div>
		{:else}
			<!-- Form Card -->
			<div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
			<div class="px-8 py-6 border-b border-gray-200" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);">
				<p class="text-gray-700">
					Tómate un momento para reflexionar sobre tu día. Responde las siguientes preguntas de manera honesta. Cada respuesta debe tener al menos 10 palabras.
				</p>
				<p class="text-gray-600 text-sm mt-2">
					📌 <strong>Importante:</strong> Puedes completar este cuestionario máximo 2 veces al día (hora de Perú GMT-5). Tus respuestas no se pueden editar una vez enviadas.
				</p>
			</div>

			<form onsubmit={handleSubmit} class="p-8">
				{#if message.text}
					<div class="mb-6 p-4 rounded-lg {message.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'}">
						<div class="flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								{#if message.type === 'success'}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								{:else}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								{/if}
							</svg>
							<span>{message.text}</span>
						</div>
					</div>
				{/if}

				<div class="space-y-8">
					<!-- Pregunta 1 -->
					<div>
						<label for="question1" class="block text-sm font-semibold text-gray-700 mb-3">
							1. ¿Cómo fue tu día hoy?
						</label>
						<textarea
							id="question1"
							bind:value={formData.question1}
							rows="4"
							placeholder="Cuéntame cómo fue tu día... ¿Qué cosas hiciste? ¿Cómo te sentiste?"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
						></textarea>
						<div class="mt-1 text-sm {getWordCount('question1') >= 10 ? 'text-green-600' : 'text-gray-500'}">
							{getWordCount('question1')} palabras {#if getWordCount('question1') < 10}(mínimo 10){/if}
						</div>
					</div>

					<!-- Pregunta 2 -->
					<div>
						<label for="question2" class="block text-sm font-semibold text-gray-700 mb-3">
							2. ¿Cómo te sientes en este momento?
						</label>
						<textarea
							id="question2"
							bind:value={formData.question2}
							rows="4"
							placeholder="Comparte cómo te sientes en este momento... ¿Hay algo que te preocupe o te haga feliz?"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
						></textarea>
						<div class="mt-1 text-sm {getWordCount('question2') >= 10 ? 'text-green-600' : 'text-gray-500'}">
							{getWordCount('question2')} palabras {#if getWordCount('question2') < 10}(mínimo 10){/if}
						</div>
					</div>

					<!-- Pregunta 3 -->
					<div>
						<label for="question3" class="block text-sm font-semibold text-gray-700 mb-3">
							3. ¿Cómo describirías tu estado de ánimo?
						</label>
						<textarea
							id="question3"
							bind:value={formData.question3}
							rows="4"
							placeholder="Cuéntame sobre tu estado de ánimo... ¿Has notado cambios en cómo te sientes últimamente?"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
						></textarea>
						<div class="mt-1 text-sm {getWordCount('question3') >= 10 ? 'text-green-600' : 'text-gray-500'}">
							{getWordCount('question3')} palabras {#if getWordCount('question3') < 10}(mínimo 10){/if}
						</div>
					</div>

					<!-- Pregunta 4 -->
					<div>
						<label for="question4" class="block text-sm font-semibold text-gray-700 mb-3">
							4. ¿Qué situaciones has experimentado hoy?
						</label>
						<textarea
							id="question4"
							bind:value={formData.question4}
							rows="4"
							placeholder="Dime qué cosas te han ayudado o dificultado hoy... ¿Hubo algo que te generó estrés o alegría?"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
						></textarea>
						<div class="mt-1 text-sm {getWordCount('question4') >= 10 ? 'text-green-600' : 'text-gray-500'}">
							{getWordCount('question4')} palabras {#if getWordCount('question4') < 10}(mínimo 10){/if}
						</div>
					</div>
				</div>

				<!-- Buttons -->
				<div class="mt-8 flex justify-end gap-4">
					<button
						type="button"
						onclick={handleClear}
						class="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
					>
						Limpiar
					</button>
					<button
						type="submit"
						disabled={isSaving}
						class="px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-xl"
						style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
					>
						{#if isSaving}
							<span class="flex items-center">
								<svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Guardando...
							</span>
						{:else}
							Guardar Notas
						{/if}
					</button>
				</div>
			</form>
		</div>
		{/if}
	</div>
</div>
