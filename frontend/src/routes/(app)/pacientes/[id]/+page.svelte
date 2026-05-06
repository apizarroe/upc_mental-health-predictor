<script>
	import { goto } from '$app/navigation';
	import PacienteForm from '$lib/components/forms/PacienteForm.svelte';

	let { data } = $props();

	let isLoading = $state(false);
	let error = $state(null);
	let isEditing = $state(false);
	let successMessage = $state(null);
	let showStatusModal = $state(false);

	let paciente = $state(data.paciente);

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

	function confirmStatusChange() {
		showStatusModal = true;
	}

	async function togglePacienteStatus() {
		try {
			isLoading = true;
			error = null;
			successMessage = null;

			const nuevoEstado = !paciente.flg_activo;

			const response = await fetch(`/api/pacientes/${paciente.id_paciente}`, {
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
				paciente = result.data;
				showStatusModal = false;
				successMessage = `Paciente ${nuevoEstado ? 'activado' : 'desactivado'} exitosamente`;

				if (!nuevoEstado && result.historiaClinicaCerrada) {
					successMessage += '. La historia clínica ha sido cerrada temporalmente.';
				}

				setTimeout(() => {
					successMessage = null;
				}, 5000);
			} else {
				showStatusModal = false;
				error = result.error || 'Error al cambiar estado del paciente';
			}
		} catch (err) {
			showStatusModal = false;
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
			class="text-white/80 hover:text-white mb-4 flex items-center gap-2"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Volver a Pacientes
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
				<div class="flex gap-2 flex-shrink-0">
					<button
						onclick={() => (isEditing = !isEditing)}
						class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors whitespace-nowrap"
					>
						{isEditing ? 'Cancelar Edición' : 'Editar'}
					</button>
					<button
						onclick={confirmStatusChange}
						class="px-4 py-2 {paciente.flg_activo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-md transition-colors whitespace-nowrap"
					>
						{paciente.flg_activo ? 'Desactivar' : 'Activar'}
					</button>
				</div>
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
						<div>
							<label class="text-sm font-medium text-gray-500">Estado Clínico</label>
							<p class="mt-1 text-gray-900">{paciente.estado_clinico ?? '—'}</p>
						</div>
						<div>
							<label class="text-sm font-medium text-gray-500">Fecha de Última Consulta</label>
							<p class="mt-1 text-gray-900">
								{paciente.fecha_ultima_consulta ? formatDate(paciente.fecha_ultima_consulta) : '—'}
							</p>
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
				<div class="flex-shrink-0 w-12 h-12 rounded-full {paciente.flg_activo ? 'bg-red-100' : 'bg-green-100'} flex items-center justify-center">
					{#if paciente.flg_activo}
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
					{paciente.flg_activo ? 'Desactivar Paciente' : 'Activar Paciente'}
				</h3>
			</div>

			<p class="text-sm text-neutral-600 mb-2">
				¿Está seguro que desea {paciente.flg_activo ? 'desactivar' : 'activar'} al paciente <strong class="text-neutral-900">{paciente.nombres} {paciente.apellidos}</strong>?
			</p>

			{#if paciente.flg_activo}
				<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
					<div class="flex">
						<svg class="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
						<p class="text-sm text-yellow-800">
							<strong>Advertencia:</strong> Si el paciente tiene una Historia Clínica Activa, esta cambiará automáticamente al estado "Cierre Temporal".
						</p>
					</div>
				</div>
			{/if}

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
					onclick={togglePacienteStatus}
					class="px-4 py-2 {paciente.flg_activo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-md transition-colors"
					disabled={isLoading}
				>
					{isLoading ? 'Procesando...' : (paciente.flg_activo ? 'Desactivar' : 'Activar')}
				</button>
			</div>
		</div>
	</div>
{/if}
