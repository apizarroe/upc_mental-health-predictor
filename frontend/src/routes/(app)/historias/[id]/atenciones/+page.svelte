<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props();

	const historia    = $derived(data.historia);
	const currentUserId = data.currentUserId ? parseInt(data.currentUserId) : null;
	const idHistoria  = $page.params.id;

	let atenciones     = $state(data.atenciones ?? []);
	let mostrarFormulario = $state(false);
	let editandoId     = $state(null);
	let guardando      = $state(false);
	let mensaje        = $state(null);

	const TIPOS = ['Presencial', 'Virtual', 'Telefónica'];

	let form = $state({ tipo_atencion: 'Presencial', observaciones: '', recomendaciones: '' });

	function formatFecha(ts) {
		return new Date(ts).toLocaleString('es-PE', {
			dateStyle: 'medium',
			timeStyle: 'short',
			timeZone: 'America/Lima'
		});
	}

	function abrirCrear() {
		editandoId = null;
		form.tipo_atencion   = 'Presencial';
		form.observaciones   = '';
		form.recomendaciones = '';
		mostrarFormulario = true;
		mensaje = null;
	}

	function abrirEditar(atencion) {
		editandoId           = atencion.id_atencion;
		form.tipo_atencion   = atencion.tipo_atencion;
		form.observaciones   = atencion.observaciones   ?? '';
		form.recomendaciones = atencion.recomendaciones ?? '';
		mostrarFormulario    = true;
		mensaje              = null;
	}

	function cancelar() {
		mostrarFormulario = false;
		editandoId = null;
		mensaje = null;
	}

	async function guardar() {
		guardando = true;
		mensaje = null;

		try {
			let response;

			if (editandoId) {
				response = await fetch(`/api/atenciones/${editandoId}`, {
					method: 'PUT',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(form)
				});
			} else {
				response = await fetch(`/api/historias/${idHistoria}/atenciones`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(form)
				});
			}

			const result = await response.json();

			if (result.success) {
				const esEdicion = !!editandoId;
				const res  = await fetch(`/api/historias/${idHistoria}/atenciones`);
				const list = await res.json();
				atenciones = list.data ?? [];
				mostrarFormulario = false;
				editandoId = null;
				mensaje = { tipo: 'success', texto: esEdicion ? 'Atención actualizada.' : 'Atención registrada.' };
			} else {
				mensaje = { tipo: 'error', texto: result.error || 'Error al guardar.' };
			}
		} catch {
			mensaje = { tipo: 'error', texto: 'Error de conexión.' };
		} finally {
			guardando = false;
		}
	}

	function getBadgeTipo(tipo) {
		const map = {
			'Presencial': 'bg-green-100 text-green-800',
			'Virtual':    'bg-blue-100 text-blue-800',
			'Telefónica': 'bg-yellow-100 text-yellow-800'
		};
		return map[tipo] ?? 'bg-gray-100 text-gray-800';
	}
</script>

<svelte:head>
	<title>Registro de Atenciones - {historia.paciente_nombres} {historia.paciente_apellidos}</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

		<!-- Header -->
		<div class="mb-8">
			<button
				onclick={() => goto(`/historias/${idHistoria}`)}
				class="text-white/80 hover:text-white mb-4 flex items-center gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
				Volver a Historia Clínica
			</button>

			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-white flex items-center gap-3">
						<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
						</svg>
						Registro de Atenciones
					</h1>
					<p class="mt-2 text-white/80">
						Paciente: <span class="font-semibold">{historia.paciente_nombres} {historia.paciente_apellidos}</span>
						<span class="mx-2">•</span>
						DNI: <span class="font-semibold">{historia.paciente_dni}</span>
					</p>
				</div>
				{#if !mostrarFormulario}
					<button onclick={abrirCrear} class="btn-primary flex items-center gap-2">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Nueva Atención
					</button>
				{/if}
			</div>
		</div>

		<!-- Mensaje -->
		{#if mensaje}
			<div class="mb-6 rounded-lg border p-4 {mensaje.tipo === 'success' ? 'border-green-200 bg-green-50 text-green-800' : 'border-red-200 bg-red-50 text-red-800'}">
				<p class="text-sm font-medium">{mensaje.texto}</p>
			</div>
		{/if}

		<!-- Formulario crear / editar -->
		{#if mostrarFormulario}
			<div class="card mb-6">
				<div class="card-body">
					<h2 class="text-lg font-semibold text-neutral-800 mb-4">
						{editandoId ? 'Editar Atención' : 'Nueva Atención'}
					</h2>

					<div class="space-y-4">
						<!-- Tipo -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Tipo de Atención <span class="text-red-500">*</span>
							</label>
							<select
								bind:value={form.tipo_atencion}
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								disabled={guardando}
							>
								{#each TIPOS as tipo}
									<option value={tipo}>{tipo}</option>
								{/each}
							</select>
						</div>

						<!-- Observaciones -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
							<textarea
								bind:value={form.observaciones}
								rows="4"
								placeholder="Observaciones de la atención..."
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
								disabled={guardando}
							></textarea>
						</div>

						<!-- Recomendaciones -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">Recomendaciones</label>
							<textarea
								bind:value={form.recomendaciones}
								rows="4"
								placeholder="Recomendaciones para el paciente..."
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
								disabled={guardando}
							></textarea>
						</div>

						<div class="flex justify-end gap-3 pt-2">
							<button
								onclick={cancelar}
								disabled={guardando}
								class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
							>
								Cancelar
							</button>
							<button
								onclick={guardar}
								disabled={guardando}
								class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50"
							>
								{guardando ? 'Guardando...' : editandoId ? 'Guardar cambios' : 'Registrar atención'}
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Lista de atenciones -->
		{#if atenciones.length === 0}
			<div class="card">
				<div class="card-body text-center py-16">
					<svg class="mx-auto h-12 w-12 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
					<p class="text-neutral-600 text-lg mb-1">No hay atenciones registradas</p>
					<p class="text-neutral-500 text-sm">Usa el botón "Nueva Atención" para registrar la primera</p>
				</div>
			</div>
		{:else}
			<div class="space-y-4">
				{#each atenciones.filter(a => a.id_atencion !== editandoId) as atencion (atencion.id_atencion)}
					<div class="card">
						<div class="card-body">
							<!-- Cabecera de la atención -->
							<div class="flex items-center justify-between mb-4 pb-3 border-b border-neutral-100">
								<div class="flex items-center gap-3 flex-wrap">
									<span class="text-sm font-medium text-neutral-700">
										{atencion.especialista_nombres} {atencion.especialista_apellidos}
									</span>
									<span class="text-neutral-300">•</span>
									<span class="text-sm text-neutral-400">{formatFecha(atencion.fecha_atencion)}</span>
								</div>
								<div class="flex items-center gap-3 flex-shrink-0">
									<span class="px-2.5 py-1 text-xs font-semibold rounded-full {getBadgeTipo(atencion.tipo_atencion)}">
										{atencion.tipo_atencion}
									</span>
									{#if parseInt(atencion.id_especialista) === currentUserId}
										<button
											onclick={() => abrirEditar(atencion)}
											class="text-purple-600 hover:text-purple-800 transition-colors"
											title="Editar atención"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</button>
									{/if}
								</div>
							</div>

							<!-- Contenido -->
							<div class="space-y-3">
								<div class="border-l-4 border-neutral-300 pl-3 py-1">
									<p class="text-xs font-semibold text-neutral-400 uppercase tracking-wide mb-1.5">Observaciones</p>
									<p class="text-sm text-neutral-800 whitespace-pre-wrap leading-relaxed">{atencion.observaciones || '—'}</p>
								</div>
								<div class="border-l-4 border-purple-400 pl-3 py-1">
									<p class="text-xs font-semibold text-purple-500 uppercase tracking-wide mb-1.5">Recomendaciones</p>
									<p class="text-sm text-neutral-800 whitespace-pre-wrap leading-relaxed">{atencion.recomendaciones || '—'}</p>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}

	</div>
</div>
