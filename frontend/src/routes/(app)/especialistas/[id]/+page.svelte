<script>
	import { goto } from '$app/navigation';
	import EspecialistaForm from '$lib/components/forms/EspecialistaForm.svelte';

	let { data } = $props();

	let isLoading = $state(false);
	let error = $state(null);
	let isEditing = $state(false);
	let successMessage = $state(null);
	let showStatusModal = $state(false);

	let especialista = $state(data.especialista);

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;
			successMessage = null;

			const response = await fetch(`/api/especialistas/${especialista.id_especialista}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				especialista = result.data;
				isEditing = false;
				successMessage = 'Especialista actualizado exitosamente';
				setTimeout(() => {
					successMessage = null;
				}, 3000);
			} else {
				error = result.error || 'Error al actualizar especialista';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	function confirmStatusChange() {
		showStatusModal = true;
	}

	async function toggleEspecialistaStatus() {
		try {
			isLoading = true;
			error = null;
			successMessage = null;

			const nuevoEstado = !especialista.flg_activo;

			const response = await fetch(`/api/especialistas/${especialista.id_especialista}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					flg_activo: nuevoEstado
				})
			});

			const result = await response.json();

			if (result.success) {
				especialista = result.data;
				showStatusModal = false;
				successMessage = `Especialista ${nuevoEstado ? 'activado' : 'desactivado'} exitosamente`;

				setTimeout(() => {
					successMessage = null;
				}, 5000);
			} else {
				showStatusModal = false;
				error = result.error || 'Error al cambiar estado del especialista';
			}
		} catch (err) {
			showStatusModal = false;
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>{especialista.nombres} {especialista.apellidos} - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Back button -->
	<div class="mb-8">
		<button
			onclick={() => goto('/especialistas')}
			class="text-white hover:text-white/80 mb-4 inline-flex items-center"
		>
			← Volver a la lista
		</button>
	</div>

	<!-- Success message -->
	{#if successMessage}
		<div class="mb-6 bg-green-50 border border-green-200 rounded-md p-4 text-green-800">
			{successMessage}
		</div>
	{/if}

	<!-- Error message -->
	{#if error}
		<div class="mb-6 bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
			{error}
		</div>
	{/if}

	<div class="bg-white shadow-md rounded-lg overflow-hidden">
		<!-- Header dentro de la tarjeta -->
		<div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
			<div class="flex justify-between items-start gap-4">
				<div class="flex-1 min-w-0">
					<h1 class="text-2xl font-bold text-gray-900 break-words">
						{especialista.nombres}
						{especialista.apellidos}
					</h1>
					<p class="mt-1 text-gray-600">Información del especialista</p>
				</div>
				<div class="flex gap-2 flex-shrink-0">
					<button
						onclick={() => (isEditing = !isEditing)}
						class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors whitespace-nowrap"
					>
						{isEditing ? 'Cancelar Edición' : 'Editar'}
					</button>
					<button
						onclick={confirmStatusChange}
						class="px-4 py-2 {especialista.flg_activo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-md transition-colors whitespace-nowrap"
					>
						{especialista.flg_activo ? 'Desactivar' : 'Activar'}
					</button>
				</div>
			</div>
		</div>

		{#if isEditing}
			<!-- Modo Edición -->
			<div class="p-6">
				<EspecialistaForm especialista={especialista} onSubmit={handleSubmit} {isLoading} submitLabel="Guardar Cambios" />
			</div>
		{:else}
			<!-- Modo Vista -->
			<div class="p-6">
				<!-- Información Personal -->
				<div class="mb-8">
					<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">Información Personal</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="text-sm font-medium text-gray-500">DNI</label>
							<p class="mt-1 text-gray-900">{especialista.dni}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Estado</label>
							<p class="mt-1">
								<span
									class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {especialista.flg_activo
										? 'bg-green-100 text-green-800'
										: 'bg-red-100 text-red-800'}"
								>
									{especialista.flg_activo ? 'Activo' : 'Inactivo'}
								</span>
							</p>
						</div>
					</div>
				</div>

				<!-- Información Profesional -->
				<div class="mb-8">
					<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
						Información Profesional
					</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="text-sm font-medium text-gray-500">Especialidad</label>
							<p class="mt-1 text-gray-900">{especialista.especialidad}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Número de Colegiatura</label>
							<p class="mt-1 text-gray-900">{especialista.colegiatura}</p>
						</div>
						<div class="md:col-span-2">
							<label class="text-sm font-medium text-gray-500">Cargo</label>
							<p class="mt-1 text-gray-900">{especialista.cargo}</p>
						</div>
					</div>
				</div>

				<!-- Información de Contacto -->
				<div class="mb-8">
					<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
						Información de Contacto
					</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="text-sm font-medium text-gray-500">Teléfono</label>
							<p class="mt-1 text-gray-900">{especialista.telefono}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Correo Electrónico</label>
							<p class="mt-1 text-gray-900">{especialista.correo}</p>
						</div>
					</div>
				</div>

				<!-- Información del Sistema -->
				<div>
					<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
						Información del Sistema
					</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="text-sm font-medium text-gray-500">ID del Especialista</label>
							<p class="mt-1 text-gray-900">{especialista.id_especialista}</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Modal de confirmación de cambio de estado -->
{#if showStatusModal}
	<div class="fixed inset-0 bg-neutral-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
		<div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
			<div class="flex items-center mb-4">
				<div class="flex-shrink-0 w-12 h-12 rounded-full {especialista.flg_activo ? 'bg-red-100' : 'bg-green-100'} flex items-center justify-center">
					{#if especialista.flg_activo}
						<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					{:else}
						<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{/if}
				</div>
				<h3 class="ml-4 text-lg font-semibold text-neutral-900">
					{especialista.flg_activo ? 'Desactivar Especialista' : 'Activar Especialista'}
				</h3>
			</div>

			<p class="text-sm text-neutral-600 mb-4">
				¿Está seguro que desea {especialista.flg_activo ? 'desactivar' : 'activar'} al especialista <strong class="text-neutral-900">{especialista.nombres} {especialista.apellidos}</strong>?
			</p>

			<div class="flex gap-3 justify-end">
				<button
					onclick={() => {
						showStatusModal = false;
					}}
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
					disabled={isLoading}
				>
					Cancelar
				</button>
				<button
					onclick={toggleEspecialistaStatus}
					class="px-4 py-2 {especialista.flg_activo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-md transition-colors"
					disabled={isLoading}
				>
					{isLoading ? 'Procesando...' : (especialista.flg_activo ? 'Desactivar' : 'Activar')}
				</button>
			</div>
		</div>
	</div>
{/if}
