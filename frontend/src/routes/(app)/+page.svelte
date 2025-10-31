<script>
	let { data } = $props();
	let user = $derived(data.user);
</script>

<svelte:head>
	<title>Dashboard - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-white mb-2">Dashboard</h1>
		<p class="text-white/80">Bienvenido al Sistema de Gestión de Salud Mental</p>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
		<!-- Pacientes Card -->
		<a href="/pacientes" class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Pacientes</p>
					<p class="text-3xl font-bold mt-2" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
						Ver lista
					</p>
				</div>
				<div class="w-16 h-16 rounded-full flex items-center justify-center" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);">
					<svg class="w-8 h-8" style="color: #667eea;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
				</div>
			</div>
		</a>

		<!-- Especialistas Card -->
		<a href="/especialistas" class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Especialistas</p>
					<p class="text-3xl font-bold mt-2" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
						Ver lista
					</p>
				</div>
				<div class="w-16 h-16 rounded-full flex items-center justify-center" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);">
					<svg class="w-8 h-8" style="color: #667eea;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
			</div>
		</a>

		<!-- Historias Clínicas Card -->
		<a href="/historias" class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Historias Clínicas</p>
					<p class="text-3xl font-bold mt-2" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
						Próximamente
					</p>
				</div>
				<div class="w-16 h-16 rounded-full flex items-center justify-center" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);">
					<svg class="w-8 h-8" style="color: #667eea;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
			</div>
		</a>
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
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
			</div>
		</div>
	</div>
</div>
