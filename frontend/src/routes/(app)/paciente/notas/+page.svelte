<script>
	import { goto } from '$app/navigation';

	let { data } = $props();

	const user = data.user;

	// Preguntas para el registro de notas
	const preguntas = [
		'¿Cómo fue tu día hoy?',
		'¿Qué actividades realizaste en tu rutina diaria?',
		'¿Cómo has estado gestionando tus emociones últimamente?',
		'¿Has tenido dificultades o situaciones que te hayan causado estrés recientemente?'
	];

	// Respuestas del paciente
	let respuestas = ['', '', '', ''];
	let error = '';
	let success = '';
	let loading = false;

	async function handleSubmit() {
		error = '';
		success = '';

		// Validar que al menos una respuesta tenga contenido
		const tieneRespuestas = respuestas.some(r => r.trim().length > 0);

		if (!tieneRespuestas) {
			error = 'Debes responder al menos una pregunta';
			return;
		}

		loading = true;

		try {
			// Crear array de notas solo con las respuestas que tengan contenido
			const notasParaGuardar = preguntas
				.map((pregunta, index) => ({
					pregunta,
					respuesta: respuestas[index]
				}))
				.filter(nota => nota.respuesta.trim().length > 0);

			const response = await fetch('/api/notas', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					id_paciente: user.user_id,
					notas: notasParaGuardar
				})
			});

			const result = await response.json();

			if (result.success) {
				success = `Notas guardadas exitosamente (${notasParaGuardar.length} nota(s))`;

				// Limpiar formulario
				respuestas = ['', '', '', ''];

				// Redirigir al historial después de 2 segundos
				setTimeout(() => {
					goto('/paciente/notas/historial');
				}, 2000);
			} else {
				error = result.error || 'Error al guardar notas';
			}
		} catch (err) {
			error = 'Error de conexión al servidor';
			console.error('Error:', err);
		} finally {
			loading = false;
		}
	}

	$inspect(respuestas)
</script>

<div class="max-w-4xl mx-auto p-6">
	<div class="flex justify-between items-center mb-6">
		<h1 class="text-white text-3xl font-bold">Notas Diarias</h1>
		<a
			href="/paciente/notas/historial"
			class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
		>
			<svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			</svg>
			Ver Historial
		</a>
	</div>

	<div class="bg-white shadow rounded-lg p-6">
		<p class="text-gray-600 mb-6">
			Tómate un momento para reflexionar sobre tu día. Responde las siguientes preguntas de manera honesta.
			No es necesario responder todas, solo aquellas que consideres relevantes.
		</p>

		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			{#each preguntas as pregunta, index}
				<div>
					<label for="pregunta_{index}" class="block text-sm font-medium text-gray-700 mb-2">
						{index + 1}. {pregunta}
					</label>
					<textarea
						id="pregunta_{index}"
						bind:value={respuestas[index]}
						rows="4"
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="Escribe tu respuesta aquí..."
						disabled={loading}
					></textarea>
				</div>
			{/each}

			<!-- Mensajes de Error/Éxito -->
			{#if error}
				<div class="bg-red-50 border-l-4 border-red-400 p-4">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm text-red-700">{error}</p>
						</div>
					</div>
				</div>
			{/if}

			{#if success}
				<div class="bg-green-50 border-l-4 border-green-400 p-4">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm text-green-700">{success}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Botones -->
			<div class="flex gap-4">
				<button
					type="submit"
					disabled={loading}
					class="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{loading ? 'Guardando...' : 'Guardar Notas'}
				</button>

				<button
					type="button"
					on:click={() => { respuestas = ['', '', '', '']; error = ''; success = ''; }}
					disabled={loading}
					class="flex-1 inline-flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Limpiar
				</button>
			</div>
		</form>
	</div>
</div>
