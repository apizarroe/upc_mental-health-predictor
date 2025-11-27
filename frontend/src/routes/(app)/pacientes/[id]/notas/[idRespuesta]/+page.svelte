<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props();

	const idPaciente = $page.params.id;

	function formatearFecha(fecha) {
		return new Date(fecha).toLocaleString('es-PE', {
			dateStyle: 'full',
			timeStyle: 'medium',
			timeZone: 'America/Lima'
		});
	}

	function getBadgeRiesgo(nivel) {
		const badges = {
			bajo: 'bg-green-100 text-green-800 border-green-200',
			moderado: 'bg-yellow-100 text-yellow-800 border-yellow-200',
			alto: 'bg-red-100 text-red-800 border-red-200'
		};
		return badges[nivel] || 'bg-gray-100 text-gray-800 border-gray-200';
	}

	function getIconoRiesgo(nivel) {
		if (nivel === 'alto') return '🔴';
		if (nivel === 'moderado') return '🟡';
		return '🟢';
	}
</script>

<svelte:head>
	<title>Detalle de Nota - {data.paciente.nombres} {data.paciente.apellidos}</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<button
				onclick={() => goto(`/pacientes/${idPaciente}/notas`)}
				class="text-white/80 hover:text-white mb-4 flex items-center gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
				Volver a Notas
			</button>
			<h1 class="text-3xl font-bold text-white flex items-center gap-3">
				<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
				Detalle de Nota Diaria
			</h1>
			<p class="mt-2 text-white/80">
				Paciente: <span class="font-semibold">{data.paciente.nombres} {data.paciente.apellidos}</span>
				<span class="mx-2">•</span>
				Fecha: <span class="font-semibold">{formatearFecha(data.respuesta.fecha_respuesta)}</span>
			</p>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Columna principal: Respuestas -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Respuestas del Paciente -->
				<div class="card">
					<div class="card-body">
						<h2 class="text-xl font-bold text-neutral-900 mb-6 flex items-center gap-2">
							<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
							</svg>
							Respuestas del Cuestionario
						</h2>

						<div class="space-y-6">
							<!-- Pregunta 1 -->
							<div>
								<h3 class="text-sm font-semibold text-neutral-700 mb-2">1. ¿Cómo fue tu día hoy?</h3>
								<p class="text-neutral-900 bg-neutral-50 p-4 rounded-lg border border-neutral-200">
									{data.respuesta.respuestas.question1}
								</p>
							</div>

							<!-- Pregunta 2 -->
							<div>
								<h3 class="text-sm font-semibold text-neutral-700 mb-2">2. ¿Cómo te sientes en este momento?</h3>
								<p class="text-neutral-900 bg-neutral-50 p-4 rounded-lg border border-neutral-200">
									{data.respuesta.respuestas.question2}
								</p>
							</div>

							<!-- Pregunta 3 -->
							<div>
								<h3 class="text-sm font-semibold text-neutral-700 mb-2">3. ¿Cómo describirías tu estado de ánimo?</h3>
								<p class="text-neutral-900 bg-neutral-50 p-4 rounded-lg border border-neutral-200">
									{data.respuesta.respuestas.question3}
								</p>
							</div>

							<!-- Pregunta 4 -->
							<div>
								<h3 class="text-sm font-semibold text-neutral-700 mb-2">4. ¿Qué situaciones te han afectado hoy?</h3>
								<p class="text-neutral-900 bg-neutral-50 p-4 rounded-lg border border-neutral-200">
									{data.respuesta.respuestas.question4}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Columna lateral: Evaluación ML -->
			<div class="lg:col-span-1 space-y-6">
				{#if data.respuesta.estado_procesamiento === 'procesado' && data.respuesta.trastornos_detectados}
					<!-- Resumen de Evaluación -->
					<div class="card bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-purple-200">
						<div class="card-body">
							<h2 class="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
								<svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
								</svg>
								Evaluación ML
							</h2>

							<!-- Nivel de Riesgo Global -->
							<div class="mb-4 p-4 rounded-lg border-2 {getBadgeRiesgo(data.respuesta.nivel_riesgo_global)}">
								<p class="text-xs font-medium uppercase tracking-wide mb-1">Nivel de Riesgo Global</p>
								<p class="text-2xl font-bold flex items-center gap-2">
									<span>{getIconoRiesgo(data.respuesta.nivel_riesgo_global)}</span>
									<span class="capitalize">{data.respuesta.nivel_riesgo_global}</span>
								</p>
							</div>

							<!-- Requiere Atención -->
							{#if data.respuesta.requiere_atencion}
								<div class="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
									<p class="text-sm font-semibold text-red-800 flex items-center gap-2">
										<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
										</svg>
										Requiere Atención
									</p>
									<p class="text-xs text-red-700 mt-1">Se recomienda seguimiento especializado</p>
								</div>
							{/if}

							<!-- Trastornos Detectados -->
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-neutral-700">Trastornos Detectados</h3>

								<!-- Depresión -->
								<div class="bg-white p-3 rounded-lg border border-neutral-200">
									<div class="flex items-center justify-between mb-2">
										<span class="text-sm font-medium text-neutral-700">Depresión</span>
										<span class="text-xs px-2 py-1 rounded {data.respuesta.trastornos_detectados.depression.has_condition ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
											{data.respuesta.trastornos_detectados.depression.has_condition ? 'Detectada' : 'No detectada'}
										</span>
									</div>
									<div class="mb-2">
										<div class="flex items-center justify-between text-xs text-neutral-600 mb-1">
											<span>Probabilidad</span>
											<span class="font-semibold">{Math.round(data.respuesta.trastornos_detectados.depression.probability * 100)}%</span>
										</div>
										<div class="w-full bg-neutral-200 rounded-full h-2">
											<div
												class="h-2 rounded-full {data.respuesta.trastornos_detectados.depression.probability >= 0.7 ? 'bg-red-500' : data.respuesta.trastornos_detectados.depression.probability >= 0.5 ? 'bg-yellow-500' : 'bg-green-500'}"
												style="width: {data.respuesta.trastornos_detectados.depression.probability * 100}%"
											></div>
										</div>
									</div>
									<p class="text-xs text-neutral-600">
										Confianza: {Math.round(data.respuesta.trastornos_detectados.depression.confidence * 100)}%
									</p>
								</div>

								<!-- Ansiedad -->
								<div class="bg-white p-3 rounded-lg border border-neutral-200">
									<div class="flex items-center justify-between mb-2">
										<span class="text-sm font-medium text-neutral-700">Ansiedad</span>
										<span class="text-xs px-2 py-1 rounded {data.respuesta.trastornos_detectados.anxiety.has_condition ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
											{data.respuesta.trastornos_detectados.anxiety.has_condition ? 'Detectada' : 'No detectada'}
										</span>
									</div>
									<div class="mb-2">
										<div class="flex items-center justify-between text-xs text-neutral-600 mb-1">
											<span>Probabilidad</span>
											<span class="font-semibold">{Math.round(data.respuesta.trastornos_detectados.anxiety.probability * 100)}%</span>
										</div>
										<div class="w-full bg-neutral-200 rounded-full h-2">
											<div
												class="h-2 rounded-full {data.respuesta.trastornos_detectados.anxiety.probability >= 0.7 ? 'bg-red-500' : data.respuesta.trastornos_detectados.anxiety.probability >= 0.5 ? 'bg-yellow-500' : 'bg-green-500'}"
												style="width: {data.respuesta.trastornos_detectados.anxiety.probability * 100}%"
											></div>
										</div>
									</div>
									<p class="text-xs text-neutral-600">
										Confianza: {Math.round(data.respuesta.trastornos_detectados.anxiety.confidence * 100)}%
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Interpretación -->
					{#if data.respuesta.interpretacion}
						<div class="card">
							<div class="card-body">
								<h3 class="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
									<svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									Interpretación
								</h3>
								<p class="text-sm text-neutral-700 bg-blue-50 p-3 rounded-lg border border-blue-200">
									{data.respuesta.interpretacion}
								</p>
							</div>
						</div>
					{/if}

					<!-- Palabras Clave -->
					{#if data.respuesta.palabras_clave}
						<div class="card">
							<div class="card-body">
								<h3 class="text-sm font-semibold text-neutral-700 mb-3">Palabras Clave Detectadas</h3>

								{#if data.respuesta.palabras_clave.depression && data.respuesta.palabras_clave.depression.length > 0}
									<div class="mb-3">
										<p class="text-xs text-neutral-600 mb-2">Depresión:</p>
										<div class="flex flex-wrap gap-1">
											{#each data.respuesta.palabras_clave.depression as palabra}
												<span class="text-xs px-2 py-1 bg-red-100 text-red-800 rounded-full">
													{palabra}
												</span>
											{/each}
										</div>
									</div>
								{/if}

								{#if data.respuesta.palabras_clave.anxiety && data.respuesta.palabras_clave.anxiety.length > 0}
									<div>
										<p class="text-xs text-neutral-600 mb-2">Ansiedad:</p>
										<div class="flex flex-wrap gap-1">
											{#each data.respuesta.palabras_clave.anxiety as palabra}
												<span class="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
													{palabra}
												</span>
											{/each}
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Información del Modelo -->
					{#if data.respuesta.modelo_nombre}
						<div class="card bg-neutral-50">
							<div class="card-body">
								<h3 class="text-xs font-semibold text-neutral-600 uppercase tracking-wide mb-3">Información Técnica</h3>
								<div class="space-y-2 text-xs text-neutral-600">
									<div class="flex justify-between">
										<span>Modelo:</span>
										<span class="font-mono text-neutral-800">{data.respuesta.modelo_tipo}</span>
									</div>
									<div class="flex justify-between">
										<span>BERT:</span>
										<span class="font-mono text-neutral-800 text-[10px]">{data.respuesta.modelo_version?.split('/').pop() || 'N/A'}</span>
									</div>
									<div class="flex justify-between">
										<span>Evaluado:</span>
										<span class="text-neutral-800">{formatearFecha(data.respuesta.fecha_evaluacion)}</span>
									</div>
								</div>
							</div>
						</div>
					{/if}

				{:else if data.respuesta.estado_procesamiento === 'error'}
					<div class="card bg-red-50 border-2 border-red-200">
						<div class="card-body">
							<h3 class="text-sm font-semibold text-red-800 mb-2 flex items-center gap-2">
								<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								</svg>
								Error en Procesamiento
							</h3>
							<p class="text-sm text-red-700">
								{data.respuesta.error_mensaje || 'Ocurrió un error al procesar esta respuesta con el modelo ML'}
							</p>
						</div>
					</div>
				{:else}
					<div class="card bg-yellow-50 border-2 border-yellow-200">
						<div class="card-body">
							<h3 class="text-sm font-semibold text-yellow-800 mb-2 flex items-center gap-2">
								<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
								</svg>
								Procesamiento Pendiente
							</h3>
							<p class="text-sm text-yellow-700">
								Esta respuesta está siendo procesada por el modelo ML. La evaluación estará disponible en breve.
							</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
