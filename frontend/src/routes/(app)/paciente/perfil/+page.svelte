<script>
	let { data } = $props();

	const { user } = data;
</script>

<div class="max-w-4xl mx-auto p-6">
	<h1 class="text-white text-3xl font-bold mb-6">Mi Perfil</h1>

	<div class="bg-white shadow rounded-lg p-6 space-y-6">
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Información Personal -->
			<div class="space-y-4">
				<h2 class="text-xl font-semibold border-b pb-2">Información Personal</h2>

				<div>
					<label class="block text-sm font-medium text-gray-700">DNI</label>
					<p class="mt-1 text-gray-900">{user.dni || 'No disponible'}</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700">Nombres</label>
					<p class="mt-1 text-gray-900">{user.nombres}</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700">Apellidos</label>
					<p class="mt-1 text-gray-900">{user.apellidos}</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700">Usuario</label>
					<p class="mt-1 text-gray-900">{user.usuario}</p>
				</div>
			</div>

			<!-- Información de Contacto -->
			<div class="space-y-4">
				<h2 class="text-xl font-semibold border-b pb-2">Información de Contacto</h2>

				<div>
					<label class="block text-sm font-medium text-gray-700">Correo Electrónico</label>
					<p class="mt-1 text-gray-900">{user.correo || 'No disponible'}</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700">Rol</label>
					<p class="mt-1">
						<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
							{user.rol}
						</span>
					</p>
				</div>
			</div>
		</div>

		<!-- Acciones -->
		<div class="border-t pt-6">
			<h2 class="text-xl font-semibold mb-4">Acciones</h2>
			<div class="flex gap-4">
				<a
					href="/paciente/cambiar-password"
					class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				>
					Cambiar Contraseña
				</a>
			</div>
		</div>

		<!-- Nota informativa -->
		<div class="bg-blue-50 border-l-4 border-blue-400 p-4">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm text-blue-700">
						Si necesitas actualizar tu información de contacto o datos personales, por favor contacta a tu especialista.
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
