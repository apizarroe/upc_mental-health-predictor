<script>
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();
	let user = $derived(data.user);

	let formData = $state({
		nombres: user.nombres || '',
		apellidos: user.apellidos || '',
		telefono: user.telefono || '',
		correo: user.correo || '',
		direccion: user.direccion || '',
		contacto_emergencia: user.contacto_emergencia || '',
		telefono_emergencia: user.telefono_emergencia || ''
	});

	let isSaving = $state(false);
	let message = $state({ type: '', text: '' });

	// Estado para cambio de contraseña
	let passwordData = $state({
		nueva: '',
		confirmar: ''
	});
	let isChangingPassword = $state(false);
	let passwordMessage = $state({ type: '', text: '' });

	// Función para formatear fecha sin problemas de zona horaria
	function formatearFecha(fecha) {
		if (!fecha) return '';
		// Si es un objeto Date, convertir a ISO string primero
		const fechaStr = fecha instanceof Date ? fecha.toISOString() : String(fecha);
		// Extraer solo la parte de la fecha (YYYY-MM-DD) y convertir a DD/MM/YYYY
		const fechaSolo = fechaStr.split('T')[0]; // "1986-08-15"
		const [año, mes, dia] = fechaSolo.split('-');
		return `${dia}/${mes}/${año}`;
	}

	async function handleSubmit(e) {
		e.preventDefault();
		isSaving = true;
		message = { type: '', text: '' };

		try {
			const response = await fetch('/api/pacientes/perfil', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				message = { type: 'success', text: 'Perfil actualizado correctamente' };
				// Recargar todos los datos del layout para reflejar los cambios
				await invalidateAll();
			} else {
				message = { type: 'error', text: result.error || 'Error al actualizar el perfil' };
			}
		} catch (error) {
			console.error('Error:', error);
			message = { type: 'error', text: 'Error de conexión. Por favor, intente nuevamente.' };
		} finally {
			isSaving = false;
		}
	}

	async function handlePasswordChange(e) {
		e.preventDefault();
		passwordMessage = { type: '', text: '' };

		// Validar que las contraseñas coincidan
		if (passwordData.nueva !== passwordData.confirmar) {
			passwordMessage = { type: 'error', text: 'Las contraseñas no coinciden' };
			return;
		}

		// Validar longitud mínima
		if (passwordData.nueva.length < 6) {
			passwordMessage = { type: 'error', text: 'La contraseña debe tener al menos 6 caracteres' };
			return;
		}

		isChangingPassword = true;

		try {
			const response = await fetch('/api/pacientes/cambiar-password', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ passwordNueva: passwordData.nueva })
			});

			const result = await response.json();

			if (result.success) {
				passwordMessage = { type: 'success', text: 'Contraseña actualizada correctamente' };
				// Limpiar formulario
				passwordData = { nueva: '', confirmar: '' };
			} else {
				passwordMessage = { type: 'error', text: result.error || 'Error al cambiar la contraseña' };
			}
		} catch (error) {
			console.error('Error:', error);
			passwordMessage = { type: 'error', text: 'Error de conexión. Por favor, intente nuevamente.' };
		} finally {
			isChangingPassword = false;
		}
	}
</script>

<svelte:head>
	<title>Mi Perfil - Portal de Pacientes</title>
</svelte:head>

<div class="p-8">
	<div class="max-w-4xl mx-auto">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-white mb-2">Mi Perfil</h1>
			<p class="text-white/80">Actualiza tu información personal</p>
		</div>

		<!-- Form Card -->
		<div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
			<div class="px-8 py-6 border-b border-gray-200" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);">
				<h2 class="text-xl font-bold text-gray-800">Información Personal</h2>
				<p class="text-sm text-gray-600 mt-1">Algunos campos no se pueden modificar por seguridad</p>
			</div>

			<form onsubmit={handleSubmit} class="p-8">
				{#if message.text}
					<div class="mb-6 p-4 rounded-lg {message.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'}">
						<div class="flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								{#if message.type === 'success'}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								{:else}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								{/if}
							</svg>
							<span>{message.text}</span>
						</div>
					</div>
				{/if}

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- DNI (solo lectura) -->
					<div>
						<label class="block text-sm font-semibold text-gray-700 mb-2">
							DNI
						</label>
						<input
							type="text"
							value={user.dni}
							disabled
							class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
						/>
						<p class="text-xs text-gray-500 mt-1">Este campo no se puede modificar</p>
					</div>

					<!-- Fecha de Nacimiento (solo lectura) -->
					<div>
						<label class="block text-sm font-semibold text-gray-700 mb-2">
							Fecha de Nacimiento
						</label>
						<input
							type="text"
							value={formatearFecha(user.fecha_nacimiento)}
							disabled
							class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
						/>
						<p class="text-xs text-gray-500 mt-1">Este campo no se puede modificar</p>
					</div>

					<!-- Nombres -->
					<div>
						<label for="nombres" class="block text-sm font-semibold text-gray-700 mb-2">
							Nombres
						</label>
						<input
							type="text"
							id="nombres"
							bind:value={formData.nombres}
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							required
						/>
					</div>

					<!-- Apellidos -->
					<div>
						<label for="apellidos" class="block text-sm font-semibold text-gray-700 mb-2">
							Apellidos
						</label>
						<input
							type="text"
							id="apellidos"
							bind:value={formData.apellidos}
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							required
						/>
					</div>

					<!-- Teléfono -->
					<div>
						<label for="telefono" class="block text-sm font-semibold text-gray-700 mb-2">
							Teléfono
						</label>
						<input
							type="tel"
							id="telefono"
							bind:value={formData.telefono}
							placeholder="999999999"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
						/>
					</div>

					<!-- Correo -->
					<div>
						<label for="correo" class="block text-sm font-semibold text-gray-700 mb-2">
							Correo Electrónico
						</label>
						<input
							type="email"
							id="correo"
							bind:value={formData.correo}
							placeholder="ejemplo@correo.com"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
						/>
					</div>

					<!-- Dirección (span 2 columns) -->
					<div class="md:col-span-2">
						<label for="direccion" class="block text-sm font-semibold text-gray-700 mb-2">
							Dirección
						</label>
						<input
							type="text"
							id="direccion"
							bind:value={formData.direccion}
							placeholder="Calle, número, distrito"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
						/>
					</div>

					<!-- Contacto de Emergencia -->
					<div>
						<label for="contacto_emergencia" class="block text-sm font-semibold text-gray-700 mb-2">
							Contacto de Emergencia
						</label>
						<input
							type="text"
							id="contacto_emergencia"
							bind:value={formData.contacto_emergencia}
							placeholder="Nombre completo"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
						/>
					</div>

					<!-- Teléfono de Emergencia -->
					<div>
						<label for="telefono_emergencia" class="block text-sm font-semibold text-gray-700 mb-2">
							Teléfono de Emergencia
						</label>
						<input
							type="tel"
							id="telefono_emergencia"
							bind:value={formData.telefono_emergencia}
							placeholder="999999999"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
						/>
					</div>
				</div>

				<!-- Submit Button -->
				<div class="mt-8 flex justify-end gap-4">
					<button
						type="submit"
						disabled={isSaving}
						class="px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-xl"
						style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
					>
						{#if isSaving}
							<span class="flex items-center">
								<svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Guardando...
							</span>
						{:else}
							Guardar Cambios
						{/if}
					</button>
				</div>
			</form>
		</div>

		<!-- Card de Cambio de Contraseña -->
		<div class="bg-white rounded-2xl shadow-2xl overflow-hidden mt-8">
			<div class="px-8 py-6 border-b border-gray-200" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);">
				<h2 class="text-xl font-bold text-gray-800">Cambiar Contraseña</h2>
				<p class="text-sm text-gray-600 mt-1">Actualiza tu contraseña de acceso</p>
			</div>

			<form onsubmit={handlePasswordChange} class="p-8">
				{#if passwordMessage.text}
					<div class="mb-6 p-4 rounded-lg {passwordMessage.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'}">
						<div class="flex items-center">
							<svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
								{#if passwordMessage.type === 'success'}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								{:else}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								{/if}
							</svg>
							<span>{passwordMessage.text}</span>
						</div>
					</div>
				{/if}

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- Nueva Contraseña -->
					<div>
						<label for="password_nueva" class="block text-sm font-semibold text-gray-700 mb-2">
							Nueva Contraseña
						</label>
						<input
							type="password"
							id="password_nueva"
							bind:value={passwordData.nueva}
							placeholder="Mínimo 6 caracteres"
							minlength="6"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							required
						/>
					</div>

					<!-- Confirmar Contraseña -->
					<div>
						<label for="password_confirmar" class="block text-sm font-semibold text-gray-700 mb-2">
							Confirmar Contraseña
						</label>
						<input
							type="password"
							id="password_confirmar"
							bind:value={passwordData.confirmar}
							placeholder="Repite la nueva contraseña"
							minlength="6"
							class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							required
						/>
					</div>
				</div>

				<!-- Submit Button -->
				<div class="mt-8 flex justify-end">
					<button
						type="submit"
						disabled={isChangingPassword}
						class="px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-xl"
						style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
					>
						{#if isChangingPassword}
							<span class="flex items-center">
								<svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Cambiando...
							</span>
						{:else}
							Cambiar Contraseña
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
