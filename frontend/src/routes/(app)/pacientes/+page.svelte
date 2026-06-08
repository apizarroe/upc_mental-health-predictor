<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { canCreatePacientes, canUpdatePacientes, canDeletePacientes } from '$lib/utils/permissions.js';

	let { data } = $props();

	let pacientes = $state([]);
	let pacientesConHistoria = $state([]);
	let isLoading = $state(true);
	let error = $state(null);
	let searchTerm = $state('');

	// Permisos del usuario actual
	const userRole = data.user.rol;
	const canCreate = canCreatePacientes(userRole);
	const canUpdate = canUpdatePacientes(userRole);

	// Función para verificar si un paciente tiene historia clínica
	function tieneHistoriaClinica(idPaciente) {
		return pacientesConHistoria.includes(idPaciente);
	}

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
				pacientesConHistoria = result.pacientesConHistoria || [];
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

	// Conteo de pacientes activos para métricas
	let pacientesActivos = $derived(pacientes.filter(p => p.flg_activo));

	// Filtrado base según el rol del usuario
	// - Admin: ve todos los pacientes (activos e inactivos)
	// - Especialista: solo ve pacientes activos
	let pacientesBase = $derived(
		userRole === 'admin'
			? pacientes
			: pacientes.filter(p => p.flg_activo)
	);

	// Aplicamos el filtro de búsqueda sobre los pacientes base
	let filteredPacientes = $derived(pacientesBase.filter((p) => {
		const search = searchTerm.toLowerCase();
		const nombreCompleto = `${p.nombres || ''} ${p.apellidos || ''}`.toLowerCase();
		return (
			p.dni?.toLowerCase().includes(search) ||
			p.nombres?.toLowerCase().includes(search) ||
			p.apellidos?.toLowerCase().includes(search) ||
			nombreCompleto.includes(search) ||
			p.correo?.toLowerCase().includes(search)
		);
	}));

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
					<h1 class="text-3xl font-bold text-white flex items-center">
						<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						Gestión de Pacientes
					</h1>
					<p class="mt-2 text-white/80">Administra la información de los pacientes del centro</p>
				</div>
				{#if canCreate}
					<button onclick={() => goto('/pacientes/nuevo')} class="btn-primary">
						<svg class="w-5 h-5 inline-block mr-2 -ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Nuevo Paciente
					</button>
				{/if}
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-{userRole === 'admin' ? '3' : '2'} gap-4 mb-6">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="p-3 rounded-lg bg-primary-100">
								<svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">
									{userRole === 'admin' ? 'Total Pacientes' : 'Pacientes Activos'}
								</p>
								<p class="text-2xl font-semibold text-neutral-900">
									{userRole === 'admin' ? pacientes.length : pacientesActivos.length}
								</p>
							</div>
						</div>
					</div>
				</div>

				{#if userRole === 'admin'}
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
									<p class="text-2xl font-semibold text-neutral-900">{pacientesActivos.length}</p>
								</div>
							</div>
						</div>
					</div>
				{/if}

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
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</div>
					<input
						type="text"
						bind:value={searchTerm}
						placeholder="Buscar por DNI, nombre o correo..."
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
					{#if !searchTerm && canCreate}
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
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider w-64">
									Nombre Completo
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Edad
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Sexo
								</th>
								{#if userRole === 'admin'}
									<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
										Teléfono
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
										Correo
									</th>
								{/if}
								{#if userRole === 'admin'}
									<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
										Estado
									</th>
								{/if}
								{#if userRole !== 'admin'}
									<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
										Estado Clínico
									</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
										Última Consulta
									</th>
								{/if}
								<th class="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Notas
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
									<td class="px-6 py-4">
										<div class="text-sm font-medium text-neutral-900 truncate max-w-xs" title="{paciente.nombres} {paciente.apellidos}">
											{paciente.nombres} {paciente.apellidos}
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{calcularEdad(paciente.fecha_nacimiento)} años
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
										{paciente.sexo === 'M' ? 'Masculino' : 'Femenino'}
									</td>
									{#if userRole === 'admin'}
										<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
											{paciente.telefono}
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
											{paciente.correo}
										</td>
									{/if}
									{#if userRole === 'admin'}
										<td class="px-6 py-4 whitespace-nowrap">
											{#if paciente.flg_activo}
												<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
													Activo
												</span>
											{:else}
												<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
													Inactivo
												</span>
											{/if}
										</td>
									{/if}
									{#if userRole !== 'admin'}
										<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
											{paciente.estado_clinico ?? '—'}
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
											{paciente.fecha_ultima_consulta ? new Date(paciente.fecha_ultima_consulta).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : ''}
										</td>
									{/if}
									<td class="px-6 py-4 whitespace-nowrap text-center">
										{#if tieneHistoriaClinica(paciente.id_paciente)}
											<button
												onclick={() => goto(`/pacientes/${paciente.id_paciente}/notas`)}
												class="text-purple-600 hover:text-purple-900 transition-colors"
												title="Ver notas diarias"
											>
												<svg class="w-6 h-6 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
												</svg>
											</button>
										{:else}
											<button
												disabled
												class="text-gray-300 cursor-not-allowed"
												title="El paciente no tiene historia clínica"
											>
												<svg class="w-6 h-6 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
												</svg>
											</button>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
										{#if canUpdate}
											<!-- Botón de editar para admins -->
											<button
												onclick={() => goto(`/pacientes/${paciente.id_paciente}`)}
												class="text-primary-600 hover:text-primary-900"
												title="Editar"
											>
												<svg class="w-5 h-5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</button>
										{:else}
											<!-- Botón de ver para especialistas (solo lectura) -->
											<button
												onclick={() => goto(`/pacientes/${paciente.id_paciente}/ver`)}
												class="text-blue-600 hover:text-blue-900"
												title="Ver detalles"
											>
												<svg class="w-5 h-5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
												</svg>
											</button>
										{/if}
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
