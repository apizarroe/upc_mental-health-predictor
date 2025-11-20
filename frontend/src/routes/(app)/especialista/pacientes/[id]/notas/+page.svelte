<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let { data } = $props();

	const user = data.user;
	const idPaciente = parseInt($page.params.id);

	let paciente = $state(null);
	let notasGrouped = $state([]);
	let loading = $state(true);
	let error = $state('');

	// Función para formatear fecha
	function formatFecha(fecha) {
		const date = new Date(fecha);
		const options = {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			weekday: 'long'
		};
		return date.toLocaleDateString('es-ES', options);
	}

	// Función para formatear hora
	function formatHora(fechaHora) {
		const date = new Date(fechaHora);
		const offsetMinutes = date.getTimezoneOffset();
		const dateLocal = new Date(date.getTime() - offsetMinutes * 60 * 1000);

		return dateLocal.toLocaleTimeString('es-ES', {
			hour: '2-digit',
			minute: '2-digit',
		});
	}

	async function cargarPaciente() {
		try {
			const response = await fetch(`/api/pacientes/${idPaciente}`);
			const result = await response.json();

			if (result.success) {
				paciente = result.data;
			} else {
				error = result.error || 'Error al cargar información del paciente';
			}
		} catch (err) {
			error = 'Error de conexión al servidor';
			console.error('Error:', err);
		}
	}

	async function cargarNotas() {
		try {
			const response = await fetch(`/api/notas/grouped?id_paciente=${idPaciente}`);
			const result = await response.json();

			if (result.success) {
				notasGrouped = result.data;
			} else {
				error = result.error || 'Error al cargar notas';
			}
		} catch (err) {
			error = 'Error de conexión al servidor';
			console.error('Error:', err);
		}
	}

	onMount(async () => {
		loading = true;
		await Promise.all([cargarPaciente(), cargarNotas()]);
		loading = false;
	});
</script>

<svelte:head>
	<title>Notas del Paciente - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-6xl mx-auto p-6">
	<div class="mb-6">
		<button
			onclick={() => goto('/pacientes')}
			class="text-white hover:text-white/80 mb-4 inline-flex items-center"
		>
			← Volver a Pacientes
		</button>

		{#if paciente}
			<div class="bg-white shadow rounded-lg p-6 mb-6">
				<h1 class="text-2xl font-bold text-gray-900 mb-2">
					Notas de {paciente.nombres} {paciente.apellidos}
				</h1>
				<div class="flex gap-4 text-sm text-gray-600">
					<span><strong>DNI:</strong> {paciente.dni}</span>
					<span><strong>Correo:</strong> {paciente.correo}</span>
					<span><strong>Teléfono:</strong> {paciente.telefono}</span>
				</div>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="bg-white shadow rounded-lg p-12 text-center">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			<p class="mt-4 text-gray-600">Cargando notas...</p>
		</div>
	{:else if error}
		<div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm text-red-700">{error}</p>
				</div>
			</div>
		</div>
	{:else if notasGrouped.length === 0}
		<div class="bg-white shadow rounded-lg p-12 text-center">
			<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			</svg>
			<h3 class="mt-2 text-sm font-medium text-gray-900">No hay notas registradas</h3>
			<p class="mt-1 text-sm text-gray-500">
				Este paciente aún no ha registrado ninguna nota.
			</p>
		</div>
	{:else}
		<!-- Información del total de notas -->
		<div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6 rounded-lg">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm text-blue-700">
						Total de registros: <strong>{notasGrouped.reduce((sum, g) => sum + g.notas.length, 0)} nota(s)</strong> en <strong>{notasGrouped.length} día(s)</strong>
					</p>
				</div>
			</div>
		</div>

		<!-- Mostrar notas agrupadas por fecha -->
		<div class="space-y-6">
			{#each notasGrouped as grupo}
				<div class="bg-white shadow rounded-lg overflow-hidden">
					<!-- Header con la fecha -->
					<div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-blue-100">
						<h2 class="text-lg font-semibold text-blue-900">
							{formatFecha(grupo.fecha)}
						</h2>
					</div>

					<!-- Notas del día -->
					<div class="divide-y divide-gray-200">
						{#each grupo.notas as nota}
							<div class="px-6 py-4 hover:bg-gray-50 transition-colors">
								<div class="flex justify-between items-start mb-2">
									<p class="text-sm font-medium text-gray-900">{nota.pregunta}</p>
									<span class="text-xs text-gray-500 ml-4 flex-shrink-0">{formatHora(nota.fecha_registro)}</span>
								</div>
								<p class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{nota.respuesta}</p>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
