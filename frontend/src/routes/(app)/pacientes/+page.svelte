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

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-gray-900">Gestión de Pacientes</h1>
		<p class="mt-2 text-gray-600">Administra la información de los pacientes del centro</p>
	</div>

	<!-- Acciones -->
	<div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
		<!-- Búsqueda -->
		<div class="w-full sm:w-96">
			<input
				type="text"
				placeholder="Buscar por DNI, nombre o correo..."
				bind:value={searchTerm}
				class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
		</div>

		<!-- Botón Nuevo -->
		<button
			on:click={() => goto('/pacientes/nuevo')}
			class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 whitespace-nowrap"
		>
			+ Nuevo Paciente
		</button>
	</div>

	<!-- Contenido -->
	{#if isLoading}
		<div class="flex justify-center items-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
			{error}
		</div>
	{:else if filteredPacientes.length === 0}
		<div class="bg-gray-50 border border-gray-200 rounded-md p-8 text-center">
			<p class="text-gray-600">
				{searchTerm ? 'No se encontraron pacientes con ese criterio de búsqueda' : 'No hay pacientes registrados'}
			</p>
			{#if !searchTerm}
				<button
					on:click={() => goto('/pacientes/nuevo')}
					class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
				>
					Registrar primer paciente
				</button>
			{/if}
		</div>
	{:else}
		<!-- Tabla de pacientes -->
		<div class="bg-white shadow-md rounded-lg overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								DNI
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Nombre Completo
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Edad
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Sexo
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Teléfono
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Correo
							</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
								Acciones
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each filteredPacientes as paciente}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{paciente.dni}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm font-medium text-gray-900">
										{paciente.nombres}
										{paciente.apellidos}
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{calcularEdad(paciente.fecha_nacimiento)} años
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{paciente.sexo === 'M' ? 'Masculino' : 'Femenino'}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{paciente.telefono}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{paciente.correo}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										on:click={() => goto(`/pacientes/${paciente.id_paciente}`)}
										class="text-blue-600 hover:text-blue-900 mr-4"
									>
										Ver
									</button>
									<button
										on:click={() => confirmDelete(paciente)}
										class="text-red-600 hover:text-red-900"
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
			<div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
				<p class="text-sm text-gray-700">
					Mostrando <span class="font-medium">{filteredPacientes.length}</span> de
					<span class="font-medium">{pacientes.length}</span> pacientes
				</p>
			</div>
		</div>
	{/if}
</div>

<!-- Modal de confirmación de eliminación -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
		<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
			<div class="mt-3">
				<h3 class="text-lg font-medium text-gray-900 mb-4">Confirmar Eliminación</h3>
				<p class="text-sm text-gray-500 mb-4">
					¿Está seguro que desea eliminar al paciente <strong
						>{pacienteToDelete?.nombres}
						{pacienteToDelete?.apellidos}</strong
					>?
				</p>
				<p class="text-sm text-gray-500 mb-6">Esta acción desactivará el paciente del sistema.</p>
				<div class="flex gap-4 justify-end">
					<button
						on:click={() => {
							showDeleteModal = false;
							pacienteToDelete = null;
						}}
						class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
					>
						Cancelar
					</button>
					<button
						on:click={deletePaciente}
						class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
					>
						Eliminar
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
