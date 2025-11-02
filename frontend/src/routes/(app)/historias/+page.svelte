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
		return date.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric' });
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

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<div class="flex justify-between items-center">
			<div>
				<h1 class="text-3xl font-bold text-white flex items-center">
					<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					Historias Clínicas
				</h1>
				<p class="mt-2 text-white/80">Gestión de historias clínicas de pacientes</p>
			</div>
			<button
				onclick={() => goto('/historias/nuevo')}
				class="px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 hover:shadow-xl transform hover:-translate-y-0.5"
				style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
			>
				+ Nueva Historia Clínica
			</button>
		</div>
	</div>

	<!-- Search Bar -->
	<div class="bg-white rounded-xl shadow-lg p-6 mb-6">
		<div class="relative">
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Buscar por paciente, DNI, especialista o diagnóstico..."
				class="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
			/>
			<svg class="absolute left-4 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
		</div>
	</div>

	<!-- Error Message -->
	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
			<p class="text-red-800">{error}</p>
		</div>
	{/if}

	<!-- Loading State -->
	{#if isLoading}
		<div class="bg-white rounded-xl shadow-lg p-12 text-center">
			<div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent"></div>
			<p class="mt-4 text-gray-600">Cargando historias clínicas...</p>
		</div>
	{:else if filteredHistorias.length === 0}
		<!-- Empty State -->
		<div class="bg-white rounded-xl shadow-lg p-12 text-center">
			<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			</svg>
			<h3 class="mt-4 text-lg font-medium text-gray-900">No hay historias clínicas</h3>
			<p class="mt-2 text-gray-600">
				{searchTerm ? 'No se encontraron historias con ese criterio de búsqueda.' : 'Comienza creando una nueva historia clínica.'}
			</p>
		</div>
	{:else}
		<!-- Historias List -->
		<div class="bg-white rounded-xl shadow-lg overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Paciente
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Fecha Apertura
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Especialista
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Diagnóstico
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Estado
							</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
								Acciones
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each filteredHistorias as historia}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div>
											<div class="text-sm font-medium text-gray-900">
												{historia.paciente_nombres} {historia.paciente_apellidos}
											</div>
											<div class="text-sm text-gray-500">DNI: {historia.paciente_dni}</div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{formatDate(historia.fecha_apertura)}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">
										{historia.especialista_nombres} {historia.especialista_apellidos}
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="text-sm text-gray-900 line-clamp-2">
										{historia.diagnostico_inicial || 'Sin diagnóstico'}
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {getEstadoBadge(historia.situacion_historia)}">
										{historia.situacion_historia || 'Abierta'}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										onclick={() => goto(`/historias/${historia.id_historia}`)}
										class="text-purple-600 hover:text-purple-900 mr-4"
									>
										Ver detalles
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Summary -->
		<div class="mt-4 text-white text-sm">
			Mostrando {filteredHistorias.length} de {historias.length} historias clínicas
		</div>
	{/if}
</div>
