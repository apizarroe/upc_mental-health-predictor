<script>
	import { goto } from '$app/navigation';

	let { data } = $props();

	let passwordActual = '';
	let passwordNueva = '';
	let passwordConfirmacion = '';
	let error = '';
	let success = '';
	let loading = false;

	async function handleSubmit() {
		error = '';
		success = '';

		// Validaciones básicas
		if (!passwordActual || !passwordNueva || !passwordConfirmacion) {
			error = 'Todos los campos son obligatorios';
			return;
		}

		if (passwordNueva !== passwordConfirmacion) {
			error = 'Las contraseñas nuevas no coinciden';
			return;
		}

		if (passwordNueva.length < 8) {
			error = 'La contraseña debe tener al menos 8 caracteres';
			return;
		}

		// Validar complejidad de contraseña
		const hasUpperCase = /[A-Z]/.test(passwordNueva);
		const hasLowerCase = /[a-z]/.test(passwordNueva);
		const hasNumber = /[0-9]/.test(passwordNueva);

		if (!hasUpperCase || !hasLowerCase || !hasNumber) {
			error = 'La contraseña debe contener mayúsculas, minúsculas y números';
			return;
		}

		loading = true;

		try {
			const response = await fetch('/api/auth/cambiar-password', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					passwordActual,
					passwordNueva,
					passwordConfirmacion
				})
			});

			const result = await response.json();

			if (result.success) {
				success = 'Contraseña cambiada exitosamente';
				passwordActual = '';
				passwordNueva = '';
				passwordConfirmacion = '';

				// Redirigir al perfil después de 2 segundos
				setTimeout(() => {
					goto('/paciente/perfil');
				}, 2000);
			} else {
				error = result.error || 'Error al cambiar contraseña';
			}
		} catch (err) {
			error = 'Error de conexión al servidor';
			console.error('Error:', err);
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-md mx-auto p-6">
	<h1 class="text-white text-3xl font-bold mb-6">Cambiar Contraseña</h1>

	<div class="bg-white shadow rounded-lg p-6">
		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<!-- Contraseña Actual -->
			<div>
				<label for="passwordActual" class="block text-sm font-medium text-gray-700">
					Contraseña Actual
				</label>
				<input
					type="password"
					id="passwordActual"
					bind:value={passwordActual}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					disabled={loading}
				/>
			</div>

			<!-- Contraseña Nueva -->
			<div>
				<label for="passwordNueva" class="block text-sm font-medium text-gray-700">
					Contraseña Nueva
				</label>
				<input
					type="password"
					id="passwordNueva"
					bind:value={passwordNueva}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					disabled={loading}
				/>
				<p class="mt-1 text-xs text-gray-500">
					Mínimo 8 caracteres, debe contener mayúsculas, minúsculas y números
				</p>
			</div>

			<!-- Confirmar Contraseña -->
			<div>
				<label for="passwordConfirmacion" class="block text-sm font-medium text-gray-700">
					Confirmar Contraseña Nueva
				</label>
				<input
					type="password"
					id="passwordConfirmacion"
					bind:value={passwordConfirmacion}
					required
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
					disabled={loading}
				/>
			</div>

			<!-- Mensajes de Error/Éxito -->
			{#if error}
				<div class="bg-red-50 border-l-4 border-red-400 p-4">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm text-red-700">{error}</p>
						</div>
					</div>
				</div>
			{/if}

			{#if success}
				<div class="bg-green-50 border-l-4 border-green-400 p-4">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm text-green-700">{success}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Botones -->
			<div class="flex gap-4">
				<button
					type="submit"
					disabled={loading}
					class="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{loading ? 'Cambiando...' : 'Cambiar Contraseña'}
				</button>

				<a
					href="/paciente/perfil"
					class="flex-1 inline-flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				>
					Cancelar
				</a>
			</div>
		</form>
	</div>
</div>
