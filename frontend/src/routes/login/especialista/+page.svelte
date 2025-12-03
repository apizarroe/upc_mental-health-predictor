<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let usuario = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error = $state('');
	let showPassword = $state(false);

	// Verificar mensajes de URL
	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		if (urlParams.get('expired') === 'true') {
			error = 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.';
		} else if (urlParams.get('invalid') === 'true') {
			error = 'Su cuenta ha sido desactivada. Contacte al administrador.';
		}
	});

	async function handleSubmit(e) {
		e.preventDefault();
		error = '';

		if (!usuario || !password) {
			error = 'Por favor complete todos los campos';
			return;
		}

		try {
			isLoading = true;

			const response = await fetch('/api/auth/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ usuario, password })
			});

			const result = await response.json();

			if (result.success) {
				// Redirigir al dashboard de especialistas
				goto('/inicio');
			} else {
				error = result.error || 'Error al iniciar sesión';
			}
		} catch (err) {
			error = 'Error de conexión. Por favor, intente nuevamente.';
			console.error('Error en login:', err);
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Iniciar Sesión Especialista - Sistema de Salud Mental</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
	<div class="max-w-md w-full mx-4">
		<!-- Card de Login -->
		<div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
			<!-- Header -->
			<div class="px-8 pt-8 pb-6 text-center" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);">
				<div class="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center mb-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);">
					<svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
					</svg>
				</div>
				<h1 class="text-3xl font-bold mb-2" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
					Centro de Salud Mental
				</h1>
				<p class="text-gray-600">Acceso para Especialistas</p>
			</div>

			<!-- Form -->
			<div class="px-8 py-6">
				<form onsubmit={handleSubmit} class="space-y-6">
					<!-- Error Message -->
					{#if error}
						<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
							<div class="flex items-start">
								<svg class="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								</svg>
								<span>{error}</span>
							</div>
						</div>
					{/if}

					<!-- Usuario -->
					<div>
						<label for="usuario" class="block text-sm font-semibold text-gray-700 mb-2">
							Usuario
						</label>
						<div class="relative">
							<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
								<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
								</svg>
							</div>
							<input
								type="text"
								id="usuario"
								bind:value={usuario}
								disabled={isLoading}
								placeholder="Ingrese su usuario"
								class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
								required
							/>
						</div>
					</div>

					<!-- Contraseña -->
					<div>
						<label for="password" class="block text-sm font-semibold text-gray-700 mb-2">
							Contraseña
						</label>
						<div class="relative">
							<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
								<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
								</svg>
							</div>
							<input
								type={showPassword ? 'text' : 'password'}
								id="password"
								bind:value={password}
								disabled={isLoading}
								placeholder="Ingrese su contraseña"
								class="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
								required
							/>
							<button
								type="button"
								onclick={() => (showPassword = !showPassword)}
								class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
							>
								{#if showPassword}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
									</svg>
								{:else}
									<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
									</svg>
								{/if}
							</button>
						</div>
					</div>

					<!-- Submit Button -->
					<button
						type="submit"
						disabled={isLoading}
						class="w-full py-3 px-4 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
						style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
					>
						{#if isLoading}
							<span class="flex items-center justify-center">
								<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Iniciando sesión...
							</span>
						{:else}
							Iniciar Sesión
						{/if}
					</button>
				</form>
			</div>

			<!-- Footer -->
			<div class="px-8 py-4 bg-gray-50 text-center text-sm text-gray-600">
				<p>¿Olvidó su contraseña? Contacte al administrador</p>
				<a href="/" class="text-purple-600 hover:text-purple-700 font-semibold mt-2 inline-block">
					← Volver al login de pacientes
				</a>
			</div>
		</div>

		<!-- Info -->
		<div class="mt-6 text-center text-white text-sm">
			<p>Sistema de Gestión de Salud Mental</p>
			<p class="mt-1 opacity-80">Acceso restringido solo para personal autorizado</p>
		</div>
	</div>
</div>
