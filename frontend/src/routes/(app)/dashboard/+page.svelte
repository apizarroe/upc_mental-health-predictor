<script>
	let { data } = $props();

	const badgeTipoAtencion = {
		Presencial: 'bg-green-100 text-green-800',
		Virtual: 'bg-blue-100 text-blue-800',
		Telefónica: 'bg-orange-100 text-orange-800'
	};

	function formatFechaHora(fecha) {
		return new Date(fecha).toLocaleString('es-PE', {
			timeZone: 'America/Lima',
			day: '2-digit',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Dashboard - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-white flex items-center">
				<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
				</svg>
				Dashboard
			</h1>
			<p class="mt-2 text-white/80">Vista general del sistema</p>
		</div>

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
			<!-- Pacientes Activos -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Pacientes Activos</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{data.pacientesActivos}</p>
					</div>
					<div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
						<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
						</svg>
					</div>
				</div>
			</div>

			<!-- Sesiones Hoy -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Notas Diarias</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{data.notasDiarias}</p>
					</div>
					<div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
						<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
						</svg>
					</div>
				</div>
			</div>

			<!-- Diagnósticos Pendientes -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Atenciones Clínicas</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{data.atenciones}</p>
					</div>
					<div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
						<svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
				</div>
			</div>

			<!-- Alertas Críticas -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Alertas Críticas</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{data.alertasCriticas}</p>
					</div>
					<div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
						<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
				</div>
			</div>
		</div>

		<!-- Atenciones Recientes -->
		<div class="bg-white rounded-xl shadow-lg overflow-hidden">
			<div class="px-6 py-4 border-b border-gray-200">
				<h2 class="text-lg font-semibold text-gray-900">Atenciones Recientes</h2>
			</div>
			{#if data.atencionesRecientes.length === 0}
				<p class="px-6 py-8 text-center text-sm text-gray-500">
					No se han registrado atenciones clínicas todavía.
				</p>
			{:else}
				<div class="divide-y divide-gray-200">
					{#each data.atencionesRecientes as atencion (atencion.id_atencion)}
						<div class="px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer">
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-4">
									<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
										<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
										</svg>
									</div>
									<div>
										<p class="text-sm font-semibold text-gray-900">
											{atencion.paciente_nombres} {atencion.paciente_apellidos}
										</p>
										<p class="text-xs text-gray-500">{formatFechaHora(atencion.fecha_atencion)}</p>
									</div>
								</div>
								<span class="px-3 py-1 text-xs font-medium rounded-full {badgeTipoAtencion[atencion.tipo_atencion] ?? 'bg-gray-100 text-gray-800'}">
									{atencion.tipo_atencion}
								</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
