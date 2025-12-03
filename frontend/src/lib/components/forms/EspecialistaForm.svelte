<script>
	let { especialista = null, onSubmit = () => {}, isLoading = false, submitLabel = 'Guardar' } = $props();

	// Datos del formulario
	let formData = {
		dni: especialista?.dni || '',
		nombres: especialista?.nombres || '',
		apellidos: especialista?.apellidos || '',
		especialidad: especialista?.especialidad || '',
		colegiatura: especialista?.colegiatura || '',
		correo: especialista?.correo || '',
		telefono: especialista?.telefono || '',
		cargo: especialista?.cargo || '',
		rol: especialista?.rol || 'especialista'
	};

	let errors = $state({});

	// Validación en tiempo real para DNI (solo números, máximo 8 caracteres)
	function handleDniInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea número
		let cleanValue = value.replace(/\D/g, '');

		// Verificar si se intenta superar el límite de 8 caracteres
		if (cleanValue.length > 8) {
			alert('El DNI no puede superar los 8 caracteres numéricos');
			cleanValue = cleanValue.slice(0, 8);
		}

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.dni = cleanValue;
	}

	// Validación en tiempo real para Nombres (solo letras y espacios, máximo 80 caracteres)
	function handleNombresInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea letra o espacio
		let cleanValue = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');

		// Verificar si se intenta superar el límite de 80 caracteres
		if (cleanValue.length > 80) {
			alert('Los nombres no pueden superar los 80 caracteres');
			cleanValue = cleanValue.slice(0, 80);
		}

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.nombres = cleanValue;
	}

	// Validación en tiempo real para Apellidos (solo letras y espacios, máximo 80 caracteres)
	function handleApellidosInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea letra o espacio
		let cleanValue = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');

		// Verificar si se intenta superar el límite de 80 caracteres
		if (cleanValue.length > 80) {
			alert('Los apellidos no pueden superar los 80 caracteres');
			cleanValue = cleanValue.slice(0, 80);
		}

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.apellidos = cleanValue;
	}

	// Validación en tiempo real para Teléfono (solo números, máximo 9 dígitos)
	function handleTelefonoInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea número
		let cleanValue = value.replace(/\D/g, '');

		// Verificar si se intenta superar el límite de 9 caracteres
		if (cleanValue.length > 9) {
			alert('El teléfono no puede superar los 9 dígitos');
			cleanValue = cleanValue.slice(0, 9);
		}

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.telefono = cleanValue;
	}

	function validateForm() {
		errors = {};

		// Validación de DNI
		if (!formData.dni) {
			errors.dni = 'DNI es requerido';
		} else if (!/^\d{8}$/.test(formData.dni)) {
			errors.dni = 'DNI debe tener exactamente 8 dígitos numéricos';
		}

		// Validación de Nombres
		if (!formData.nombres) {
			errors.nombres = 'Nombres son requeridos';
		} else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(formData.nombres)) {
			errors.nombres = 'Los nombres solo pueden contener letras y espacios';
		} else if (formData.nombres.length > 80) {
			errors.nombres = 'Los nombres no pueden superar los 80 caracteres';
		}

		// Validación de Apellidos
		if (!formData.apellidos) {
			errors.apellidos = 'Apellidos son requeridos';
		} else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(formData.apellidos)) {
			errors.apellidos = 'Los apellidos solo pueden contener letras y espacios';
		} else if (formData.apellidos.length > 80) {
			errors.apellidos = 'Los apellidos no pueden superar los 80 caracteres';
		}

		if (!formData.especialidad) errors.especialidad = 'Especialidad es requerida';
		if (!formData.colegiatura) errors.colegiatura = 'Colegiatura es requerida';

		// Validación de Teléfono
		if (!formData.telefono) {
			errors.telefono = 'Teléfono es requerido';
		} else if (!/^\d{9}$/.test(formData.telefono)) {
			errors.telefono = 'El teléfono debe tener exactamente 9 dígitos numéricos';
		}

		if (!formData.correo) errors.correo = 'Correo es requerido';
		else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
			errors.correo = 'Correo inválido';
		}
		if (!formData.cargo) errors.cargo = 'Cargo es requerido';
		if (!formData.rol) errors.rol = 'Rol es requerido';

		return Object.keys(errors).length === 0;
	}

	function handleSubmit() {
		if (validateForm()) {
			onSubmit(formData);
		}
	}
</script>

<form onsubmit={(e) => { e.preventDefault(); handleSubmit(e); }} class="space-y-6">
	<!-- DNI y Nombres -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="dni" class="block text-sm font-medium text-gray-700 mb-1">
				DNI <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="dni"
				value={formData.dni}
				oninput={handleDniInput}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.dni}
				disabled={isLoading}
			/>
			{#if errors.dni}
				<p class="text-red-500 text-sm mt-1">{errors.dni}</p>
			{/if}
		</div>

		<div>
			<label for="nombres" class="block text-sm font-medium text-gray-700 mb-1">
				Nombres <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="nombres"
				value={formData.nombres}
				oninput={handleNombresInput}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.nombres}
				disabled={isLoading}
			/>
			{#if errors.nombres}
				<p class="text-red-500 text-sm mt-1">{errors.nombres}</p>
			{/if}
		</div>
	</div>

	<!-- Apellidos y Rol -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="apellidos" class="block text-sm font-medium text-gray-700 mb-1">
				Apellidos <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="apellidos"
				value={formData.apellidos}
				oninput={handleApellidosInput}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.apellidos}
				disabled={isLoading}
			/>
			{#if errors.apellidos}
				<p class="text-red-500 text-sm mt-1">{errors.apellidos}</p>
			{/if}
		</div>

		<div>
			<label for="rol" class="block text-sm font-medium text-gray-700 mb-1">
				Rol <span class="text-red-500">*</span>
			</label>
			<select
				id="rol"
				bind:value={formData.rol}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.rol}
				disabled={isLoading}
			>
				<option value="especialista">Especialista</option>
				<option value="admin">Admin</option>
			</select>
			{#if errors.rol}
				<p class="text-red-500 text-sm mt-1">{errors.rol}</p>
			{/if}
		</div>
	</div>

	<!-- Especialidad -->
	<div>
		<label for="especialidad" class="block text-sm font-medium text-gray-700 mb-1">
			Especialidad <span class="text-red-500">*</span>
		</label>
		<input
			type="text"
			id="especialidad"
			bind:value={formData.especialidad}
			maxlength="50"
			placeholder="Ej: Psicólogo Clínico, Psiquiatra"
			class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			class:border-red-500={errors.especialidad}
			disabled={isLoading}
		/>
		{#if errors.especialidad}
			<p class="text-red-500 text-sm mt-1">{errors.especialidad}</p>
		{/if}
	</div>

	<!-- Colegiatura y Cargo -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="colegiatura" class="block text-sm font-medium text-gray-700 mb-1">
				Número de Colegiatura <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="colegiatura"
				bind:value={formData.colegiatura}
				maxlength="20"
				placeholder="Ej: CPsP12345, CMP23456"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.colegiatura}
				disabled={isLoading}
			/>
			{#if errors.colegiatura}
				<p class="text-red-500 text-sm mt-1">{errors.colegiatura}</p>
			{/if}
		</div>

		<div>
			<label for="cargo" class="block text-sm font-medium text-gray-700 mb-1">
				Cargo <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="cargo"
				bind:value={formData.cargo}
				maxlength="50"
				placeholder="Ej: Psicólogo Senior, Director"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.cargo}
				disabled={isLoading}
			/>
			{#if errors.cargo}
				<p class="text-red-500 text-sm mt-1">{errors.cargo}</p>
			{/if}
		</div>
	</div>

	<!-- Teléfono y Correo -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="telefono" class="block text-sm font-medium text-gray-700 mb-1">
				Teléfono <span class="text-red-500">*</span>
			</label>
			<input
				type="tel"
				id="telefono"
				value={formData.telefono}
				oninput={handleTelefonoInput}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.telefono}
				disabled={isLoading}
			/>
			{#if errors.telefono}
				<p class="text-red-500 text-sm mt-1">{errors.telefono}</p>
			{/if}
		</div>

		<div>
			<label for="correo" class="block text-sm font-medium text-gray-700 mb-1">
				Correo Electrónico <span class="text-red-500">*</span>
			</label>
			<input
				type="email"
				id="correo"
				bind:value={formData.correo}
				maxlength="50"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.correo}
				disabled={isLoading}
			/>
			{#if errors.correo}
				<p class="text-red-500 text-sm mt-1">{errors.correo}</p>
			{/if}
		</div>
	</div>

	<!-- Botón Submit -->
	<div class="flex justify-end">
		<button
			type="submit"
			disabled={isLoading}
			class="btn-primary"
		>
			{#if isLoading}
				Guardando...
			{:else}
				{submitLabel}
			{/if}
		</button>
	</div>
</form>
