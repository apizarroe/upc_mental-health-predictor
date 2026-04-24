<script>
	const { data } = $props();
	const paciente = $derived(data.paciente);
	const evolucion = $derived(data.evolucion);

	// Filtrar datos por ventana de días
	function filtrarDias(datos, dias) {
		const limite = new Date();
		limite.setDate(limite.getDate() - dias);
		return datos.filter((d) => new Date(d.fecha) >= limite);
	}

	const datos7  = $derived(filtrarDias(evolucion, 7));
	const datos14 = $derived(filtrarDias(evolucion, 14));
	const datos30  = $derived(evolucion);

	// ── SVG chart helpers ──────────────────────────────────────────────────────
	const W = 500, H = 180;
	const PAD = { top: 15, right: 16, bottom: 36, left: 46 };
	const PW = W - PAD.left - PAD.right; // 438
	const PH = H - PAD.top  - PAD.bottom; // 129

	function xPos(i, total) {
		if (total <= 1) return PAD.left + PW / 2;
		return PAD.left + (i / (total - 1)) * PW;
	}

	function yPos(pct) {
		// pct: 0-100
		return PAD.top + (1 - pct / 100) * PH;
	}

	function buildPath(datos, campo) {
		if (datos.length === 0) return '';
		return datos
			.map((d, i) => `${i === 0 ? 'M' : 'L'}${xPos(i, datos.length).toFixed(1)},${yPos(d[campo]).toFixed(1)}`)
			.join(' ');
	}

	function formatFecha(str) {
		const d = new Date(str + 'T12:00:00'); // evitar offset de zona horaria
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

	// Resumen del último punto disponible en el período
	function resumen(datos) {
		if (datos.length === 0) return null;
		return datos.at(-1);
	}

	const GRIDS = [0, 25, 50, 75, 100];
</script>

<div class="mx-auto max-w-4xl space-y-8 p-6">

	<!-- Encabezado -->
	<div class="flex items-center justify-between">
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
	</div>

	<!-- Leyenda global -->
	<div class="flex gap-6 text-sm">
		<span class="flex items-center gap-2">
			<span class="inline-block h-3 w-8 rounded-full bg-rose-500"></span>
			Depresión
		</span>
		<span class="flex items-center gap-2">
			<span class="inline-block h-3 w-8 rounded-full bg-indigo-500"></span>
			Ansiedad
		</span>
	</div>

	<!-- ── GRÁFICO 1: Estado actual (7 días) ────────────────────────────────── -->
	{#snippet grafico(datos, titulo)}
		{@const ult = resumen(datos)}
		<div class="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
			<div class="mb-4 flex items-start justify-between">
				<h2 class="font-semibold text-gray-800">{titulo}</h2>
				{#if ult}
					<div class="flex gap-4 text-sm">
						<span class="font-medium text-rose-600">Dep. {ult.prob_depresion}%</span>
						<span class="font-medium text-indigo-600">Ans. {ult.prob_ansiedad}%</span>
					</div>
				{/if}
			</div>

			{#if datos.length === 0}
				<div class="flex h-36 items-center justify-center text-sm text-gray-400">
					Sin evaluaciones procesadas en este período
				</div>
			{:else}
				<svg
					viewBox="0 0 {W} {H}"
					class="w-full"
					aria-label="Gráfico de evolución {titulo}"
				>
					<!-- Grid horizontal -->
					{#each GRIDS as g}
						{@const y = yPos(g)}
						<line
							x1={PAD.left} y1={y}
							x2={W - PAD.right} y2={y}
							stroke="#e5e7eb" stroke-width="1"
						/>
						<text x={PAD.left - 6} y={y + 4} text-anchor="end" font-size="10" fill="#9ca3af">
							{g}%
						</text>
					{/each}

					<!-- Línea depresión -->
					<path
						d={buildPath(datos, 'prob_depresion')}
						fill="none" stroke="#f43f5e" stroke-width="2" stroke-linejoin="round"
					/>
					<!-- Línea ansiedad -->
					<path
						d={buildPath(datos, 'prob_ansiedad')}
						fill="none" stroke="#6366f1" stroke-width="2" stroke-linejoin="round"
					/>

					<!-- Puntos depresión -->
					{#each datos as d, i}
						<circle
							cx={xPos(i, datos.length)} cy={yPos(d.prob_depresion)}
							r="3" fill="#f43f5e"
						/>
					{/each}
					<!-- Puntos ansiedad -->
					{#each datos as d, i}
						<circle
							cx={xPos(i, datos.length)} cy={yPos(d.prob_ansiedad)}
							r="3" fill="#6366f1"
						/>
					{/each}

					<!-- Etiquetas eje X -->
					{#each etiquetasX(datos) as { i, label }}
						<text
							x={xPos(i, datos.length)} y={H - 6}
							text-anchor="middle" font-size="10" fill="#6b7280"
						>
							{label}
						</text>
					{/each}

					<!-- Umbral de detección (38%) -->
					<line
						x1={PAD.left} y1={yPos(38)}
						x2={W - PAD.right} y2={yPos(38)}
						stroke="#fbbf24" stroke-width="1" stroke-dasharray="4 3"
					/>
					<text x={W - PAD.right + 2} y={yPos(38) + 4} font-size="9" fill="#fbbf24">38%</text>
				</svg>
				<p class="mt-1 text-right text-xs text-gray-400">
					Línea amarilla: umbral de detección (≥ 38%)
				</p>
			{/if}
		</div>
	{/snippet}

	{@render grafico(datos7,  'Estado actual — últimos 7 días')}
	{@render grafico(datos14, 'Estado clínico — últimos 14 días')}
	{@render grafico(datos30, 'Tendencia — últimos 30 días')}

</div>
