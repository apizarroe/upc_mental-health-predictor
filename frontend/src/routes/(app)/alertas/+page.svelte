<script>
	let { data } = $props();

	// Modos de filtro mutuamente excluyentes: 'todos' | 'mios' | 'buscar'
	let modoFiltro = $state('todos');
	let busquedaEspecialista = $state('');

	const modosFiltro = [
		{ valor: 'todos', etiqueta: 'Todos' },
		{ valor: 'mios', etiqueta: 'Mis pacientes' },
		{ valor: 'buscar', etiqueta: 'Buscar por especialista' }
	];

	const etiquetas = {
		ideacion_suicida: 'Ideación suicida',
		ideacion_pasiva: 'Ideación pasiva',
		autolesion: 'Autolesión',
		crisis_panico: 'Crisis de pánico',
		perdida_control: 'Pérdida de control',
		colapso: 'Colapso emocional',
		descompensacion: 'Descompensación'
	};

	let alertasFiltradas = $derived.by(() => {
		if (modoFiltro === 'mios') {
			return data.alertas.filter((alerta) => alerta.es_mi_paciente);
		}

		if (modoFiltro === 'buscar') {
			const query = busquedaEspecialista.trim().toLowerCase();
			if (!query) return data.alertas;
			return data.alertas.filter((alerta) => {
				const especialistas = alerta.especialistas_tratantes ?? [];
				return especialistas.some((e) => e.usuario?.toLowerCase().includes(query));
			});
		}

		return data.alertas;
	});

	function tiempoRelativo(fecha) {
		const diff = Math.floor((Date.now() - new Date(fecha)) / 1000);
		if (diff < 60) return 'hace un momento';
		if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
		if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`;
		return `hace ${Math.floor(diff / 86400)} días`;
	}

	function badgeRiesgo(nivel) {
		if (nivel === 'alto') return 'bg-red-100 text-red-800 border border-red-200';
		if (nivel === 'moderado') return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
		return 'bg-green-100 text-green-800 border border-green-200';
	}

	function iconoRiesgo(nivel) {
		if (nivel === 'alto') return '🔴';
		if (nivel === 'moderado') return '🟡';
		return '🟢';
	}

	// Modal de información del paciente
	let pacienteModal = $state(null);
	let modalLoading = $state(false);
	let modalError = $state(null);

	async function abrirModalPaciente(idPaciente) {
		modalLoading = true;
		modalError = null;
		pacienteModal = {};
		try {
			const response = await fetch(`/api/pacientes/${idPaciente}`);
			const result = await response.json();
			if (result.success) {
				pacienteModal = result.data;
			} else {
				modalError = result.error || 'Error al cargar la información del paciente';
			}
		} catch (err) {
			modalError = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			modalLoading = false;
		}
	}

	function cerrarModal() {
		pacienteModal = null;
		modalError = null;
	}

	function formatDate(dateString) {
		const date = new Date(dateString);
		return date.toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			timeZone: 'America/Lima'
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
	<title>Alertas de Riesgo - Sistema de Salud Mental</title>
</svelte:head>

<div class="py-8">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

		<!-- Header -->
		<div class="mb-8">
			<div class="mb-4 flex items-start justify-between">
				<div>
					<h1 class="flex items-center text-3xl font-bold text-white">
						<svg class="mr-3 h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
						</svg>
						Alertas de Riesgo
					</h1>
					<p class="mt-2 text-white/80">
						Notas con señales de riesgo detectadas en los últimos 14 días
					</p>
				</div>
			</div>

			<!-- Stats -->
			<div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="rounded-lg bg-red-100 p-3">
								<svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Total alertas</p>
								<p class="text-2xl font-semibold text-neutral-900">{data.alertas.length}</p>
							</div>
						</div>
					</div>
				</div>

				<div class="card">
					<div class="card-body">
						<div class="flex items-center">
							<div class="rounded-lg bg-purple-100 p-3">
								<svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
								</svg>
							</div>
							<div class="ml-4">
								<p class="text-sm font-medium text-neutral-600">Mis pacientes</p>
								<p class="text-2xl font-semibold text-neutral-900">
									{data.alertas.filter((a) => a.es_mi_paciente).length}
								</p>
							</div>
						</div>
					</div>
				</div>

			</div>
		</div>

		<!-- Contenido principal en card -->
		<div class="card">
			<div class="card-body">

				<!-- Filtro -->
				<div class="mb-4 flex flex-col gap-3 border-b border-neutral-100 pb-4 sm:flex-row sm:items-center sm:justify-between">
					<p class="text-sm text-neutral-500">
						Mostrando <span class="font-semibold text-neutral-800">{alertasFiltradas.length}</span>
						alerta{alertasFiltradas.length !== 1 ? 's' : ''}
					</p>
					<div class="flex flex-col gap-3 sm:flex-row sm:items-center">
						<div class="inline-flex rounded-lg border border-neutral-200 bg-neutral-50 p-1 text-sm">
							{#each modosFiltro as modo}
								<button
									type="button"
									onclick={() => (modoFiltro = modo.valor)}
									class="rounded-md px-3 py-1.5 font-medium whitespace-nowrap transition {modoFiltro === modo.valor
										? 'bg-white text-neutral-900 shadow-sm'
										: 'text-neutral-500 hover:text-neutral-700'}"
								>
									{modo.etiqueta}
								</button>
							{/each}
						</div>

						{#if modoFiltro === 'buscar'}
							<label class="relative">
								<svg class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
								</svg>
								<input
									type="text"
									placeholder="Usuario del especialista"
									class="input input-sm input-bordered w-full rounded-lg pl-9 sm:w-56"
									bind:value={busquedaEspecialista}
								/>
							</label>
						{/if}
					</div>
				</div>

				<!-- Lista -->
				{#if alertasFiltradas.length === 0}
					<div class="py-12 text-center">
						<svg class="mx-auto mb-4 h-12 w-12 text-neutral-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<p class="font-semibold text-neutral-500">Sin alertas activas</p>
						<p class="mt-1 text-sm text-neutral-400">
							{#if modoFiltro === 'buscar' && busquedaEspecialista.trim()}
								No se encontraron alertas de pacientes atendidos por un especialista con ese usuario
							{:else if modoFiltro === 'mios'}
								Ninguno de tus pacientes tiene señales de riesgo en las últimas 2 semanas
							{:else}
								No hay señales de riesgo detectadas en las últimas 2 semanas
							{/if}
						</p>
					</div>
				{:else}
					<div class="space-y-3">
						{#each alertasFiltradas as alerta (alerta.id_respuesta)}
							{@const señales = alerta.trastornos_detectados?.risk_assessment?.señales_detectadas ?? []}
							{@const tiposUnicos = [...new Set(señales.map((s) => s.tipo))]}

							<div class="rounded-lg border border-neutral-200 bg-white p-4 transition-shadow hover:shadow-sm">
								<div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

									<!-- Info -->
									<div class="flex-1">
										<div class="mb-2 flex flex-wrap items-center gap-2">
											<span class="font-semibold text-neutral-900">
												{alerta.paciente_apellidos}, {alerta.paciente_nombres}
											</span>
											<span class="rounded-full px-2 py-0.5 text-xs font-semibold {badgeRiesgo(alerta.nivel_riesgo_global)}">
												{iconoRiesgo(alerta.nivel_riesgo_global)}
												{alerta.nivel_riesgo_global ?? 'desconocido'}
											</span>
											{#if alerta.es_mi_paciente}
												<span class="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
													Mi paciente
												</span>
											{/if}
										</div>

										<!-- Tipos de señal -->
										<div class="mb-2 flex flex-wrap gap-1">
											{#each tiposUnicos as tipo}
												<span class="rounded bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
													{etiquetas[tipo] ?? tipo}
												</span>
											{/each}
										</div>

										<!-- Frases detectadas -->
										<ul class="space-y-0.5">
											{#each señales as señal}
												<li class="text-sm italic text-neutral-600">"{señal.frase}"</li>
											{/each}
										</ul>
									</div>

									<!-- Acciones -->
									<div class="flex flex-col items-end gap-2">
										<span class="text-xs text-neutral-400">
											{tiempoRelativo(alerta.fecha_evaluacion)}
										</span>
										<div class="flex gap-2">
											<a
												href="/pacientes/{alerta.id_paciente}/notas/{alerta.id_respuesta}"
												class="btn btn-sm btn-outline border-red-200 text-red-700 hover:bg-red-50"
											>
												Ver nota
											</a>
											<button
												onclick={() => abrirModalPaciente(alerta.id_paciente)}
												class="btn btn-sm btn-ghost text-neutral-600"
											>
												Ver paciente
											</button>
										</div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<!-- Modal: Información del paciente -->
{#if pacienteModal !== null}
	<div
		class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4"
		onclick={cerrarModal}
		onkeydown={(e) => e.key === 'Escape' && cerrarModal()}
		role="presentation"
	>
		<div
			class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white shadow-2xl"
			onclick={(e) => e.stopPropagation()}
			role="dialog"
			aria-modal="true"
			tabindex="-1"
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between rounded-t-xl px-6 py-4"
				style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
			>
				<h3 class="text-lg font-semibold text-white">Información del Paciente</h3>
				<button
					onclick={cerrarModal}
					class="rounded-full p-1 text-white/80 transition-colors hover:bg-white/20 hover:text-white"
					aria-label="Cerrar"
				>
					<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<!-- Body -->
			<div class="px-6 py-5">
				{#if modalLoading}
					<div class="flex flex-col items-center justify-center py-10">
						<div class="mb-3 h-10 w-10 animate-spin rounded-full border-b-2 border-purple-600"></div>
						<p class="text-sm text-neutral-500">Cargando información...</p>
					</div>
				{:else if modalError}
					<p class="py-6 text-center text-sm text-red-600">{modalError}</p>
				{:else if pacienteModal?.dni}
					<!-- Información Personal -->
					<div class="mb-6">
						<h4 class="mb-3 border-b border-neutral-200 pb-2 text-sm font-semibold text-neutral-700">
							Información Personal
						</h4>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<p class="text-xs font-medium text-neutral-500">DNI</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.dni}</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Fecha de Nacimiento</p>
								<p class="mt-0.5 text-sm text-neutral-900">
									{formatDate(pacienteModal.fecha_nacimiento)}
									<span class="text-neutral-500">({calcularEdad(pacienteModal.fecha_nacimiento)} años)</span>
								</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Sexo</p>
								<p class="mt-0.5 text-sm text-neutral-900">
									{pacienteModal.sexo === 'M' ? 'Masculino' : 'Femenino'}
								</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Estado</p>
								<p class="mt-0.5">
									<span
										class="inline-flex rounded-full px-2 py-0.5 text-xs font-semibold {pacienteModal.flg_activo
											? 'bg-green-100 text-green-800'
											: 'bg-red-100 text-red-800'}"
									>
										{pacienteModal.flg_activo ? 'Activo' : 'Inactivo'}
									</span>
								</p>
							</div>
						</div>
					</div>

					<!-- Información de Contacto -->
					<div class="mb-6">
						<h4 class="mb-3 border-b border-neutral-200 pb-2 text-sm font-semibold text-neutral-700">
							Información de Contacto
						</h4>
						<div class="grid grid-cols-2 gap-4">
							<div class="col-span-2">
								<p class="text-xs font-medium text-neutral-500">Dirección</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.direccion}</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Teléfono</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.telefono}</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Correo Electrónico</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.correo}</p>
							</div>
						</div>
					</div>

					<!-- Contacto de Emergencia -->
					<div>
						<h4 class="mb-3 border-b border-neutral-200 pb-2 text-sm font-semibold text-neutral-700">
							Contacto de Emergencia
						</h4>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<p class="text-xs font-medium text-neutral-500">Nombre</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.contacto_emergencia}</p>
							</div>
							<div>
								<p class="text-xs font-medium text-neutral-500">Teléfono</p>
								<p class="mt-0.5 text-sm text-neutral-900">{pacienteModal.telefono_emergencia}</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
