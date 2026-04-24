<script>
	const { data } = $props();
	const paciente = $derived(data.paciente);
	const evolucion = $derived(data.evolucion);

	let tabActiva = $state('7d');

	const TABS = [
		{ id: '7d',  label: 'Estado actual',   sub: 'Últimos 7 días'  },
		{ id: '14d', label: 'Estado clínico',  sub: 'Últimos 14 días' },
		{ id: '30d', label: 'Tendencia',        sub: 'Últimos 30 días' }
	];

	// Filtrar datos por ventana de días
	function filtrarDias(datos, dias) {
		const limite = new Date();
		limite.setDate(limite.getDate() - dias);
		return datos.filter((d) => new Date(d.fecha) >= limite);
	}

	const datos7  = $derived(filtrarDias(evolucion, 7));
	const datos14 = $derived(filtrarDias(evolucion, 14));
	const datos30  = $derived(evolucion);

	const datosActivos = $derived(
		tabActiva === '7d' ? datos7 : tabActiva === '14d' ? datos14 : datos30
	);

	// ── SVG chart helpers ──────────────────────────────────────────────────────
	const W = 500, H = 180;
	const PAD = { top: 15, right: 16, bottom: 36, left: 46 };
	const PW = W - PAD.left - PAD.right;
	const PH = H - PAD.top  - PAD.bottom;

	function xPos(i, total) {
		if (total <= 1) return PAD.left + PW / 2;
		return PAD.left + (i / (total - 1)) * PW;
	}

	function yPos(pct) {
		return PAD.top + (1 - pct / 100) * PH;
	}

	function buildPath(datos, campo) {
		if (datos.length === 0) return '';
		return datos
			.map((d, i) => `${i === 0 ? 'M' : 'L'}${xPos(i, datos.length).toFixed(1)},${yPos(d[campo]).toFixed(1)}`)
			.join(' ');
	}

	function formatFecha(str) {
		const d = new Date(str + 'T12:00:00');
		return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`;
	}

	function etiquetasX(datos) {
		const n = datos.length;
		if (n === 0) return [];
		if (n <= 6) return datos.map((d, i) => ({ i, label: formatFecha(d.fecha) }));
		const paso = Math.ceil(n / 6);
		const labels = [];
		for (let i = 0; i < n; i += paso) labels.push({ i, label: formatFecha(datos[i].fecha) });
		if (labels.at(-1).i !== n - 1)
			labels.push({ i: n - 1, label: formatFecha(datos[n - 1].fecha) });
		return labels;
	}

	function resumen(datos) {
		if (datos.length === 0) return null;
		return datos.at(-1);
	}

	const GRIDS = [0, 25, 50, 75, 100];
	const UMBRAL = 38;

	const TESTS = {
		depresion: ['test_depresion1', 'test_depresion2'],
		ansiedad:  ['test_ansiedad1',  'test_ansiedad2']
	};

	const recomendacion = $derived.by(() => {
		if (datos14.length === 0) return null;
		const avgDep = datos14.reduce((s, d) => s + d.prob_depresion, 0) / datos14.length;
		const avgAnx = datos14.reduce((s, d) => s + d.prob_ansiedad,  0) / datos14.length;
		const rDep = Math.round(avgDep);
		const rAnx = Math.round(avgAnx);
		const superaDep = rDep >= UMBRAL;
		const superaAnx = rAnx >= UMBRAL;

		let mostrarDep = false;
		let mostrarAnx = false;

		if (superaDep && superaAnx) {
			if (rDep === rAnx) { mostrarDep = true; mostrarAnx = true; }
			else if (rDep > rAnx) { mostrarDep = true; }
			else { mostrarAnx = true; }
		} else {
			mostrarDep = superaDep;
			mostrarAnx = superaAnx;
		}

		return { mostrarDep, mostrarAnx, avgDep: rDep, avgAnx: rAnx };
	});
</script>

<div class="mx-auto max-w-4xl space-y-6 p-6">

	<!-- Encabezado -->
	<div>
		<a
			href="/pacientes/{paciente.id_paciente}/notas"
			class="mb-4 flex items-center gap-2 text-white/80 hover:text-white"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Volver a Notas
		</a>
		<h1 class="text-3xl font-bold text-white">
			Evolución — {paciente.nombres} {paciente.apellidos}
		</h1>
		<p class="mt-2 text-white/80">
			Probabilidades de depresión y ansiedad detectadas por el modelo ML
		</p>
	</div>

	<!-- Card principal con tabs -->
	<div class="rounded-xl border border-gray-200 bg-white shadow-sm">

		<!-- Tabs -->
		<div class="flex border-b border-gray-200">
			{#each TABS as tab}
				<button
					onclick={() => tabActiva = tab.id}
					class="flex flex-1 flex-col items-center gap-0.5 px-4 py-3 text-sm transition-colors
						{tabActiva === tab.id
							? 'border-b-2 border-purple-600 font-semibold text-purple-700'
							: 'text-gray-500 hover:text-gray-700'}"
				>
					<span>{tab.label}</span>
					<span class="text-xs font-normal opacity-70">{tab.sub}</span>
				</button>
			{/each}
		</div>

		<!-- Contenido del tab activo -->
		<div class="p-5">
			<!-- Leyenda + resumen último punto -->
			<div class="mb-4 flex items-center justify-between">
				<div class="flex gap-5 text-sm">
					<span class="flex items-center gap-2">
						<span class="inline-block h-2.5 w-7 rounded-full bg-rose-500"></span>
						Depresión
					</span>
					<span class="flex items-center gap-2">
						<span class="inline-block h-2.5 w-7 rounded-full bg-teal-500"></span>
						Ansiedad
					</span>
				</div>
				{#if resumen(datosActivos)}
					{@const ult = resumen(datosActivos)}
					<div class="flex gap-4 text-sm">
						<span class="font-medium text-rose-600">Dep. {ult.prob_depresion}%</span>
						<span class="font-medium text-teal-600">Ans. {ult.prob_ansiedad}%</span>
					</div>
				{/if}
			</div>

			<!-- Gráfico -->
			{#if datosActivos.length === 0}
				<div class="flex h-44 items-center justify-center text-sm text-gray-400">
					Sin evaluaciones procesadas en este período
				</div>
			{:else}
				<svg
					viewBox="0 0 {W} {H}"
					class="w-full"
					aria-label="Gráfico de evolución"
				>
					{#each GRIDS as g}
						{@const y = yPos(g)}
						<line x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} stroke="#e5e7eb" stroke-width="1" />
						<text x={PAD.left - 6} y={y + 4} text-anchor="end" font-size="10" fill="#9ca3af">{g}%</text>
					{/each}

					<path d={buildPath(datosActivos, 'prob_depresion')} fill="none" stroke="#f43f5e" stroke-width="2" stroke-linejoin="round" />
					<path d={buildPath(datosActivos, 'prob_ansiedad')}  fill="none" stroke="#14b8a6" stroke-width="2" stroke-linejoin="round" />

					{#each datosActivos as d, i}
						<circle cx={xPos(i, datosActivos.length)} cy={yPos(d.prob_depresion)} r="3" fill="#f43f5e" />
					{/each}
					{#each datosActivos as d, i}
						<circle cx={xPos(i, datosActivos.length)} cy={yPos(d.prob_ansiedad)} r="3" fill="#14b8a6" />
					{/each}

					{#each etiquetasX(datosActivos) as { i, label }}
						<text x={xPos(i, datosActivos.length)} y={H - 6} text-anchor="middle" font-size="10" fill="#6b7280">{label}</text>
					{/each}

					<line x1={PAD.left} y1={yPos(38)} x2={W - PAD.right} y2={yPos(38)} stroke="#fbbf24" stroke-width="1" stroke-dasharray="4 3" />
					<text x={W - PAD.right + 2} y={yPos(38) + 4} font-size="9" fill="#fbbf24">38%</text>
				</svg>
				<p class="mt-1 text-right text-xs text-gray-400">
					Línea amarilla: umbral de detección (≥ 38%)
				</p>
			{/if}
		</div>
	</div>

	<!-- Recomendaciones — solo visibles en tab Estado clínico -->
	{#if tabActiva === '14d' && recomendacion}
		<div class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
			<h2 class="mb-4 font-semibold text-gray-800">Pruebas psicológicas recomendadas</h2>

			{#if !recomendacion.mostrarDep && !recomendacion.mostrarAnx}
				<p class="text-sm text-gray-500">
					Ninguna condición supera el umbral de detección (≥ {UMBRAL}%) en los últimos 14 días.
					No se requieren pruebas adicionales por el momento.
				</p>
			{:else}
				<div class="flex flex-col gap-4 sm:flex-row">
					{#if recomendacion.mostrarDep}
						<div class="flex-1 rounded-lg border border-rose-100 bg-rose-50 p-4">
							<div class="mb-3 flex items-center gap-2">
								<span class="inline-block h-3 w-3 rounded-full bg-rose-500"></span>
								<span class="font-medium text-rose-700">Depresión — {recomendacion.avgDep}%</span>
							</div>
							<ul class="space-y-1">
								{#each TESTS.depresion as test}
									<li class="flex items-center gap-2 text-sm text-rose-800">
										<svg class="h-4 w-4 flex-shrink-0 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
										{test}
									</li>
								{/each}
							</ul>
						</div>
					{/if}
					{#if recomendacion.mostrarAnx}
						<div class="flex-1 rounded-lg border border-teal-100 bg-teal-50 p-4">
							<div class="mb-3 flex items-center gap-2">
								<span class="inline-block h-3 w-3 rounded-full bg-teal-500"></span>
								<span class="font-medium text-teal-700">Ansiedad — {recomendacion.avgAnx}%</span>
							</div>
							<ul class="space-y-1">
								{#each TESTS.ansiedad as test}
									<li class="flex items-center gap-2 text-sm text-teal-800">
										<svg class="h-4 w-4 flex-shrink-0 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
										{test}
									</li>
								{/each}
							</ul>
						</div>
					{/if}
				</div>
			{/if}

			<p class="mt-3 text-xs text-gray-400">
				Basado en el promedio de los últimos 14 días · Umbral de detección: ≥ {UMBRAL}%
			</p>
		</div>
	{/if}

</div>
