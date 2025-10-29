<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let pacientes = [];
	let isLoading = true;
	let error = null;
	let searchTerm = '';
	let showDeleteModal = false;
	let pacienteToDelete = null;

	onMount(async () => {
		await loadPacientes();
	});

	async function loadPacientes() {
		try {
			isLoading = true;
			const response = await fetch('/api/pacientes');
			const result = await response.json();

			if (result.success) {
				pacientes = result.data;
			} else {
				error = result.error || 'Error al cargar pacientes';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	function confirmDelete(paciente) {
		pacienteToDelete = paciente;
		showDeleteModal = true;
	}

	async function deletePaciente() {
		if (!pacienteToDelete) return;

		try {
			const response = await fetch(`/api/pacientes/${pacienteToDelete.id_paciente}`, {
				method: 'DELETE'
			});

			const result = await response.json();

			if (result.success) {
				await loadPacientes();
				showDeleteModal = false;
				pacienteToDelete = null;
			} else {
				alert('Error al eliminar paciente: ' + result.error);
			}
		} catch (err) {
			alert('Error de conexión al eliminar paciente');
			console.error(err);
		}
	}

	$: filteredPacientes = pacientes.filter((p) => {
		const search = searchTerm.toLowerCase();
		return (
			p.dni?.toLowerCase().includes(search) ||
			p.nombres?.toLowerCase().includes(search) ||
			p.apellidos?.toLowerCase().includes(search) ||
			p.correo?.toLowerCase().includes(search)
		);
	});

	function calcularEdad(fechaNacimiento) {
		const hoy = new Date();
		const nacimiento = new Date(fechaNacimiento);
		let edad = hoy.getFullYear() - nacimiento.getFullYear();
		const mes = hoy.getMonth() - nacimiento.getMonth();
		if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
			edad--;
		}
		return edad;
	}
</script>

<svelte:head>
	<title>Pacientes - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header con estadísticas -->
		<div class="mb-8">
			<div class="flex justify-between items-start mb-4">
				<div>
					<h1 class="text-3xl font-bold text-neutral-900 flex items-center">
						<svg class="w-8 h-8 text-primary-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						Gestión de Pacientes
					</h1>
					<p class="mt-2 text-neutral-600">Administra la información de los pacientes del centro</p>
				</div>
				<button onclick={() => goto('/pacientes/nuevo')} class="btn-primary">
					<svg class="w-5 h-5 inline-block mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					Nuevo Paciente
				</button>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-primary-100">
								<svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Total Pacientes</p>
								<p class="text-2xl font-semibold text-neutral-900">{pacientes.length}</p>
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
								<p class="text-sm font-medium text-neutral-600">Pacientes Activos</p>
								<p class="text-2xl font-semibold text-neutral-900">{pacientes.filter(p => p.flg_activo).length}</p>
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
								<p class="text-2xl font-semibold text-neutral-900">{filteredPacientes.length}</p>
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
					<svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					<input
						type="text"
						placeholder="Buscar por DNI, nombre o correo..."
						bind:value={searchTerm}
						class="form-input pl-10"
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
						<p class="text-neutral-600">Cargando pacientes...</p>
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
		{:else if filteredPacientes.length === 0}
			<div class="card">
				<div class="card-body text-center py-12">
					<svg class="mx-auto h-12 w-12 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
					<p class="text-neutral-600 mb-4">
						{searchTerm ? 'No se encontraron pacientes con ese criterio de búsqueda' : 'No hay pacientes registrados'}
					</p>
					{#if !searchTerm}
						<button onclick={() => goto('/pacientes/nuevo')} class="btn-primary">
							Registrar primer paciente
						</button>
					{/if}
				</div>
			</div>
		{:else}
			<!-- Tabla de pacientes -->
			<div class="card">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-neutral-200">
						<thead class="bg-neutral-50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									DNI
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Nombre Completo
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Edad
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Sexo
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Teléfono
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Correo
								</th>
								<th class="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Acciones
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-neutral-200">
							{#each filteredPacientes as paciente}
								<tr class="hover:bg-neutral-50 transition-colors">
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900">
										{paciente.dni}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-neutral-900">
											{paciente.nombres} {paciente.apellidos}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{calcularEdad(paciente.fecha_nacimiento)} años
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{paciente.sexo === 'M' ? 'Masculino' : 'Femenino'}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{paciente.telefono}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{paciente.correo}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
										<button
											onclick={() => goto(`/pacientes/${paciente.id_paciente}`)}
											class="text-primary-600 hover:text-primary-900 font-medium"
										>
											Ver
										</button>
										<button
											onclick={() => confirmDelete(paciente)}
											class="text-red-600 hover:text-red-900 font-medium"
										>
											Eliminar
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
						Mostrando <span class="font-medium">{filteredPacientes.length}</span> de
						<span class="font-medium">{pacientes.length}</span> pacientes
					</p>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Modal de confirmación de eliminación -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-neutral-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="relative bg-white rounded-card shadow-soft max-w-md w-full p-6">
			<div class="flex items-center mb-4">
				<div class="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
					<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
				</div>
				<h3 class="ml-4 text-lg font-semibold text-neutral-900">Confirmar Eliminación</h3>
			</div>
			<p class="text-sm text-neutral-600 mb-2">
				¿Está seguro que desea eliminar al paciente <strong class="text-neutral-900">{pacienteToDelete?.nombres} {pacienteToDelete?.apellidos}</strong>?
			</p>
			<p class="text-sm text-neutral-500 mb-6">Esta acción desactivará el paciente del sistema.</p>
			<div class="flex gap-3 justify-end">
				<button
					onclick={() => {
						showDeleteModal = false;
						pacienteToDelete = null;
					}}
					class="btn-outline"
				>
					Cancelar
				</button>
				<button onclick={deletePaciente} class="btn-danger">
					Eliminar
				</button>
			</div>
		</div>
	</div>
{/if}
