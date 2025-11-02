<script>
	let { data } = $props();
	let user = $derived(data.user);
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
			</div>
		</div>
	</div>
</div>
