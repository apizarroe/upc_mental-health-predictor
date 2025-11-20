<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let { data } = $props();

	const user = data.user;

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

	async function cargarNotas() {
		loading = true;
		error = '';

		try {
			const response = await fetch(`/api/notas/grouped?id_paciente=${user.user_id}`);
			const result = await response.json();

			if (result.success) {
				notasGrouped = result.data;
			} else {
				error = result.error || 'Error al cargar notas';
			}
		} catch (err) {
			error = 'Error de conexión al servidor';
			console.error('Error:', err);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		cargarNotas();
	});
</script>

<div class="max-w-6xl mx-auto p-6">
	<div class="flex justify-between items-center mb-6">
		<h1 class="text-white text-3xl font-bold">Historial de Notas</h1>
		<a
			href="/paciente/notas"
			class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
		>
			<svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Nueva Nota
		</a>
	</div>

	{#if loading}
		<div class="bg-white shadow rounded-lg p-12 text-center">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			<p class="mt-4 text-gray-600">Cargando notas...</p>
		</div>
	{:else if error}
		<div class="bg-red-50 border-l-4 border-red-400 p-4">
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
			<p class="mt-1 text-sm text-gray-500">Comienza registrando tu primera nota diaria.</p>
			<div class="mt-6">
				<a
					href="/paciente/notas"
					class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
				>
					<svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					Crear Primera Nota
				</a>
			</div>
		</div>
	{:else}
		<!-- Mostrar notas agrupadas por fecha -->
		<div class="space-y-6">
			{#each notasGrouped as grupo}
				<div class="bg-white shadow rounded-lg overflow-hidden">
					<!-- Header con la fecha -->
					<div class="bg-blue-50 px-6 py-4 border-b border-blue-100">
						<h2 class="text-lg font-semibold text-blue-900">
							{formatFecha(grupo.fecha)}
						</h2>
					</div>

					<!-- Notas del día -->
					<div class="divide-y divide-gray-200">
						{#each grupo.notas as nota}
							<div class="px-6 py-4">
								<div class="flex justify-between items-start mb-2">
									<p class="text-sm font-medium text-gray-900">{nota.pregunta}</p>
									<span class="text-xs text-gray-500">{formatHora(nota.fecha_registro)}</span>
								</div>
								<p class="text-sm text-gray-700 whitespace-pre-wrap">{nota.respuesta}</p>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
