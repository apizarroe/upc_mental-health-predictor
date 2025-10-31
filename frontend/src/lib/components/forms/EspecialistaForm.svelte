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
		cargo: especialista?.cargo || ''
	};

	let errors = {};

	function validateForm() {
		errors = {};

		if (!formData.dni) errors.dni = 'DNI es requerido';
		if (!formData.nombres) errors.nombres = 'Nombres son requeridos';
		if (!formData.apellidos) errors.apellidos = 'Apellidos son requeridos';
		if (!formData.especialidad) errors.especialidad = 'Especialidad es requerida';
		if (!formData.colegiatura) errors.colegiatura = 'Colegiatura es requerida';
		if (!formData.telefono) errors.telefono = 'Teléfono es requerido';
		if (!formData.correo) errors.correo = 'Correo es requerido';
		else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
			errors.correo = 'Correo inválido';
		}
		if (!formData.cargo) errors.cargo = 'Cargo es requerido';

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
				bind:value={formData.dni}
				maxlength="12"
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
				bind:value={formData.nombres}
				maxlength="80"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.nombres}
				disabled={isLoading}
			/>
			{#if errors.nombres}
				<p class="text-red-500 text-sm mt-1">{errors.nombres}</p>
			{/if}
		</div>
	</div>

	<!-- Apellidos y Especialidad -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="apellidos" class="block text-sm font-medium text-gray-700 mb-1">
				Apellidos <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="apellidos"
				bind:value={formData.apellidos}
				maxlength="80"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.apellidos}
				disabled={isLoading}
			/>
			{#if errors.apellidos}
				<p class="text-red-500 text-sm mt-1">{errors.apellidos}</p>
			{/if}
		</div>

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
				bind:value={formData.telefono}
				maxlength="20"
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
