<script>
	import { canCreatePacientes, canCreateEspecialistas, canCreateHistorias } from '$lib/utils/permissions.js';

	let { data } = $props();
	let user = $derived(data.user);
	let conteoAlertas = $derived(data.conteoAlertas ?? 0);

	// Permisos del usuario actual
	const canCreatePatient = canCreatePacientes(user.rol);
	const canCreateSpecialist = canCreateEspecialistas(user.rol);
	const canCreateHistory = canCreateHistorias(user.rol);
</script>

<svelte:head>
	<title>Inicio - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-white mb-2 flex items-center">
			<svg class="w-8 h-8 text-white mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
			</svg>
			Inicio
		</h1>
		<p class="text-white/80">Bienvenido al Sistema de Gestión de Salud Mental</p>
	</div>

	<!-- Welcome Message -->
	<div class="bg-white rounded-xl shadow-lg p-8">
		<h2 class="text-2xl font-bold text-gray-900 mb-4">
			Bienvenido, {user.nombres} {user.apellidos}
		</h2>
		<p class="text-gray-600 mb-6">
			Has iniciado sesión como <span class="font-semibold capitalize">{user.rol}</span> en el Sistema de Gestión de Salud Mental.
		</p>

		<div class="border-t border-gray-200 pt-6">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Accesos Rápidos</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				{#if canCreatePatient}
					<a href="/pacientes/nuevo" class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 transition-all duration-300">
						<div class="w-10 h-10 rounded-lg flex items-center justify-center mr-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
							<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
						</div>
						<div>
							<p class="font-semibold text-gray-900">Nuevo Paciente</p>
							<p class="text-sm text-gray-600">Registrar un nuevo paciente</p>
						</div>
					</a>
				{/if}

				{#if canCreateSpecialist}
					<a href="/especialistas/nuevo" class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 transition-all duration-300">
						<div class="w-10 h-10 rounded-lg flex items-center justify-center mr-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
							<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
						</div>
						<div>
							<p class="font-semibold text-gray-900">Nuevo Especialista</p>
							<p class="text-sm text-gray-600">Registrar un nuevo especialista</p>
						</div>
					</a>
				{/if}

				{#if canCreateHistory}
					<a href="/historias/nuevo" class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 transition-all duration-300">
						<div class="w-10 h-10 rounded-lg flex items-center justify-center mr-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
							<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
						</div>
						<div>
							<p class="font-semibold text-gray-900">Nueva Historia Clínica</p>
							<p class="text-sm text-gray-600">Crear una nueva historia clínica</p>
						</div>
					</a>
				{/if}

				<a href="/alertas" class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 transition-all duration-300">
					<div class="relative mr-4 w-10 h-10 rounded-lg flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
						<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
						</svg>
						{#if conteoAlertas > 0}
							<span class="absolute -top-1.5 -right-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-xs font-bold text-white ring-2 ring-white">
								{conteoAlertas > 99 ? '99+' : conteoAlertas}
							</span>
						{/if}
					</div>
					<div>
						<p class="flex items-center gap-2 font-semibold text-gray-900">
							Alertas de Riesgo
							{#if conteoAlertas > 0}
								<span class="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
									{conteoAlertas > 99 ? '99+' : conteoAlertas} por revisar
								</span>
							{/if}
						</p>
						<p class="text-sm text-gray-600">Ver notas con señales de riesgo detectadas</p>
					</div>
				</a>
			</div>
		</div>
	</div>
</div>
