<script>
	let { data } = $props();

	// Formatear fecha y hora
	function formatFecha(fecha) {
		const date = new Date(fecha);
		return date.toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatHora(fecha) {
		const date = new Date(fecha);
		return date.toLocaleTimeString('es-PE', {
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	// Obtener badge de estado
	function getEstadoBadge(estado) {
		const badges = {
			pendiente: { color: 'bg-yellow-100 text-yellow-800', text: 'Pendiente' },
			procesado: { color: 'bg-green-100 text-green-800', text: 'Procesado' },
			error: { color: 'bg-red-100 text-red-800', text: 'Error' }
		};
		return badges[estado] || badges.pendiente;
	}

	// Ver detalle de una respuesta
	let modalRespuesta = $state(null);

	function verDetalle(respuesta) {
		console.log('🔍 Ver detalle de respuesta:', respuesta);
		console.log('   Tipo de respuestas:', typeof respuesta.respuestas);
		console.log('   Contenido respuestas:', respuesta.respuestas);
		if (respuesta.respuestas) {
			console.log('   question1:', respuesta.respuestas.question1);
			console.log('   question2:', respuesta.respuestas.question2);
			console.log('   question3:', respuesta.respuestas.question3);
			console.log('   question4:', respuesta.respuestas.question4);
		}
		modalRespuesta = respuesta;
	}

	function cerrarModal() {
		modalRespuesta = null;
	}
</script>

<svelte:head>
	<title>Historial del Día - Portal de Pacientes</title>
</svelte:head>

<div class="p-8">
	<div class="max-w-5xl mx-auto">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center gap-4 mb-4">
				<button
					onclick={() => window.location.href = '/paciente/notas'}
					class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
					Volver
				</button>
			</div>
			<h1 class="text-3xl font-bold text-white mb-2">Historial del Día</h1>
			<p class="text-white/80">Respuestas registradas hoy ({formatFecha(new Date())})</p>
		</div>

		<!-- Lista de respuestas -->
		{#if data.respuestas.length === 0}
			<div class="bg-white rounded-2xl shadow-2xl p-12 text-center">
				<div class="mb-4">
					<svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<h3 class="text-xl font-semibold text-gray-700 mb-2">No hay respuestas registradas hoy</h3>
				<p class="text-gray-500 mb-6">Aún no has completado el cuestionario diario. Puedes hacerlo hasta 2 veces al día.</p>
				<button
					onclick={() => window.location.href = '/paciente/notas'}
					class="px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 hover:shadow-xl"
					style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
				>
					Completar Cuestionario
				</button>
			</div>
		{:else}
			<div class="space-y-6">
				{#each data.respuestas as respuesta, index}
					<div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
						<div class="p-6">
							<!-- Header de la tarjeta -->
							<div class="flex justify-between items-start mb-4">
								<div>
									<h3 class="text-lg font-semibold text-gray-800">
										Respuesta #{data.respuestas.length - index}
									</h3>
									<p class="text-sm text-gray-500">
										{formatHora(respuesta.fecha_respuesta)}
									</p>
								</div>
								<div class="flex gap-2 items-center">
									{#if respuesta.estado_procesamiento}
										{@const badge = getEstadoBadge(respuesta.estado_procesamiento)}
										<span class="px-3 py-1 rounded-full text-xs font-semibold {badge.color}">
											{badge.text}
										</span>
									{/if}
								</div>
							</div>

							<!-- Mensaje informativo -->
							<div class="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
								<div class="flex items-start gap-3">
									<svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									<div>
										<h4 class="text-sm font-semibold text-blue-900 mb-1">Respuesta registrada exitosamente</h4>
										<p class="text-sm text-blue-700">
											Tu respuesta ha sido procesada. Los resultados de la evaluación son confidenciales y solo están disponibles para tu especialista.
										</p>
									</div>
								</div>
							</div>

							<!-- Botón ver detalle -->
							<button
								onclick={() => verDetalle(respuesta)}
								class="w-full px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold rounded-lg transition-colors"
							>
								Ver mis respuestas
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<!-- Modal para ver detalle -->
{#if modalRespuesta}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onclick={cerrarModal}>
		<div class="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
			<div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
				<h2 class="text-2xl font-bold text-gray-800">Respuestas del Cuestionario</h2>
				<button
					onclick={cerrarModal}
					class="text-gray-400 hover:text-gray-600 transition-colors"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<div class="p-6 space-y-6">
				<!-- Pregunta 1 -->
				<div>
					<h3 class="text-sm font-semibold text-gray-700 mb-2">1. ¿Cómo fue tu día hoy?</h3>
					<p class="text-gray-800 bg-gray-50 p-4 rounded-lg">{modalRespuesta.respuestas.question1}</p>
				</div>

				<!-- Pregunta 2 -->
				<div>
					<h3 class="text-sm font-semibold text-gray-700 mb-2">2. ¿Cómo te sientes en este momento?</h3>
					<p class="text-gray-800 bg-gray-50 p-4 rounded-lg">{modalRespuesta.respuestas.question2}</p>
				</div>

				<!-- Pregunta 3 -->
				<div>
					<h3 class="text-sm font-semibold text-gray-700 mb-2">3. ¿Cómo describirías tu estado de ánimo?</h3>
					<p class="text-gray-800 bg-gray-50 p-4 rounded-lg">{modalRespuesta.respuestas.question3}</p>
				</div>

				<!-- Pregunta 4 -->
				<div>
					<h3 class="text-sm font-semibold text-gray-700 mb-2">4. ¿Qué situaciones has experimentado hoy?</h3>
					<p class="text-gray-800 bg-gray-50 p-4 rounded-lg">{modalRespuesta.respuestas.question4}</p>
				</div>

				<!-- Info adicional -->
				<div class="pt-4 border-t border-gray-200">
					<p class="text-sm text-gray-500">
						Registrado: {formatFecha(modalRespuesta.fecha_respuesta)} a las {formatHora(modalRespuesta.fecha_respuesta)}
					</p>
				</div>
			</div>

			<div class="sticky bottom-0 bg-gray-50 p-6 border-t border-gray-200">
				<button
					onclick={cerrarModal}
					class="w-full px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
