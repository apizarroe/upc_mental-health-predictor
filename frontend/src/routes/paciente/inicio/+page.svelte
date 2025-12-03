<script>
	let { data } = $props();
	let user = $derived(data.user);
</script>

<svelte:head>
	<title>Inicio - Portal de Pacientes</title>
</svelte:head>

<div class="p-8">
	<div class="max-w-4xl mx-auto">
		<div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
			<div class="px-8 py-12 text-center" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);">
				<div class="w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-6" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);">
					<svg class="w-14 h-14 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
					</svg>
				</div>

				<h1 class="text-4xl font-bold mb-3" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
					¡Bienvenido/a!
				</h1>

				<p class="text-2xl font-semibold text-gray-800 mb-2">
					{user.nombres} {user.apellidos}
				</p>
				<p class="text-gray-600 flex items-center justify-center">
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
					</svg>
					DNI: {user.dni}
				</p>
			</div>

			<div class="px-8 py-10">
				<div class="space-y-6">
					<div class="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-lg">
						<div class="flex items-start">
							<svg class="w-6 h-6 text-blue-400 mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div>
								<h3 class="text-lg font-semibold text-blue-800 mb-2">
									Bienvenido al Portal de Pacientes
								</h3>
								<p class="text-blue-700">
									Gracias por acceder a nuestro sistema. Estamos trabajando para mejorar continuamente nuestros servicios y brindarle la mejor atención posible.
								</p>
							</div>
						</div>
					</div>

					<div class="bg-gray-50 rounded-lg p-6">
						<h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
							<svg class="w-6 h-6 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
							</svg>
							Información de Contacto
						</h3>
						<div class="space-y-3 text-gray-700">
							<p class="flex items-center">
								<svg class="w-5 h-5 mr-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
								</svg>
								<span>Para consultas, comuníquese con su especialista asignado</span>
							</p>
							<p class="flex items-center">
								<svg class="w-5 h-5 mr-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span>Horario de atención: Lunes a Viernes, 8:00 AM - 6:00 PM</span>
							</p>
						</div>
					</div>

					<div class="bg-amber-50 border-l-4 border-amber-400 p-6 rounded-lg">
						<div class="flex items-start">
							<svg class="w-6 h-6 text-amber-400 mr-3 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
							</svg>
							<div>
								<h3 class="text-lg font-semibold text-amber-800 mb-2">
									Recordatorio de Seguridad
								</h3>
								<p class="text-amber-700">
									Por su seguridad, su sesión expirará automáticamente después de 30 minutos de inactividad.
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="px-8 py-6 bg-gray-50 text-center border-t border-gray-200">
				<p class="text-sm text-gray-600">Centro de Salud Mental © 2024</p>
				<p class="text-xs text-gray-500 mt-1">Sus datos están protegidos conforme a la Ley de Protección de Datos Personales</p>
			</div>
		</div>
	</div>
</div>
