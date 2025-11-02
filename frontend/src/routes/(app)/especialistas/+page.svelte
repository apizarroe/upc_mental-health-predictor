<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let especialistas = $state([]);
	let isLoading = $state(true);
	let error = $state(null);
	let searchTerm = $state('');
	let showDeleteModal = $state(false);
	let especialistaToDelete = $state(null);

	onMount(async () => {
		await loadEspecialistas();
	});

	async function loadEspecialistas() {
		try {
			isLoading = true;
			const response = await fetch('/api/especialistas');
			const result = await response.json();

			if (result.success) {
				especialistas = result.data;
			} else {
				error = result.error || 'Error al cargar especialistas';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	function confirmDelete(especialista) {
		especialistaToDelete = especialista;
		showDeleteModal = true;
	}

	async function deleteEspecialista() {
		if (!especialistaToDelete) return;

		try {
			const response = await fetch(`/api/especialistas/${especialistaToDelete.id_especialista}`, {
				method: 'DELETE'
			});

			const result = await response.json();

			if (result.success) {
				await loadEspecialistas();
				showDeleteModal = false;
				especialistaToDelete = null;
			} else {
				alert('Error al eliminar especialista: ' + result.error);
			}
		} catch (err) {
			alert('Error de conexión al eliminar especialista');
			console.error(err);
		}
	}

	// Primero filtramos solo los activos
	let especialistasActivos = $derived(especialistas.filter(e => e.flg_activo));

	// Luego aplicamos el filtro de búsqueda solo sobre los activos
	let filteredEspecialistas = $derived(especialistasActivos.filter((e) => {
		const search = searchTerm.toLowerCase();
		const nombreCompleto = `${e.nombres || ''} ${e.apellidos || ''}`.toLowerCase();
		return (
			e.dni?.toLowerCase().includes(search) ||
			e.nombres?.toLowerCase().includes(search) ||
			e.apellidos?.toLowerCase().includes(search) ||
			nombreCompleto.includes(search) ||
			e.correo?.toLowerCase().includes(search) ||
			e.especialidad?.toLowerCase().includes(search) ||
			e.colegiatura?.toLowerCase().includes(search)
		);
	}));
</script>

<svelte:head>
	<title>Especialistas - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header con estadísticas -->
		<div class="mb-8">
			<div class="flex justify-between items-start mb-4">
				<div>
					<h1 class="text-3xl font-bold text-white flex items-center">
						<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
						</svg>
						Gestión de Especialistas
					</h1>
					<p class="mt-2 text-white/80">Administra el personal de salud mental del centro</p>
				</div>
				<button onclick={() => goto('/especialistas/nuevo')} class="btn-primary">
					<svg class="w-5 h-5 inline-block mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					Nuevo Especialista
				</button>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-primary-100">
								<svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Total Especialistas</p>
								<p class="text-2xl font-semibold text-neutral-900">{especialistas.length}</p>
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
								<p class="text-sm font-medium text-neutral-600">Especialistas Activos</p>
								<p class="text-2xl font-semibold text-neutral-900">{especialistasActivos.length}</p>
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
								<p class="text-sm font-medium text-neutral-600">Resultados Búsqueda</p>
								<p class="text-2xl font-semibold text-neutral-900">{filteredEspecialistas.length}</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Barra de búsqueda -->
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
							placeholder="Buscar por DNI, nombre, especialidad, colegiatura o correo..."
							class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
						/>
					</div>
				</div>
			</div>
		</div>

		<!-- Contenido principal -->
		{#if isLoading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4">
				<p class="text-red-800">{error}</p>
			</div>
		{:else if filteredEspecialistas.length === 0}
			<div class="card text-center py-12">
				<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
				</svg>
				<h3 class="mt-2 text-sm font-medium text-gray-900">No hay especialistas registrados</h3>
				<p class="mt-1 text-sm text-gray-500">Comienza agregando un nuevo especialista</p>
				<div class="mt-6">
					<button onclick={() => goto('/especialistas/nuevo')} class="btn-primary">
						<svg class="w-5 h-5 inline-block mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Nuevo Especialista
					</button>
				</div>
			</div>
		{:else}
			<div class="card overflow-hidden">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-64">
									Especialista
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Especialidad
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Colegiatura
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Contacto
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
							{#each filteredEspecialistas as especialista}
								<tr class="hover:bg-gray-50 transition-colors">
									<td class="px-6 py-4">
										<div class="flex items-center">
											<div class="flex-shrink-0 h-10 w-10">
												<div class="h-10 w-10 rounded-full flex items-center justify-center text-white font-semibold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
													{especialista.nombres.charAt(0)}{especialista.apellidos.charAt(0)}
												</div>
											</div>
											<div class="ml-4 min-w-0">
												<div class="text-sm font-medium text-gray-900 truncate max-w-xs" title="{especialista.nombres} {especialista.apellidos}">
													{especialista.nombres} {especialista.apellidos}
												</div>
												<div class="text-sm text-gray-500">DNI: {especialista.dni}</div>
											</div>
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">{especialista.especialidad}</div>
										<div class="text-sm text-gray-500">{especialista.cargo}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">{especialista.colegiatura}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm text-gray-900">{especialista.telefono}</div>
										<div class="text-sm text-gray-500">{especialista.correo}</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										{#if especialista.flg_activo}
											<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
												Activo
											</span>
										{:else}
											<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
												Inactivo
											</span>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
										<button
											onclick={() => goto(`/especialistas/${especialista.id_especialista}`)}
											class="text-primary-600 hover:text-primary-900 mr-4"
											title="Ver/Editar"
										>
											<svg class="w-5 h-5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</button>
										<button
											onclick={() => confirmDelete(especialista)}
											class="text-red-600 hover:text-red-900"
											title="Eliminar"
										>
											<svg class="w-5 h-5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
											</svg>
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Modal de confirmación de eliminación -->
{#if showDeleteModal}
	<div class="fixed z-10 inset-0 overflow-y-auto">
		<div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
			<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

			<div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
				<div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
					<div class="sm:flex sm:items-start">
						<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
							<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
							</svg>
						</div>
						<div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
							<h3 class="text-lg leading-6 font-medium text-gray-900">
								Eliminar Especialista
							</h3>
							<div class="mt-2">
								<p class="text-sm text-gray-500">
									¿Está seguro que desea eliminar al especialista
									<strong>{especialistaToDelete?.nombres} {especialistaToDelete?.apellidos}</strong>?
									Esta acción desactivará el especialista en el sistema.
								</p>
							</div>
						</div>
					</div>
				</div>
				<div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
					<button
						type="button"
						onclick={deleteEspecialista}
						class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
					>
						Eliminar
					</button>
					<button
						type="button"
						onclick={() => (showDeleteModal = false)}
						class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
					>
						Cancelar
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
