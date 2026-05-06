<script>
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let { data } = $props();

	const idPaciente = data.paciente.id_paciente;
	const idRespuesta = data.respuesta.id_respuesta;
	const esAdmin = data.user?.rol === 'admin';

	const diagnosticoModelo = data.diagnosticoModelo ?? {
		depression: false,
		anxiety: false
	};

	const trastornos = data.respuesta.trastornos_detectados ?? {};

	const validacionInicial = data.validacionActual;
	let validacionActual = $state(validacionInicial);
	let retrainingStatus = $state(data.retrainingStatus);
	let guardando = $state(false);
	let iniciandoReentrenamiento = $state(false);
	let mensaje = $state(null);
	let mensajeReentrenamiento = $state(null);

	function inferirDecision(validacion) {
		return (
			validacion?.coincidencias?.decision ??
			(validacion?.util_para_entrenamiento ? 'modificar' : 'aceptar')
		);
	}

	function getDiagnosticoInicial(validacion) {
		if (validacion?.diagnostico_especialista) {
			return {
				depression: Boolean(validacion.diagnostico_especialista.depression),
				anxiety: Boolean(validacion.diagnostico_especialista.anxiety)
			};
		}

		return { ...diagnosticoModelo };
	}

	let form = $state({
		decision: inferirDecision(validacionInicial),
		diagnosticoEspecialista: getDiagnosticoInicial(validacionInicial),
		nivelConfianza: validacionInicial?.nivel_confianza ?? 80,
		observaciones: validacionInicial?.observaciones ?? '',
		recomendacionPaciente: validacionInicial?.recomendacion_paciente ?? '',
		requiereSeguimiento: Boolean(validacionInicial?.requiere_seguimiento)
	});

	const requiereReentrenamiento = $derived(form.decision !== 'aceptar');

	function formatearFecha(fecha) {
		return new Date(fecha).toLocaleString('es-PE', {
			dateStyle: 'medium',
			timeStyle: 'short',
			timeZone: 'America/Lima'
		});
	}

	function formatearProbabilidad(valor) {
		return `${Math.round((valor ?? 0) * 100)}%`;
	}

	function getBadgeRiesgo(nivel) {
		const badges = {
			bajo: 'bg-green-100 text-green-800 border-green-200',
			moderado: 'bg-yellow-100 text-yellow-800 border-yellow-200',
			alto: 'bg-red-100 text-red-800 border-red-200'
		};
		return badges[nivel] || 'bg-gray-100 text-gray-800 border-gray-200';
	}

	function seleccionarDecision(decision) {
		form.decision = decision;
		if (decision === 'aceptar') {
			form.diagnosticoEspecialista = { ...diagnosticoModelo };
		}
	}

	function actualizarDiagnostico(campo, valor) {
		form.diagnosticoEspecialista = {
			...form.diagnosticoEspecialista,
			[campo]: valor
		};
	}

	async function cargarEstadoReentrenamiento() {
		if (!esAdmin) return;

		try {
			const response = await fetch('/api/ml/reentrenar');
			const result = await response.json();

			if (response.ok && result.success) {
				retrainingStatus = result.status;
			}
		} catch (error) {
			console.error('Error al consultar estado de reentrenamiento:', error);
		}
	}

	onMount(() => {
		if (!esAdmin) return undefined;

		cargarEstadoReentrenamiento();
		const intervalId = window.setInterval(cargarEstadoReentrenamiento, 5000);

		return () => window.clearInterval(intervalId);
	});

	async function guardarValidacion() {
		guardando = true;
		mensaje = null;

		try {
			const response = await fetch(`/api/respuestas/${idRespuesta}/validacion`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(form)
			});

			const result = await response.json();

			if (response.ok && result.success) {
				validacionActual = result.validacion;
				mensaje = {
					tipo: 'success',
					texto: 'La validación clínica se guardó correctamente.'
				};

				if (form.decision === 'aceptar') {
					form.diagnosticoEspecialista = { ...diagnosticoModelo };
				}

				await cargarEstadoReentrenamiento();
				return;
			}

			mensaje = {
				tipo: 'error',
				texto: result.error || 'No se pudo guardar la validación.'
			};
		} catch (error) {
			console.error('Error al guardar validación:', error);
			mensaje = {
				tipo: 'error',
				texto: 'Error de conexión al guardar la validación.'
			};
		} finally {
			guardando = false;
		}
	}

	async function iniciarReentrenamiento() {
		iniciandoReentrenamiento = true;
		mensajeReentrenamiento = null;

		try {
			const response = await fetch('/api/ml/reentrenar', {
				method: 'POST'
			});
			const result = await response.json();

			if (response.ok && result.success) {
				retrainingStatus = result.status;
				mensajeReentrenamiento = {
					tipo: 'success',
					texto: result.message || 'Reentrenamiento iniciado correctamente.'
				};
				return;
			}

			mensajeReentrenamiento = {
				tipo: response.status === 409 ? 'warning' : 'error',
				texto: result.message || result.error || 'No se pudo iniciar el reentrenamiento.'
			};

			if (result.status) {
				retrainingStatus = result.status;
			}
		} catch (error) {
			console.error('Error al iniciar reentrenamiento:', error);
			mensajeReentrenamiento = {
				tipo: 'error',
				texto: 'Error de conexión al iniciar el reentrenamiento.'
			};
		} finally {
			iniciandoReentrenamiento = false;
		}
	}
</script>

<svelte:head>
	<title>Validación de Diagnóstico - {data.paciente.nombres} {data.paciente.apellidos}</title>
</svelte:head>

<div class="py-8">
	<div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
		<div class="mb-8">
			<button
				onclick={() => goto(resolve(`/pacientes/${idPaciente}/notas/${idRespuesta}`))}
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
				Volver al detalle de la nota
			</button>

			<div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
				<div>
					<h1 class="flex items-center gap-3 text-3xl font-bold text-white">
						<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m5-2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						Validación de Diagnóstico
					</h1>
					<p class="mt-2 text-white/80">
						Paciente:
						<span class="font-semibold">{data.paciente.nombres} {data.paciente.apellidos}</span>
						<span class="mx-2">•</span>
						Nota del
						<span class="font-semibold">{formatearFecha(data.respuesta.fecha_respuesta)}</span>
					</p>
				</div>

				<div
					class="rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white/90 backdrop-blur-sm"
				>
					<p class="font-semibold">Especialista actual</p>
					<p>{data.user.nombres} {data.user.apellidos}</p>
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
			<div class="space-y-6 lg:col-span-2">
				<div class="card border-2 border-emerald-200 bg-gradient-to-br from-emerald-50 to-white">
					<div class="card-body">
						<div class="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
							<div>
								<h2 class="text-xl font-bold text-neutral-900">
									Diagnóstico sugerido por el modelo
								</h2>
								<p class="mt-1 text-sm text-neutral-600">
									Este es el resultado actual de la evaluación ML para la nota diaria.
								</p>
							</div>

							<span
								class="inline-flex w-fit rounded-full border px-3 py-1 text-sm font-semibold {getBadgeRiesgo(
									data.respuesta.nivel_riesgo_global
								)}"
							>
								Riesgo {data.respuesta.nivel_riesgo_global || 'no definido'}
							</span>
						</div>

						<div class="grid gap-4 md:grid-cols-2">
							<div class="rounded-xl border border-neutral-200 bg-white p-4">
								<div class="mb-3 flex items-center justify-between">
									<h3 class="font-semibold text-neutral-900">Depresión</h3>
									<span
										class="rounded-full px-3 py-1 text-xs font-semibold {diagnosticoModelo.depression
											? 'bg-red-100 text-red-700'
											: 'bg-green-100 text-green-700'}"
									>
										{diagnosticoModelo.depression ? 'Detectada' : 'No detectada'}
									</span>
								</div>
								<p class="text-sm text-neutral-600">
									Probabilidad: <span class="font-semibold text-neutral-900"
										>{formatearProbabilidad(trastornos.depression?.probability)}</span
									>
								</p>
								<p class="text-sm text-neutral-600">
									Confianza: <span class="font-semibold text-neutral-900"
										>{formatearProbabilidad(trastornos.depression?.confidence)}</span
									>
								</p>
							</div>

							<div class="rounded-xl border border-neutral-200 bg-white p-4">
								<div class="mb-3 flex items-center justify-between">
									<h3 class="font-semibold text-neutral-900">Ansiedad</h3>
									<span
										class="rounded-full px-3 py-1 text-xs font-semibold {diagnosticoModelo.anxiety
											? 'bg-red-100 text-red-700'
											: 'bg-green-100 text-green-700'}"
									>
										{diagnosticoModelo.anxiety ? 'Detectada' : 'No detectada'}
									</span>
								</div>
								<p class="text-sm text-neutral-600">
									Probabilidad: <span class="font-semibold text-neutral-900"
										>{formatearProbabilidad(trastornos.anxiety?.probability)}</span
									>
								</p>
								<p class="text-sm text-neutral-600">
									Confianza: <span class="font-semibold text-neutral-900"
										>{formatearProbabilidad(trastornos.anxiety?.confidence)}</span
									>
								</p>
							</div>
						</div>

						<div class="mt-4 rounded-xl border border-neutral-200 bg-white p-4">
							<h3 class="mb-2 font-semibold text-neutral-900">Interpretación del modelo</h3>
							<p class="text-sm leading-relaxed text-neutral-700">
								{data.respuesta.interpretacion || 'No se registró interpretación adicional.'}
							</p>
						</div>
					</div>
				</div>

				<div class="card">
					<div class="card-body">
						<div class="mb-6 flex flex-col gap-2">
							<h2 class="text-xl font-bold text-neutral-900">Validación clínica</h2>
							<p class="text-sm text-neutral-600">
								Elige si aceptas el diagnóstico sugerido, si lo rechazas o si deseas ajustarlo.
							</p>
							{#if validacionActual}
								<p class="text-xs text-neutral-500">
									Última actualización: {formatearFecha(validacionActual.fecha_validacion)}
								</p>
							{/if}
						</div>

						{#if mensaje}
							<div
								class="mb-5 rounded-lg border p-4 {mensaje.tipo === 'success'
									? 'border-green-200 bg-green-50 text-green-800'
									: 'border-red-200 bg-red-50 text-red-800'}"
							>
								<p class="text-sm font-medium">{mensaje.texto}</p>
							</div>
						{/if}

						<div class="space-y-6">
							<div>
								<label class="mb-3 block text-sm font-semibold text-neutral-700">
									Decisión del especialista
								</label>
								<div class="grid gap-3 md:grid-cols-3">
									<button
										type="button"
										onclick={() => seleccionarDecision('aceptar')}
										class="rounded-xl border px-4 py-4 text-left transition {form.decision ===
										'aceptar'
											? 'border-emerald-500 bg-emerald-50 text-emerald-800'
											: 'border-neutral-200 bg-white text-neutral-700 hover:border-emerald-200'}"
									>
										<p class="font-semibold">Aceptar</p>
										<p class="mt-1 text-sm">Confirmo el diagnóstico sugerido por el modelo.</p>
									</button>

									<button
										type="button"
										onclick={() => seleccionarDecision('modificar')}
										class="rounded-xl border px-4 py-4 text-left transition {form.decision ===
										'modificar'
											? 'border-amber-500 bg-amber-50 text-amber-800'
											: 'border-neutral-200 bg-white text-neutral-700 hover:border-amber-200'}"
									>
										<p class="font-semibold">Modificar</p>
										<p class="mt-1 text-sm">Ajusto parcialmente el diagnóstico sugerido.</p>
									</button>

									<button
										type="button"
										onclick={() => seleccionarDecision('rechazar')}
										class="rounded-xl border px-4 py-4 text-left transition {form.decision ===
										'rechazar'
											? 'border-rose-500 bg-rose-50 text-rose-800'
											: 'border-neutral-200 bg-white text-neutral-700 hover:border-rose-200'}"
									>
										<p class="font-semibold">Rechazar</p>
										<p class="mt-1 text-sm">
											Descarto el diagnóstico actual y registro uno diferente.
										</p>
									</button>
								</div>
							</div>

							<div class="rounded-xl border border-neutral-200 bg-neutral-50 p-5">
								<div class="mb-4 flex items-center justify-between">
									<div>
										<h3 class="font-semibold text-neutral-900">Diagnóstico del especialista</h3>
										<p class="text-sm text-neutral-600">
											Marca las condiciones que consideras presentes.
										</p>
									</div>
									{#if requiereReentrenamiento}
										<span
											class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800"
										>
											Marcará esta validación para reentrenamiento
										</span>
									{/if}
								</div>

								<div class="grid gap-3 md:grid-cols-2">
									<label
										class="flex items-center gap-3 rounded-xl border border-neutral-200 bg-white px-4 py-4"
									>
										<input
											type="checkbox"
											checked={form.diagnosticoEspecialista.depression}
											disabled={form.decision === 'aceptar'}
											onchange={(event) =>
												actualizarDiagnostico('depression', event.currentTarget.checked)}
											class="h-4 w-4 rounded border-neutral-300 text-emerald-600 focus:ring-emerald-500"
										/>
										<div>
											<p class="font-semibold text-neutral-900">Depresión</p>
											<p class="text-sm text-neutral-600">Indicadores clínicos compatibles.</p>
										</div>
									</label>

									<label
										class="flex items-center gap-3 rounded-xl border border-neutral-200 bg-white px-4 py-4"
									>
										<input
											type="checkbox"
											checked={form.diagnosticoEspecialista.anxiety}
											disabled={form.decision === 'aceptar'}
											onchange={(event) =>
												actualizarDiagnostico('anxiety', event.currentTarget.checked)}
											class="h-4 w-4 rounded border-neutral-300 text-emerald-600 focus:ring-emerald-500"
										/>
										<div>
											<p class="font-semibold text-neutral-900">Ansiedad</p>
											<p class="text-sm text-neutral-600">Indicadores clínicos compatibles.</p>
										</div>
									</label>
								</div>
							</div>

							<div class="grid gap-6 md:grid-cols-2">
								<div>
									<label
										for="nivelConfianza"
										class="mb-2 block text-sm font-semibold text-neutral-700"
									>
										Nivel de confianza (0-100)
									</label>
									<input
										id="nivelConfianza"
										type="number"
										min="0"
										max="100"
										class="w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-neutral-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 focus:outline-none"
										value={form.nivelConfianza ?? ''}
										oninput={(event) => (form.nivelConfianza = Number(event.currentTarget.value))}
									/>
								</div>

								<label
									class="flex items-center gap-3 rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-4 text-sm text-neutral-700"
								>
									<input
										type="checkbox"
										checked={form.requiereSeguimiento}
										onchange={(event) => (form.requiereSeguimiento = event.currentTarget.checked)}
										class="h-4 w-4 rounded border-neutral-300 text-emerald-600 focus:ring-emerald-500"
									/>
									El paciente requiere seguimiento adicional
								</label>
							</div>

							<div>
								<label
									for="observaciones"
									class="mb-2 block text-sm font-semibold text-neutral-700"
								>
									Observaciones clínicas
								</label>
								<textarea
									id="observaciones"
									rows="5"
									class="w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-neutral-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 focus:outline-none"
									placeholder="Explica por qué aceptas, rechazas o modificas el diagnóstico sugerido."
									bind:value={form.observaciones}
								></textarea>
							</div>

							<div>
								<label
									for="recomendacionPaciente"
									class="mb-2 block text-sm font-semibold text-neutral-700"
								>
									Recomendación para el paciente
								</label>
								<textarea
									id="recomendacionPaciente"
									rows="4"
									class="w-full rounded-lg border border-neutral-300 bg-white px-4 py-3 text-neutral-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 focus:outline-none"
									placeholder="Indica acciones sugeridas, cuidados o siguientes pasos."
									bind:value={form.recomendacionPaciente}
								></textarea>
							</div>

							<div class="flex justify-end">
								<button
									type="button"
									onclick={guardarValidacion}
									disabled={guardando}
									class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-6 py-3 font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
								>
									{#if guardando}
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
										Guardando...
									{:else}
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M5 13l4 4L19 7"
											/>
										</svg>
										Guardar validación
									{/if}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="space-y-6">
				<div class="card">
					<div class="card-body">
						<h2 class="mb-4 text-lg font-bold text-neutral-900">Resumen rápido</h2>

						<div class="space-y-3 text-sm text-neutral-700">
							<div class="flex items-center justify-between rounded-lg bg-neutral-50 px-4 py-3">
								<span>Estado ML</span>
								<span class="font-semibold capitalize">{data.respuesta.estado_procesamiento}</span>
							</div>
							<div class="flex items-center justify-between rounded-lg bg-neutral-50 px-4 py-3">
								<span>Requiere atención</span>
								<span class="font-semibold">{data.respuesta.requiere_atencion ? 'Sí' : 'No'}</span>
							</div>
							<div class="flex items-center justify-between rounded-lg bg-neutral-50 px-4 py-3">
								<span>Decisión actual</span>
								<span class="font-semibold capitalize">{form.decision}</span>
							</div>
							<div class="flex items-center justify-between rounded-lg bg-neutral-50 px-4 py-3">
								<span>Entrará al reentrenamiento</span>
								<span class="font-semibold">{requiereReentrenamiento ? 'Sí' : 'No'}</span>
							</div>
						</div>
					</div>
				</div>

				{#if esAdmin}
					<div class="card border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-white">
						<div class="card-body">
							<div class="mb-4">
								<h2 class="text-lg font-bold text-neutral-900">Reentrenamiento manual</h2>
								<p class="mt-1 text-sm text-neutral-600">
									Solo admin puede gatillar el entrenamiento usando validaciones rechazadas o
									modificadas.
								</p>
							</div>

							{#if mensajeReentrenamiento}
								<div
									class="mb-4 rounded-lg border p-4 {mensajeReentrenamiento.tipo === 'success'
										? 'border-green-200 bg-green-50 text-green-800'
										: mensajeReentrenamiento.tipo === 'warning'
											? 'border-amber-200 bg-amber-50 text-amber-800'
											: 'border-red-200 bg-red-50 text-red-800'}"
								>
									<p class="text-sm font-medium">{mensajeReentrenamiento.texto}</p>
								</div>
							{/if}

							<div class="space-y-3 text-sm text-neutral-700">
								<div class="flex items-center justify-between rounded-lg bg-white px-4 py-3">
									<span>Validaciones pendientes</span>
									<span class="font-semibold">{retrainingStatus?.pendingCount ?? 0}</span>
								</div>
								<div class="flex items-center justify-between rounded-lg bg-white px-4 py-3">
									<span>Estado</span>
									<span class="font-semibold">
										{retrainingStatus?.isRunning ? 'En ejecución' : 'Disponible'}
									</span>
								</div>
								<div class="flex items-center justify-between rounded-lg bg-white px-4 py-3">
									<span>Última ejecución</span>
									<span class="text-right font-semibold">
										{retrainingStatus?.lastFinishedAt
											? formatearFecha(retrainingStatus.lastFinishedAt)
											: 'Sin registro'}
									</span>
								</div>
							</div>

							<button
								type="button"
								onclick={iniciarReentrenamiento}
								disabled={iniciandoReentrenamiento || retrainingStatus?.isRunning}
								class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
							>
								{#if iniciandoReentrenamiento || retrainingStatus?.isRunning}
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
									{retrainingStatus?.isRunning ? 'Reentrenando...' : 'Iniciando...'}
								{:else}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.868v4.264a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									Gatillar reentrenamiento
								{/if}
							</button>

							{#if retrainingStatus?.logTail}
								<div class="mt-5 rounded-xl bg-neutral-950 p-4 text-xs text-emerald-200">
									<p class="mb-2 font-semibold text-white">Log reciente</p>
									<pre
										class="max-h-72 overflow-auto whitespace-pre-wrap">{retrainingStatus.logTail}</pre>
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
