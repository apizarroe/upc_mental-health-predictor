<script>
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props();

	const idPaciente = $page.params.id;
	const idRespuesta = $page.params.idRespuesta;
	const currentUserId = data.currentUserId;
	const puedeValidarDiagnostico = $derived(
		data.respuesta.estado_procesamiento === 'procesado' && Boolean(data.respuesta.id_evaluacion)
	);

	let isReprocesando = $state(false);
	let mensajeReprocesar = $state(null);
	let observaciones = $state(data.observaciones ?? []);
	let observacionesEditables = $state([]);
	let editandoObservaciones = $state(false);
	let guardandoObservaciones = $state(false);
	let mensajeObservaciones = $state(null);
	let riesgoAtendido = $state(data.respuesta.riesgo_atendido === true);
	let riesgoAtendidoPendiente = $state(data.respuesta.riesgo_atendido === true);

	const tieneObservacionesPropias = $derived(
		observaciones.some((o) => o.id_especialista === currentUserId)
	);
	const puedeEditarObservaciones = $derived(tieneObservacionesPropias || observaciones.length < 3);
	const tieneSenalesRiesgo = $derived(
		(data.respuesta.trastornos_detectados?.risk_assessment?.señales_detectadas?.length ?? 0) > 0
	);
	// Habilitado solo si, al guardar, quedará al menos una observación asociada a la nota
	const habraObservacionesAlGuardar = $derived(
		observaciones.some((o) => o.id_especialista !== currentUserId) ||
			observacionesEditables.some((o) => o.descripcion.trim().length > 0)
	);

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

	function iniciarEdicionObservaciones() {
		// Solo las propias son editables; las ajenas se muestran aparte como solo lectura
		const propias = observaciones.filter((o) => o.id_especialista === currentUserId);
		observacionesEditables =
			propias.length > 0
				? propias.map((o) => ({ id_observacion: o.id_observacion, descripcion: o.descripcion }))
				: [];
		riesgoAtendidoPendiente = riesgoAtendido;
		editandoObservaciones = true;
		mensajeObservaciones = null;
	}

	function agregarObservacion() {
		if (observaciones.length >= 3) return;
		observacionesEditables = [...observacionesEditables, { id_observacion: null, descripcion: '' }];
	}

	function eliminarObservacionEditable(index) {
		observacionesEditables = observacionesEditables.filter((_, i) => i !== index);
	}

	function actualizarObservacion(index, value) {
		observacionesEditables = observacionesEditables.map((o, i) =>
			i === index ? { ...o, descripcion: value } : o
		);
	}

	function alternarRiesgoAtendidoPendiente(checked) {
		// Solo es un cambio local; se persiste recién al presionar "Guardar cambios".
		// Una vez persistido como TRUE no puede revertirse (no existe estado FALSE).
		if (riesgoAtendido) return;
		riesgoAtendidoPendiente = checked;
	}

	async function reprocesarRespuesta() {
		if (
			!confirm(
				'¿Estás seguro de que deseas reprocesar esta respuesta? La evaluación actual será reemplazada.'
			)
		) {
			return;
		}

		isReprocesando = true;
		mensajeReprocesar = null;

		try {
			const response = await fetch(`/api/respuestas/${idRespuesta}/reprocesar`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			const result = await response.json();

			if (result.success) {
				mensajeReprocesar = {
					tipo: 'success',
					texto: 'Respuesta reprocesada exitosamente. Recargando...'
				};
				// Recargar la página después de 1 segundo para ver los nuevos resultados
				setTimeout(() => {
					window.location.reload();
				}, 1000);
			} else {
				mensajeReprocesar = {
					tipo: 'error',
					texto: result.error || 'Error al reprocesar la respuesta'
				};
			}
		} catch (error) {
			console.error('Error al reprocesar:', error);
			mensajeReprocesar = { tipo: 'error', texto: 'Error de conexión al reprocesar la respuesta' };
		} finally {
			isReprocesando = false;
		}
	}

	async function guardarObservaciones() {
		guardandoObservaciones = true;
		mensajeObservaciones = null;

		try {
			const response = await fetch(`/api/respuestas/${idRespuesta}/observaciones`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					observaciones: observacionesEditables
				})
			});

			const result = await response.json();

			if (response.ok && result.success) {
				observaciones = result.observaciones ?? [];
				observacionesEditables = observaciones.map((observacion) => observacion.descripcion);
				editandoObservaciones = false;

				let riesgoAtendidoOk = true;
				if (riesgoAtendidoPendiente && !riesgoAtendido && observaciones.length > 0) {
					try {
						const respRiesgo = await fetch(`/api/respuestas/${idRespuesta}/riesgo-atendido`, {
							method: 'POST'
						});
						const resultRiesgo = await respRiesgo.json();
						if (respRiesgo.ok && resultRiesgo.success) {
							riesgoAtendido = true;
						} else {
							riesgoAtendidoOk = false;
						}
					} catch (error) {
						console.error('Error al marcar riesgo atendido:', error);
						riesgoAtendidoOk = false;
					}
				}
				riesgoAtendidoPendiente = riesgoAtendido;

				mensajeObservaciones = {
					tipo: riesgoAtendidoOk ? 'success' : 'error',
					texto: riesgoAtendidoOk
						? 'Observaciones guardadas correctamente.'
						: 'Observaciones guardadas, pero no se pudo registrar la acción frente al riesgo.'
				};
			} else {
				mensajeObservaciones = {
					tipo: 'error',
					texto: result.error || 'No se pudieron guardar las observaciones.'
				};
			}
		} catch (error) {
			console.error('Error al guardar observaciones:', error);
			mensajeObservaciones = {
				tipo: 'error',
				texto: 'Error de conexión al guardar las observaciones.'
			};
		} finally {
			guardandoObservaciones = false;
		}
	}
</script>

<svelte:head>
	<title>Detalle de Nota - {data.paciente.nombres} {data.paciente.apellidos}</title>
</svelte:head>

<div class="py-8">
	<div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<button
				onclick={() => goto(resolve(`/pacientes/${idPaciente}/notas`))}
				class="mb-4 flex items-center gap-2 text-white/80 hover:text-white"
			>
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
				Volver a Notas
			</button>

			<div class="flex items-start justify-between">
				<div>
					<h1 class="flex items-center gap-3 text-3xl font-bold text-white">
						<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						Detalle de Nota Diaria
					</h1>
					<p class="mt-2 text-white/80">
						Paciente: <span class="font-semibold"
							>{data.paciente.nombres} {data.paciente.apellidos}</span
						>
						<span class="mx-2">•</span>
						Fecha:
						<span class="font-semibold">{formatearFecha(data.respuesta.fecha_respuesta)}</span>
					</p>
				</div>

				<div class="flex flex-wrap items-center justify-end gap-3">
					{#if puedeValidarDiagnostico}
						<a
							href={resolve(`/pacientes/${idPaciente}/notas/${idRespuesta}/validacion`)}
							class="flex items-center gap-2 rounded-lg border border-emerald-300/40 bg-emerald-500/15 px-6 py-3 font-semibold text-white backdrop-blur-sm transition-all duration-300 hover:bg-emerald-500/25"
						>
							Validar diagnóstico
						</a>
					{/if}

					<button
						onclick={reprocesarRespuesta}
						disabled={isReprocesando}
						class="flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-6 py-3 font-semibold text-white backdrop-blur-sm transition-all duration-300 hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{#if isReprocesando}
							<svg
								class="h-5 w-5 animate-spin"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								/>
							</svg>
							Reprocesando...
						{:else}
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								/>
							</svg>
							Reprocesar
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Mensaje de reprocesamiento -->
		{#if mensajeReprocesar}
			<div class="mb-6">
				{#if mensajeReprocesar.tipo === 'success'}
					<div class="rounded border-l-4 border-green-500 bg-green-50 p-4">
						<div class="flex items-center gap-3">
							<svg class="h-5 w-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<p class="text-sm font-medium text-green-800">{mensajeReprocesar.texto}</p>
						</div>
					</div>
				{:else}
					<div class="rounded border-l-4 border-red-500 bg-red-50 p-4">
						<div class="flex items-center gap-3">
							<svg class="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
									clip-rule="evenodd"
								/>
							</svg>
							<p class="text-sm font-medium text-red-800">{mensajeReprocesar.texto}</p>
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
			<!-- Columna principal: Respuestas -->
			<div class="space-y-6 lg:col-span-2">
				<!-- Respuestas del Paciente -->
				<div class="card">
					<div class="card-body">
						<h2 class="mb-6 flex items-center gap-2 text-xl font-bold text-neutral-900">
							<svg
								class="h-6 w-6 text-purple-600"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
								/>
							</svg>
							Respuestas del Cuestionario
						</h2>

						<div class="space-y-6">
							<!-- Pregunta 1 -->
							<div>
								<h3 class="mb-2 text-sm font-semibold text-neutral-700">
									1. ¿Cómo fue tu día hoy?
								</h3>
								<p class="rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-neutral-900">
									{data.respuesta.respuestas.question1}
								</p>
							</div>

							<!-- Pregunta 2 -->
							<div>
								<h3 class="mb-2 text-sm font-semibold text-neutral-700">
									2. ¿Cómo te sientes en este momento?
								</h3>
								<p class="rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-neutral-900">
									{data.respuesta.respuestas.question2}
								</p>
							</div>

							<!-- Pregunta 3 -->
							<div>
								<h3 class="mb-2 text-sm font-semibold text-neutral-700">
									3. ¿Cómo describirías tu estado de ánimo?
								</h3>
								<p class="rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-neutral-900">
									{data.respuesta.respuestas.question3}
								</p>
							</div>

							<!-- Pregunta 4 -->
							<div>
								<h3 class="mb-2 text-sm font-semibold text-neutral-700">
									4. ¿Qué situaciones te han afectado hoy?
								</h3>
								<p class="rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-neutral-900">
									{data.respuesta.respuestas.question4}
								</p>
							</div>
						</div>
					</div>
				</div>

				<div class="card">
					<div class="card-body">
						<div class="mb-6 flex items-center justify-between gap-4">
							<h2 class="flex items-center gap-2 text-xl font-bold text-neutral-900">
								<svg
									class="h-6 w-6 text-amber-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
								Observaciones
							</h2>

							{#if !editandoObservaciones && puedeEditarObservaciones}
								<button
									type="button"
									onclick={iniciarEdicionObservaciones}
									class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-neutral-200 text-neutral-600 transition hover:border-amber-300 hover:bg-amber-50 hover:text-amber-700"
									aria-label="Editar observaciones"
									title="Editar observaciones"
								>
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
										/>
									</svg>
								</button>
							{/if}
						</div>

						{#if tieneSenalesRiesgo}
							<div class="mb-4 rounded-lg border border-neutral-200 bg-neutral-50 p-4">
								{#if editandoObservaciones}
									<label
										class="flex items-center gap-3 text-sm text-neutral-700 {riesgoAtendido ||
										!habraObservacionesAlGuardar
											? ''
											: 'cursor-pointer'}"
									>
										<input
											type="checkbox"
											class="checkbox checkbox-sm checkbox-error"
											checked={riesgoAtendidoPendiente}
											disabled={riesgoAtendido || !habraObservacionesAlGuardar}
											onchange={(event) =>
												alternarRiesgoAtendidoPendiente(event.currentTarget.checked)}
										/>
										<span>Se tomó acción frente a la(s) señal(es) de riesgo detectadas en esta nota</span>
									</label>

									{#if !riesgoAtendido}
										{#if habraObservacionesAlGuardar}
											<p class="mt-2 pl-7 text-xs text-neutral-500">
												Este cambio se guardará junto con tus observaciones al presionar "Guardar
												cambios".
											</p>
										{:else}
											<p class="mt-2 pl-7 text-xs text-neutral-500">
												Para marcar esta acción primero debes registrar al menos una observación.
											</p>
										{/if}
									{/if}
								{:else}
									<div class="flex items-center gap-3 text-sm text-neutral-700">
										<input
											type="checkbox"
											class="checkbox checkbox-sm checkbox-error"
											checked={riesgoAtendido}
											disabled
										/>
										<span>
											{#if riesgoAtendido}
												<span class="font-semibold text-neutral-900"
													>Se tomó acción frente al riesgo detectado en esta nota.</span
												>
											{:else}
												Aún no se ha marcado una acción frente a la(s) señal(es) de riesgo
												detectadas en esta nota.
											{/if}
										</span>
									</div>
								{/if}
							</div>
						{/if}

						{#if mensajeObservaciones}
							<div
								class="mb-4 rounded-lg border p-4 {mensajeObservaciones.tipo === 'success'
									? 'border-green-200 bg-green-50 text-green-800'
									: 'border-red-200 bg-red-50 text-red-800'}"
							>
								<p class="text-sm font-medium">{mensajeObservaciones.texto}</p>
							</div>
						{/if}

						{#if editandoObservaciones}
							<div class="space-y-4">
								<!-- Observaciones de otros especialistas (solo lectura) -->
								{#each observaciones.filter((o) => o.id_especialista !== currentUserId) as obs (obs.id_observacion ?? obs.descripcion)}
									<div class="rounded-lg border border-neutral-100 bg-gray-50 p-4 opacity-70">
										<div class="mb-1 flex items-center justify-between">
											<span class="text-xs font-medium text-neutral-500">Solo lectura</span>
											<div class="text-right text-xs text-neutral-400">
												{#if obs.especialista_nombres}
													<span class="block"
														>{obs.especialista_nombres} {obs.especialista_apellidos}</span
													>
												{/if}
											</div>
										</div>
										<p class="text-sm text-neutral-600">{obs.descripcion}</p>
									</div>
								{/each}

								<!-- Observaciones propias editables -->
								{#each observacionesEditables as obs, index (`editable-${index}`)}
									<div>
										<div class="mb-1 flex items-center justify-between">
											<label
												class="text-sm font-semibold text-neutral-700"
												for={`observacion-${index}`}
											>
												Observación
											</label>
											<button
												type="button"
												onclick={() => eliminarObservacionEditable(index)}
												class="text-xs text-red-500 hover:text-red-700"
												title="Eliminar observación"
											>
												Eliminar
											</button>
										</div>
										<textarea
											id={`observacion-${index}`}
											class="min-h-28 w-full rounded-lg border border-neutral-300 bg-white p-4 text-neutral-900 focus:border-amber-500 focus:ring-2 focus:ring-amber-200 focus:outline-none"
											placeholder="Escribe una observación"
											value={obs.descripcion}
											oninput={(event) => actualizarObservacion(index, event.currentTarget.value)}
										></textarea>
									</div>
								{/each}

								{#if observaciones.length < 3}
									<button
										type="button"
										onclick={agregarObservacion}
										class="inline-flex items-center gap-2 rounded-lg bg-amber-100 px-4 py-2 text-sm font-semibold text-amber-800 transition hover:bg-amber-200"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 4v16m8-8H4"
											/>
										</svg>
										Agregar observación
									</button>
								{:else}
									<p class="text-xs text-neutral-400">Límite de 3 observaciones alcanzado.</p>
								{/if}

								<div class="flex justify-end">
									<button
										type="button"
										onclick={guardarObservaciones}
										disabled={guardandoObservaciones}
										class="inline-flex items-center gap-2 rounded-lg bg-amber-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-60"
									>
										{#if guardandoObservaciones}
											<svg
												class="h-4 w-4 animate-spin"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
												/>
											</svg>
											Guardando...
										{:else}
											<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M5 13l4 4L19 7"
												/>
											</svg>
											Guardar cambios
										{/if}
									</button>
								</div>
							</div>
						{:else if observaciones.length > 0}
							<div class="space-y-4">
								{#each observaciones as observacion, index (observacion.id_observacion ?? `obs-${index}`)}
									<div class="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
										<div class="mb-2 flex items-center justify-between">
											<h3 class="text-sm font-semibold text-neutral-700">
												Observación {index + 1}
											</h3>
											<div class="flex items-start gap-4">
												<div class="text-right text-xs text-neutral-500">
													{#if observacion.especialista_nombres}
														<span class="block"
															>{observacion.especialista_nombres}
															{observacion.especialista_apellidos}</span
														>
													{/if}
													{#if observacion.fecha_observacion}
														<span class="block">
															{new Date(observacion.fecha_observacion).toLocaleString('es-PE', {
																dateStyle: 'medium',
																timeStyle: 'short',
																timeZone: 'America/Lima'
															})}
														</span>
													{/if}
												</div>
											</div>
										</div>
										<p class="whitespace-pre-wrap text-neutral-900">{observacion.descripcion}</p>
									</div>
								{/each}
							</div>
						{:else}
							<div
								class="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-6 text-center text-sm text-neutral-600"
							>
								Aún no hay observaciones registradas para esta nota diaria.
							</div>
						{/if}
					</div>
				</div>
			</div>

			<!-- Columna lateral: Evaluación ML -->
			<div class="space-y-6 lg:col-span-1">
				{#if data.respuesta.estado_procesamiento === 'procesado' && data.respuesta.trastornos_detectados}
					<!-- Resumen de Evaluación -->
					<div class="card border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
						<div class="card-body">
							<h2 class="mb-4 flex items-center gap-2 text-lg font-bold text-neutral-900">
								<svg
									class="h-5 w-5 text-purple-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
									/>
								</svg>
								Evaluación ML
							</h2>

							<!-- Nivel de Riesgo Global -->
							<div
								class="mb-4 rounded-lg border-2 p-4 {getBadgeRiesgo(
									data.respuesta.nivel_riesgo_global
								)}"
							>
								<p class="mb-1 text-xs font-medium tracking-wide uppercase">
									Nivel de Riesgo Global
								</p>
								<p class="flex items-center gap-2 text-2xl font-bold">
									<span>{getIconoRiesgo(data.respuesta.nivel_riesgo_global)}</span>
									<span class="capitalize">{data.respuesta.nivel_riesgo_global}</span>
								</p>
							</div>

							<!-- Requiere Atención -->
							{#if data.respuesta.requiere_atencion}
								<div class="mb-4 rounded border-l-4 border-red-500 bg-red-50 p-3">
									<p class="flex items-center gap-2 text-sm font-semibold text-red-800">
										<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
											<path
												fill-rule="evenodd"
												d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
												clip-rule="evenodd"
											/>
										</svg>
										Requiere Atención
									</p>
									<p class="mt-1 text-xs text-red-700">Se recomienda seguimiento especializado</p>
								</div>
							{/if}

							<!-- Señales de Riesgo Detectadas -->
							{#if data.respuesta.trastornos_detectados?.risk_assessment?.señales_detectadas?.length > 0}
								{@const señales = data.respuesta.trastornos_detectados.risk_assessment.señales_detectadas}
								{@const etiquetas = {
									ideacion_suicida: 'Ideación suicida',
									ideacion_pasiva: 'Ideación pasiva',
									autolesion: 'Autolesión',
									crisis_panico: 'Crisis de pánico',
									perdida_control: 'Pérdida de control',
									colapso: 'Colapso emocional',
									descompensacion: 'Descompensación'
								}}
								{@const agrupadas = señales.reduce((acc, s) => {
									if (!acc[s.tipo]) acc[s.tipo] = { nivel: s.nivel, frases: [] };
									acc[s.tipo].frases.push(s.frase);
									return acc;
								}, {})}
								<h3 class="mb-3 flex items-center gap-2 text-sm font-semibold text-neutral-700">
									<svg class="h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
									</svg>
									Señales de riesgo detectadas
								</h3>
								<div class="rounded-lg border border-red-200 bg-red-50 p-3">
									<ul class="space-y-2">
										{#each Object.entries(agrupadas) as [tipo, grupo]}
											<li>
												<p class="text-sm font-semibold text-red-700">{etiquetas[tipo] ?? tipo}</p>
												<ul class="mt-0.5 space-y-0.5 pl-3">
													{#each grupo.frases as frase}
														<li class="text-sm italic text-neutral-700">"{frase}"</li>
													{/each}
												</ul>
											</li>
										{/each}
									</ul>
								</div>
							{/if}
						</div>
					</div>

					<!-- Trastornos Detectados -->
					<div class="card">
						<div class="card-body">
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-neutral-700">Trastornos Detectados</h3>

								<!-- Depresión -->
								<div class="rounded-lg border border-neutral-200 bg-white p-3">
									<div class="mb-2 flex items-center justify-between">
										<span class="text-sm font-medium text-neutral-700">Depresión</span>
										<span
											class="rounded px-2 py-1 text-xs {data.respuesta.trastornos_detectados
												.depression.has_condition
												? 'bg-red-100 text-red-800'
												: 'bg-green-100 text-green-800'}"
										>
											{data.respuesta.trastornos_detectados.depression.has_condition
												? 'Detectada'
												: 'No detectada'}
										</span>
									</div>
									<div class="mb-2">
										<div class="mb-1 flex items-center justify-between text-xs text-neutral-600">
											<span>Probabilidad</span>
											<span class="font-semibold"
												>{Math.round(
													data.respuesta.trastornos_detectados.depression.probability * 100
												)}%</span
											>
										</div>
										<div class="h-2 w-full rounded-full bg-neutral-200">
											<div
												class="h-2 rounded-full {data.respuesta.trastornos_detectados.depression
													.probability >= 0.7
													? 'bg-red-500'
													: data.respuesta.trastornos_detectados.depression.probability >= 0.5
														? 'bg-yellow-500'
														: 'bg-green-500'}"
												style="width: {data.respuesta.trastornos_detectados.depression.probability *
													100}%"
											></div>
										</div>
									</div>
									<p class="text-xs text-neutral-600">
										Confianza: {Math.round(
											data.respuesta.trastornos_detectados.depression.confidence * 100
										)}%
									</p>
								</div>

								<!-- Ansiedad -->
								<div class="rounded-lg border border-neutral-200 bg-white p-3">
									<div class="mb-2 flex items-center justify-between">
										<span class="text-sm font-medium text-neutral-700">Ansiedad</span>
										<span
											class="rounded px-2 py-1 text-xs {data.respuesta.trastornos_detectados.anxiety
												.has_condition
												? 'bg-red-100 text-red-800'
												: 'bg-green-100 text-green-800'}"
										>
											{data.respuesta.trastornos_detectados.anxiety.has_condition
												? 'Detectada'
												: 'No detectada'}
										</span>
									</div>
									<div class="mb-2">
										<div class="mb-1 flex items-center justify-between text-xs text-neutral-600">
											<span>Probabilidad</span>
											<span class="font-semibold"
												>{Math.round(
													data.respuesta.trastornos_detectados.anxiety.probability * 100
												)}%</span
											>
										</div>
										<div class="h-2 w-full rounded-full bg-neutral-200">
											<div
												class="h-2 rounded-full {data.respuesta.trastornos_detectados.anxiety
													.probability >= 0.7
													? 'bg-red-500'
													: data.respuesta.trastornos_detectados.anxiety.probability >= 0.5
														? 'bg-yellow-500'
														: 'bg-green-500'}"
												style="width: {data.respuesta.trastornos_detectados.anxiety.probability *
													100}%"
											></div>
										</div>
									</div>
									<p class="text-xs text-neutral-600">
										Confianza: {Math.round(
											data.respuesta.trastornos_detectados.anxiety.confidence * 100
										)}%
									</p>
								</div>
							</div>
							{#if data.respuesta.interpretacion}
								<div class="mt-3 border-t border-neutral-200 pt-3">
									<h3 class="mb-3 flex items-center gap-2 text-sm font-semibold text-neutral-700">
										<svg
											class="h-4 w-4 text-blue-600"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
										Interpretación
									</h3>
									<p class="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-neutral-700">
										{data.respuesta.interpretacion}
									</p>
								</div>
							{/if}
						</div>
					</div>

					<!-- Palabras Clave -->
					{#if data.respuesta.palabras_clave}
						<div class="card">
							<div class="card-body">
								<h3 class="mb-3 text-sm font-semibold text-neutral-700">
									Palabras Clave Detectadas
								</h3>

								{#if data.respuesta.palabras_clave.depression && data.respuesta.palabras_clave.depression.length > 0}
									<div class="mb-3">
										<p class="mb-2 text-xs text-neutral-600">Depresión:</p>
										<div class="flex flex-wrap gap-1">
											{#each data.respuesta.palabras_clave.depression as palabra (`depression-${palabra}`)}
												<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800">
													{palabra}
												</span>
											{/each}
										</div>
									</div>
								{/if}

								{#if data.respuesta.palabras_clave.anxiety && data.respuesta.palabras_clave.anxiety.length > 0}
									<div>
										<p class="mb-2 text-xs text-neutral-600">Ansiedad:</p>
										<div class="flex flex-wrap gap-1">
											{#each data.respuesta.palabras_clave.anxiety as palabra (`anxiety-${palabra}`)}
												<span class="rounded-full bg-yellow-100 px-2 py-1 text-xs text-yellow-800">
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
								<h3 class="mb-3 text-xs font-semibold tracking-wide text-neutral-600 uppercase">
									Información Técnica
								</h3>
								<div class="space-y-2 text-xs text-neutral-600">
									<div class="flex justify-between">
										<span>Modelo:</span>
										<span class="font-mono text-neutral-800">{data.respuesta.modelo_tipo}</span>
									</div>
									<div class="flex justify-between">
										<span>BERT:</span>
										<span class="font-mono text-[10px] text-neutral-800"
											>{data.respuesta.modelo_version?.split('/').pop() || 'N/A'}</span
										>
									</div>
									<div class="flex justify-between">
										<span>Evaluado:</span>
										<span class="text-neutral-800"
											>{formatearFecha(data.respuesta.fecha_evaluacion)}</span
										>
									</div>
								</div>
							</div>
						</div>
					{/if}
				{:else if data.respuesta.estado_procesamiento === 'error'}
					<div class="card border-2 border-red-200 bg-red-50">
						<div class="card-body">
							<h3 class="mb-2 flex items-center gap-2 text-sm font-semibold text-red-800">
								<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
										clip-rule="evenodd"
									/>
								</svg>
								Error en Procesamiento
							</h3>
							<p class="text-sm text-red-700">
								{data.respuesta.error_mensaje ||
									'Ocurrió un error al procesar esta respuesta con el modelo ML'}
							</p>
						</div>
					</div>
				{:else}
					<div class="card border-2 border-yellow-200 bg-yellow-50">
						<div class="card-body">
							<h3 class="mb-2 flex items-center gap-2 text-sm font-semibold text-yellow-800">
								<svg
									class="h-5 w-5 animate-spin"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
									/>
								</svg>
								Procesamiento Pendiente
							</h3>
							<p class="text-sm text-yellow-700">
								Esta respuesta está siendo procesada por el modelo ML. La evaluación estará
								disponible en breve.
							</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
