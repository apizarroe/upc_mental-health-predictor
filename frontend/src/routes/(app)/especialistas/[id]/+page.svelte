<script>
	import { goto } from '$app/navigation';
	import EspecialistaForm from '$lib/components/forms/EspecialistaForm.svelte';

	let { data } = $props();

	let isLoading = $state(false);
	let error = $state(null);
	let isEditing = $state(false);
	let successMessage = $state(null);

	let especialista = $derived(data.especialista);

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
				<button
					onclick={() => (isEditing = !isEditing)}
					class="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors whitespace-nowrap"
				>
					{isEditing ? 'Cancelar Edición' : 'Editar'}
				</button>
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
