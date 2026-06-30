<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let historias = $state([]);
	let isLoading = $state(true);
	let error = $state(null);
	let searchTerm = $state('');

	onMount(async () => {
		await loadHistorias();
	});

	async function loadHistorias() {
		try {
			isLoading = true;
			const response = await fetch('/api/historias');
			const result = await response.json();

			if (result.success) {
				historias = result.data;
			} else {
				error = result.error || 'Error al cargar historias clínicas';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	let filteredHistorias = $derived(historias.filter((h) => {
		const search = searchTerm.toLowerCase();
		const pacienteNombre = `${h.paciente_nombres || ''} ${h.paciente_apellidos || ''}`.toLowerCase();
		return (
			h.paciente_dni?.toLowerCase().includes(search) ||
			pacienteNombre.includes(search) ||
			h.especialista_nombres?.toLowerCase().includes(search) ||
			h.especialista_apellidos?.toLowerCase().includes(search) ||
			h.diagnostico_inicial?.toLowerCase().includes(search)
		);
	}));

	function formatDate(dateString) {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);
		return date.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'America/Lima' });
	}

	function getEstadoBadge(situacion) {
		if (situacion === 'Cerrada') {
			return 'bg-gray-100 text-gray-800';
		}
		return 'bg-green-100 text-green-800';
	}
</script>

<svelte:head>
	<title>Historias Clínicas - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header con estadísticas -->
		<div class="mb-8">
			<div class="flex justify-between items-start mb-4">
				<div>
					<h1 class="text-3xl font-bold text-white flex items-center">
						<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						Historias Clínicas
					</h1>
					<p class="mt-2 text-white/80">Gestión de historias clínicas de pacientes</p>
				</div>
				<button onclick={() => goto('/historias/nuevo')} class="btn-primary">
					<svg class="w-5 h-5 inline-block mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					Nueva Historia Clínica
				</button>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-primary-100">
								<svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Total Historias Clínicas</p>
								<p class="text-2xl font-semibold text-neutral-900">{historias.length}</p>
							</div>
						</div>
					</div>
				</div>

				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-secondary-100">
								<svg class="w-6 h-6 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Historias Activas</p>
								<p class="text-2xl font-semibold text-neutral-900">{historias.filter(h => h.situacion_historia !== 'Cerrada').length}</p>
							</div>
						</div>
					</div>
				</div>

				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-accent-100">
								<svg class="w-6 h-6 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Resultados</p>
								<p class="text-2xl font-semibold text-neutral-900">{filteredHistorias.length}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Búsqueda -->
		<div class="card mb-6">
			<div class="card-body">
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</div>
					<input
						type="text"
						bind:value={searchTerm}
						placeholder="Buscar por paciente, DNI, especialista o diagnóstico..."
						class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
					/>
				</div>
			</div>
		</div>

		<!-- Contenido -->
		{#if isLoading}
			<div class="card">
				<div class="card-body flex justify-center items-center py-12">
					<div class="text-center">
						<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
						<p class="text-neutral-600">Cargando historias clínicas...</p>
					</div>
				</div>
			</div>
		{:else if error}
			<div class="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
				<div class="flex items-center">
					<svg class="w-5 h-5 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<p class="text-red-800">{error}</p>
				</div>
			</div>
		{:else if filteredHistorias.length === 0}
			<div class="card">
				<div class="card-body text-center py-12">
					<svg class="mx-auto h-12 w-12 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<p class="text-neutral-600 mb-4">
						{searchTerm ? 'No se encontraron historias clínicas con ese criterio de búsqueda' : 'No hay historias clínicas registradas'}
					</p>
					{#if !searchTerm}
						<button onclick={() => goto('/historias/nuevo')} class="btn-primary">
							Crear primera historia clínica
						</button>
					{/if}
				</div>
			</div>
		{:else}
			<!-- Tabla de historias -->
			<div class="card">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-neutral-200">
						<thead class="bg-neutral-50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Paciente
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Fecha Apertura
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Especialista
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Diagnóstico
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Estado
								</th>
								<th class="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Acciones
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-neutral-200">
							{#each filteredHistorias as historia}
								<tr class="hover:bg-neutral-50 transition-colors">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-neutral-900">
											{historia.paciente_nombres} {historia.paciente_apellidos}
										</div>
										<div class="text-sm text-neutral-500">DNI: {historia.paciente_dni}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{formatDate(historia.fecha_apertura)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{historia.especialista_nombres} {historia.especialista_apellidos}
									</td>
									<td class="px-6 py-4">
										<div class="text-sm text-neutral-900 truncate max-w-xs" title="{historia.diagnostico_inicial || 'Sin diagnóstico'}">
											{historia.diagnostico_inicial || 'Sin diagnóstico'}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getEstadoBadge(historia.situacion_historia)}">
											{historia.situacion_historia || 'Abierta'}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
										<button
											onclick={() => goto(`/historias/${historia.id_historia}`)}
											class="text-primary-600 hover:text-primary-900"
											title="Ver detalles"
										>
											<svg class="w-5 h-5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Footer con contador -->
				<div class="bg-neutral-50 px-6 py-3 border-t border-neutral-200">
					<p class="text-sm text-neutral-700">
						Mostrando <span class="font-medium">{filteredHistorias.length}</span> de
						<span class="font-medium">{historias.length}</span> historias clínicas
					</p>
				</div>
			</div>
		{/if}
	</div>
</div>
