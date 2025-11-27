<script>
	import { createEventDispatcher } from 'svelte';

	export let nombreUsuario = '';
	export let tipoUsuario = 'especialista'; // 'especialista' o 'paciente'

	const dispatch = createEventDispatcher();

	let passwordNueva = '';
	let passwordConfirmacion = '';
	let loading = false;
	let error = '';
	let mostrarPassword = false;

	// Validación de contraseña
	$: passwordValida =
		passwordNueva.length >= 8 &&
		/[A-Z]/.test(passwordNueva) &&
		/[a-z]/.test(passwordNueva) &&
		/[0-9]/.test(passwordNueva);

	$: passwordsCoinciden = passwordNueva === passwordConfirmacion && passwordNueva.length > 0;

	// Indicadores de validación individuales
	$: tieneMinimo8 = passwordNueva.length >= 8;
	$: tieneMayuscula = /[A-Z]/.test(passwordNueva);
	$: tieneMinuscula = /[a-z]/.test(passwordNueva);
	$: tieneNumero = /[0-9]/.test(passwordNueva);

	async function handleSubmit() {
		// Validaciones
		if (!passwordValida) {
			error =
				'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número';
			return;
		}

		if (!passwordsCoinciden) {
			error = 'Las contraseñas no coinciden';
			return;
		}

		loading = true;
		error = '';

		try {
			const endpoint =
				tipoUsuario === 'paciente'
					? '/api/pacientes/cambiar-password-primer-login'
					: '/api/especialistas/cambiar-password-primer-login';

			const response = await fetch(endpoint, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					passwordNueva
				})
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Error al cambiar la contraseña');
			}

			// Emitir evento de éxito
			dispatch('success');
		} catch (err) {
			error = err.message;
		} finally {
			loading = false;
		}
	}
</script>

<!-- Modal de fondo (no se puede cerrar) -->
<div class="modal-overlay">
	<div class="modal-container">
		<div class="modal-header">
			<h2>Cambio de Contraseña Obligatorio</h2>
			<p class="modal-subtitle">Bienvenido/a, {nombreUsuario}</p>
		</div>

		<div class="modal-body">
			<div class="info-box">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="1.5"
					stroke="currentColor"
					class="info-icon"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
					/>
				</svg>
				<p>
					Por seguridad, es necesario que cambies tu contraseña temporal por una contraseña
					personal. Esta contraseña debe ser única y que solo tú conozcas.
				</p>
			</div>

			<form on:submit|preventDefault={handleSubmit}>
				<!-- Nueva contraseña -->
				<div class="form-group">
					<label for="passwordNueva">Nueva Contraseña</label>
					<div class="password-input-wrapper">
						<input
							id="passwordNueva"
							type={mostrarPassword ? 'text' : 'password'}
							bind:value={passwordNueva}
							placeholder="Ingrese su nueva contraseña"
							required
							disabled={loading}
							class:invalid={passwordNueva.length > 0 && !passwordValida}
							class:valid={passwordValida}
						/>
						<button
							type="button"
							class="toggle-password"
							on:click={() => (mostrarPassword = !mostrarPassword)}
							tabindex="-1"
						>
							{#if mostrarPassword}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									class="icon"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
									/>
								</svg>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									class="icon"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
									/>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
									/>
								</svg>
							{/if}
						</button>
					</div>

					<!-- Indicadores de validación -->
					<div class="validation-indicators">
						<div class="indicator" class:valid={tieneMinimo8}>
							<span class="indicator-icon">{tieneMinimo8 ? '✓' : '○'}</span>
							Mínimo 8 caracteres
						</div>
						<div class="indicator" class:valid={tieneMayuscula}>
							<span class="indicator-icon">{tieneMayuscula ? '✓' : '○'}</span>
							Una letra mayúscula
						</div>
						<div class="indicator" class:valid={tieneMinuscula}>
							<span class="indicator-icon">{tieneMinuscula ? '✓' : '○'}</span>
							Una letra minúscula
						</div>
						<div class="indicator" class:valid={tieneNumero}>
							<span class="indicator-icon">{tieneNumero ? '✓' : '○'}</span>
							Un número
						</div>
					</div>
				</div>

				<!-- Confirmar contraseña -->
				<div class="form-group">
					<label for="passwordConfirmacion">Confirmar Contraseña</label>
					<input
						id="passwordConfirmacion"
						type={mostrarPassword ? 'text' : 'password'}
						bind:value={passwordConfirmacion}
						placeholder="Confirme su nueva contraseña"
						required
						disabled={loading}
						class:invalid={passwordConfirmacion.length > 0 && !passwordsCoinciden}
						class:valid={passwordsCoinciden}
					/>
					{#if passwordConfirmacion.length > 0 && !passwordsCoinciden}
						<span class="error-text">Las contraseñas no coinciden</span>
					{/if}
				</div>

				<!-- Error general -->
				{#if error}
					<div class="error-box">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="error-icon"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
							/>
						</svg>
						<span>{error}</span>
					</div>
				{/if}

				<!-- Botón de submit -->
				<button
					type="submit"
					class="btn-submit"
					disabled={!passwordValida || !passwordsCoinciden || loading}
				>
					{#if loading}
						Cambiando contraseña...
					{:else}
						Cambiar Contraseña
					{/if}
				</button>
			</form>
		</div>
	</div>
</div>

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 9999;
		padding: 1rem;
		backdrop-filter: blur(4px);
	}

	.modal-container {
		background: white;
		border-radius: 12px;
		max-width: 500px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
	}

	.modal-header {
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 12px 12px 0 0;
	}

	.modal-header h2 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 700;
	}

	.modal-subtitle {
		margin: 0.5rem 0 0 0;
		font-size: 0.95rem;
		opacity: 0.9;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.info-box {
		display: flex;
		gap: 1rem;
		padding: 1rem;
		background: #eff6ff;
		border: 1px solid #bfdbfe;
		border-radius: 8px;
		margin-bottom: 1.5rem;
		color: #1e40af;
		font-size: 0.9rem;
		line-height: 1.5;
	}

	.info-icon {
		width: 24px;
		height: 24px;
		flex-shrink: 0;
		margin-top: 2px;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 600;
		color: #374151;
		font-size: 0.9rem;
	}

	.password-input-wrapper {
		position: relative;
	}

	input {
		width: 100%;
		padding: 0.75rem;
		border: 2px solid #d1d5db;
		border-radius: 8px;
		font-size: 1rem;
		transition: all 0.2s;
		box-sizing: border-box;
	}

	input:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	input.valid {
		border-color: #10b981;
		background-color: #f0fdf4;
	}

	input.invalid {
		border-color: #ef4444;
		background-color: #fef2f2;
	}

	input:disabled {
		background-color: #f3f4f6;
		cursor: not-allowed;
	}

	.password-input-wrapper input {
		padding-right: 3rem;
	}

	.toggle-password {
		position: absolute;
		right: 0.75rem;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		cursor: pointer;
		color: #6b7280;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.toggle-password:hover {
		color: #374151;
	}

	.toggle-password .icon {
		width: 20px;
		height: 20px;
	}

	.validation-indicators {
		margin-top: 0.75rem;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}

	.indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.85rem;
		color: #6b7280;
		transition: color 0.2s;
	}

	.indicator.valid {
		color: #10b981;
	}

	.indicator-icon {
		font-weight: bold;
		width: 18px;
		text-align: center;
	}

	.error-text {
		display: block;
		margin-top: 0.5rem;
		color: #ef4444;
		font-size: 0.85rem;
	}

	.error-box {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 8px;
		color: #dc2626;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.error-icon {
		width: 20px;
		height: 20px;
		flex-shrink: 0;
	}

	.btn-submit {
		width: 100%;
		padding: 0.875rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.btn-submit:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
	}

	.btn-submit:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}
</style>
