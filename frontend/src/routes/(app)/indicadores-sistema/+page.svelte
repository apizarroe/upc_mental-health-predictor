<script>
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';

	let reportes = $state([]);
	let isLoading = $state(true);
	let isGenerating = $state(false);
	let error = $state('');
	let successMessage = $state('');

	function isoADisplay(isoDate) {
		if (!isoDate) return '';
		const [y, m, d] = isoDate.split('-');
		return `${d}/${m}/${y}`;
	}

	function displayAIso(displayDate) {
		if (!displayDate || displayDate.length !== 10) return '';
		const [d, m, y] = displayDate.split('/');
		if (!d || !m || !y || y.length !== 4) return '';
		return `${y}-${m}-${d}`;
	}

	function formatearFechaInput(fecha) {
		const year = fecha.getFullYear();
		const month = String(fecha.getMonth() + 1).padStart(2, '0');
		const day = String(fecha.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	function getDefaultRange() {
		const ahora = Date.now();
		const hace30Dias = ahora - 30 * 24 * 60 * 60 * 1000;

		return {
			fechaInicio: formatearFechaInput(new Date(hace30Dias)),
			fechaFin: formatearFechaInput(new Date(ahora))
		};
	}

	const defaultRange = getDefaultRange();

	let fechaInicio = $state(defaultRange.fechaInicio);
	let fechaFin = $state(defaultRange.fechaFin);

	let fechaInicioDisplay = $state(isoADisplay(defaultRange.fechaInicio));
	let fechaFinDisplay = $state(isoADisplay(defaultRange.fechaFin));

	function onFechaInicioInput(e) {
		fechaInicioDisplay = e.currentTarget.value;
		const iso = displayAIso(fechaInicioDisplay);
		if (iso) fechaInicio = iso;
	}

	function onFechaFinInput(e) {
		fechaFinDisplay = e.currentTarget.value;
		const iso = displayAIso(fechaFinDisplay);
		if (iso) fechaFin = iso;
	}

	onMount(async () => {
		await cargarReportes();
	});

	async function cargarReportes() {
		try {
			isLoading = true;
			error = '';

			const response = await fetch('/api/indicadores-sistema');
			const result = await response.json();

			if (!result.success) {
				error = result.error || 'No se pudieron cargar los reportes.';
				return;
			}

			reportes = result.data || [];
		} catch (err) {
			console.error(err);
			error = 'Error de conexión al cargar reportes.';
		} finally {
			isLoading = false;
		}
	}

	async function generarReporte() {
		try {
			isGenerating = true;
			error = '';
			successMessage = '';

			const response = await fetch('/api/indicadores-sistema', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					fecha_inicio: fechaInicio,
					fecha_fin: fechaFin
				})
			});

			const result = await response.json();

			if (!result.success) {
				error = result.error || 'No se pudo generar el reporte.';
				return;
			}

			successMessage = result.message || 'Reporte generado correctamente.';
			await cargarReportes();
		} catch (err) {
			console.error(err);
			error = 'Error de conexión al generar el reporte.';
		} finally {
			isGenerating = false;
		}
	}

	function formatearFechaHora(valor) {
		if (!valor) return 'N/A';
		return new Date(valor).toLocaleString('es-PE', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			timeZone: 'America/Lima'
		});
	}

	function formatearFecha(valor) {
		if (!valor) return 'N/A';
		return new Date(valor).toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			timeZone: 'America/Lima'
		});
	}

	function getTotales(reporte) {
		return reporte.indicadores_json?.totales ?? {};
	}

	function getPruebas(reporte) {
		return reporte.indicadores_json?.pruebas_psicologicas_recomendadas ?? {};
	}
</script>

<svelte:head>
	<title>Indicadores del Sistema - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<div class="mb-8">
			<h1 class="flex items-center text-3xl font-bold text-white">
				<svg class="mr-3 h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 17v-6m4 6V7m4 10v-3M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z"
					/>
				</svg>
				Indicadores del Sistema
			</h1>
			<p class="mt-2 text-white/80">
				Genera y consulta reportes históricos de uso y validación del sistema.
			</p>
		</div>

		<div class="card mb-6">
			<div class="card-header">
				<h2 class="text-lg font-semibold text-neutral-900">Generar nuevo reporte</h2>
				<p class="mt-1 text-sm text-neutral-600">
					Selecciona un rango de fechas de hasta 4 meses para generar un snapshot exportable.
				</p>
			</div>
			<div class="card-body">
				<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
					<div>
						<label for="fecha_inicio" class="mb-2 block text-sm font-medium text-neutral-700">
							Fecha inicio
						</label>
						<div class="relative">
							<input id="fecha_inicio" type="text" placeholder="dd/mm/yyyy" maxlength="10"
								value={fechaInicioDisplay} oninput={onFechaInicioInput} class="form-input pr-10" />
							<input type="date" class="absolute inset-0 opacity-0 w-full cursor-pointer"
								value={fechaInicio}
								onchange={(e) => { fechaInicio = e.currentTarget.value; fechaInicioDisplay = isoADisplay(e.currentTarget.value); }} />
							<span class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-neutral-400">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							</span>
						</div>
					</div>
					<div>
						<label for="fecha_fin" class="mb-2 block text-sm font-medium text-neutral-700">
							Fecha fin
						</label>
						<div class="relative">
							<input id="fecha_fin" type="text" placeholder="dd/mm/yyyy" maxlength="10"
								value={fechaFinDisplay} oninput={onFechaFinInput} class="form-input pr-10" />
							<input type="date" class="absolute inset-0 opacity-0 w-full cursor-pointer"
								value={fechaFin}
								onchange={(e) => { fechaFin = e.currentTarget.value; fechaFinDisplay = isoADisplay(e.currentTarget.value); }} />
							<span class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-neutral-400">
								<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							</span>
						</div>
					</div>
					<div class="flex items-end md:col-span-2">
						<button
							class="btn-primary w-full md:w-auto"
							onclick={generarReporte}
							disabled={isGenerating}
						>
							{isGenerating ? 'Generando reporte...' : 'Generar reporte'}
						</button>
					</div>
				</div>

				{#if error}
					<div
						class="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
					>
						{error}
					</div>
				{/if}

				{#if successMessage}
					<div
						class="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
					>
						{successMessage}
					</div>
				{/if}
			</div>
		</div>

		<div class="card">
			<div class="card-header">
				<h2 class="text-lg font-semibold text-neutral-900">Reportes generados</h2>
				<p class="mt-1 text-sm text-neutral-600">
					Historial compartido entre administradores, ordenado por fecha de generación.
				</p>
			</div>

			{#if isLoading}
				<div class="card-body flex items-center justify-center py-12">
					<div class="text-center">
						<div
							class="border-primary-600 mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2"
						></div>
						<p class="text-neutral-600">Cargando reportes...</p>
					</div>
				</div>
			{:else if reportes.length === 0}
				<div class="card-body py-12 text-center">
					<p class="text-neutral-600">Todavía no se han generado reportes de indicadores.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-neutral-200">
						<thead class="bg-neutral-50">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-500 uppercase"
								>
									Generación
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-500 uppercase"
								>
									Solicitante
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-500 uppercase"
								>
									Rango
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-500 uppercase"
								>
									Resumen
								</th>
								<th
									class="px-6 py-3 text-right text-xs font-medium tracking-wider text-neutral-500 uppercase"
								>
									Acciones
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-neutral-200 bg-white">
							{#each reportes as reporte (reporte.id_reporte)}
								{@const totales = getTotales(reporte)}
								{@const pruebas = getPruebas(reporte)}
								<tr class="transition-colors hover:bg-neutral-50">
									<td class="px-6 py-4 text-sm whitespace-nowrap text-neutral-700">
										{formatearFechaHora(reporte.fecha_generacion)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="text-sm font-medium text-neutral-900">
											{reporte.solicitante_nombre}
										</div>
										<div class="text-xs text-neutral-500 uppercase">
											{reporte.formato_exportacion}
										</div>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-neutral-700">
										{formatearFecha(reporte.fecha_inicio)} - {formatearFecha(reporte.fecha_fin)}
									</td>
									<td class="px-6 py-4 text-sm text-neutral-700">
										<div class="grid grid-cols-1 gap-1 lg:grid-cols-2">
											<div>
												Pacientes: <span class="font-semibold"
													>{totales.pacientes_atendidos ?? 0}</span
												>
											</div>
											<div>
												Notas: <span class="font-semibold">{totales.notas_analizadas ?? 0}</span>
											</div>
											<div>
												Diag. sugeridos: <span class="font-semibold"
													>{totales.diagnosticos_sugeridos ?? 0}</span
												>
											</div>
											<div>
												Diag. aceptados: <span class="font-semibold"
													>{totales.diagnosticos_aceptados ?? 0}</span
												>
											</div>
											<div class="lg:col-span-2">
												Pruebas recomendadas:
												<span class="font-semibold">{pruebas.total_recomendaciones ?? 0}</span>
											</div>
										</div>
									</td>
									<td class="px-6 py-4 text-right">
										<a
											href={resolve(`/api/indicadores-sistema/${reporte.id_reporte}/export`)}
											class="btn-outline inline-flex items-center justify-center px-4 py-2 text-sm"
										>
											Exportar
										</a>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
</div>
