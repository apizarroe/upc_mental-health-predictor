<script>
	import { goto } from '$app/navigation';
	import PacienteForm from '$lib/components/forms/PacienteForm.svelte';

	let { data } = $props();

	let isLoading = $state(false);
	let error = $state(null);
	let isEditing = $state(false);
	let successMessage = $state(null);

	let paciente = $derived(data.paciente);

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;
			successMessage = null;

			const response = await fetch(`/api/pacientes/${paciente.id_paciente}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				paciente = result.data;
				isEditing = false;
				successMessage = 'Paciente actualizado exitosamente';
				setTimeout(() => {
					successMessage = null;
				}, 3000);
			} else {
				error = result.error || 'Error al actualizar paciente';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	function formatDate(dateString) {
		const date = new Date(dateString);
		return date.toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

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
	<title>{paciente.nombres} {paciente.apellidos} - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Back button -->
	<div class="mb-8">
		<button
			onclick={() => goto('/pacientes')}
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
						{paciente.nombres}
						{paciente.apellidos}
					</h1>
					<p class="mt-1 text-gray-600">Información del paciente</p>
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
				<PacienteForm patient={paciente} onSubmit={handleSubmit} {isLoading} submitLabel="Guardar Cambios" />
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
							<p class="mt-1 text-gray-900">{paciente.dni}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Fecha de Nacimiento</label>
							<p class="mt-1 text-gray-900">
								{formatDate(paciente.fecha_nacimiento)}
								<span class="text-gray-500">({calcularEdad(paciente.fecha_nacimiento)} años)</span>
							</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Sexo</label>
							<p class="mt-1 text-gray-900">{paciente.sexo === 'M' ? 'Masculino' : 'Femenino'}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Estado</label>
							<p class="mt-1">
								<span
									class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {paciente.flg_activo
										? 'bg-green-100 text-green-800'
										: 'bg-red-100 text-red-800'}"
								>
									{paciente.flg_activo ? 'Activo' : 'Inactivo'}
								</span>
							</p>
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
							<label class="text-sm font-medium text-gray-500">Dirección</label>
							<p class="mt-1 text-gray-900">{paciente.direccion}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Teléfono</label>
							<p class="mt-1 text-gray-900">{paciente.telefono}</p>
						</div>
						<div class="md:col-span-2">
							<label class="text-sm font-medium text-gray-500">Correo Electrónico</label>
							<p class="mt-1 text-gray-900">{paciente.correo}</p>
						</div>
					</div>
				</div>

				<!-- Contacto de Emergencia -->
				<div class="mb-8">
					<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
						Contacto de Emergencia
					</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="text-sm font-medium text-gray-500">Nombre</label>
							<p class="mt-1 text-gray-900">{paciente.contacto_emergencia}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Teléfono</label>
							<p class="mt-1 text-gray-900">{paciente.telefono_emergencia}</p>
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
							<label class="text-sm font-medium text-gray-500">ID del Paciente</label>
							<p class="mt-1 text-gray-900">{paciente.id_paciente}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Fecha de Registro</label>
							<p class="mt-1 text-gray-900">{formatDate(paciente.fecha_registro)}</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
