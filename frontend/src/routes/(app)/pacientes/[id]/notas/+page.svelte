<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props();

	const idPaciente = $page.params.id;

	function formatearFecha(fecha) {
		return new Date(fecha).toLocaleString('es-PE', {
			dateStyle: 'medium',
			timeStyle: 'short',
			timeZone: 'America/Lima'
		});
	}

	function getBadgeEstado(estado) {
		const badges = {
			pendiente: 'bg-yellow-100 text-yellow-800',
			procesado: 'bg-green-100 text-green-800',
			error: 'bg-red-100 text-red-800'
		};
		return badges[estado] || 'bg-gray-100 text-gray-800';
	}

	function getBadgeRiesgo(nivel) {
		const badges = {
			bajo: 'bg-green-100 text-green-800',
			moderado: 'bg-yellow-100 text-yellow-800',
			alto: 'bg-red-100 text-red-800'
		};
		return badges[nivel] || 'bg-gray-100 text-gray-800';
	}

	function tieneSenalesRiesgo(respuesta) {
		const señales = respuesta.trastornos_detectados?.risk_assessment?.señales_detectadas;
		return Array.isArray(señales) && señales.length > 0;
	}
</script>

<svelte:head>
	<title>Notas Diarias - {data.paciente.nombres} {data.paciente.apellidos}</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<button
						onclick={() => goto('/pacientes')}
						class="text-white/80 hover:text-white mb-4 flex items-center gap-2"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
						</svg>
						Volver a Pacientes
					</button>
					<h1 class="text-3xl font-bold text-white flex items-center gap-3">
						<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
						</svg>
						Notas Diarias
					</h1>
					<p class="mt-2 text-white/80">
						Paciente: <span class="font-semibold">{data.paciente.nombres} {data.paciente.apellidos}</span>
						<span class="mx-2">•</span>
						DNI: <span class="font-semibold">{data.paciente.dni}</span>
					</p>
				</div>
				<div class="flex items-center gap-3">
					<a
						href="/pacientes/{idPaciente}/evolucion"
						class="flex items-center gap-2 rounded-lg bg-white/10 px-4 py-3 text-sm font-medium text-white backdrop-blur-sm hover:bg-white/20"
					>
						<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
						</svg>
						Ver Evolución
					</a>
					<div class="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-4 text-center">
						<p class="text-white/80 text-sm">Total de Registros</p>
						<p class="text-3xl font-bold text-white">{data.total}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Tabla de Notas -->
		{#if data.respuestas.length === 0}
			<div class="card">
				<div class="card-body text-center py-12">
					<svg class="mx-auto h-12 w-12 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<p class="text-neutral-600 mb-2 text-lg">No hay notas diarias registradas</p>
					<p class="text-neutral-500 text-sm">El paciente aún no ha completado el cuestionario de notas diarias</p>
				</div>
			</div>
		{:else}
			<div class="card">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-neutral-200">
						<thead class="bg-neutral-50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Fecha y Hora
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Estado
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Nivel de Riesgo
								</th>
								<th class="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Señales de riesgo
								</th>
								<th class="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Riesgo Atendido
								</th>
								<th class="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
									Acciones
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-neutral-200">
							{#each data.respuestas as respuesta}
								<tr class="hover:bg-neutral-50 transition-colors">
									<td class="px-6 py-4 whitespace-nowrap text-sm text-neutral-900">
										{formatearFecha(respuesta.fecha_respuesta)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getBadgeEstado(respuesta.estado_procesamiento)}">
											{respuesta.estado_procesamiento}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										{#if respuesta.nivel_riesgo_global}
											<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getBadgeRiesgo(respuesta.nivel_riesgo_global)}">
												{respuesta.nivel_riesgo_global}
											</span>
										{:else}
											<span class="text-neutral-400 text-sm">-</span>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-center">
										{#if tieneSenalesRiesgo(respuesta)}
											<svg class="w-5 h-5 text-red-600 inline-block" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
											</svg>
										{:else}
											<span class="text-neutral-400 text-sm">-</span>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-center">
										{#if !tieneSenalesRiesgo(respuesta)}
											<span class="text-neutral-400 text-sm">-</span>
										{:else if respuesta.riesgo_atendido}
											<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
												Atendido
											</span>
										{:else}
											<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
												Pendiente
											</span>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-center">
										<button
											onclick={() => goto(`/pacientes/${idPaciente}/notas/${respuesta.id_respuesta}`)}
											class="text-purple-600 hover:text-purple-900 font-medium text-sm flex items-center justify-center gap-1 mx-auto"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
											Ver Detalle
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Paginación (placeholder para futuro) -->
				{#if data.total > data.limite}
					<div class="bg-neutral-50 px-6 py-4 border-t border-neutral-200">
						<p class="text-sm text-neutral-600">
							Mostrando {Math.min(data.limite, data.total)} de {data.total} registros
						</p>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
