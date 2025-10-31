<script>
	let { patient = null, onSubmit = () => {}, isLoading = false, submitLabel = 'Guardar' } = $props();

	// Función para convertir fecha ISO a formato YYYY-MM-DD para input date
	function formatDateForInput(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	// Datos del formulario
	let formData = {
		dni: patient?.dni || '',
		nombres: patient?.nombres || '',
		apellidos: patient?.apellidos || '',
		fecha_nacimiento: formatDateForInput(patient?.fecha_nacimiento) || '',
		sexo: patient?.sexo || 'M',
		direccion: patient?.direccion || '',
		telefono: patient?.telefono || '',
		correo: patient?.correo || '',
		contacto_emergencia: patient?.contacto_emergencia || '',
		telefono_emergencia: patient?.telefono_emergencia || ''
	};

	let errors = {};

	function validateForm() {
		errors = {};

		if (!formData.dni) errors.dni = 'DNI es requerido';
		if (!formData.nombres) errors.nombres = 'Nombres son requeridos';
		if (!formData.apellidos) errors.apellidos = 'Apellidos son requeridos';
		if (!formData.fecha_nacimiento) errors.fecha_nacimiento = 'Fecha de nacimiento es requerida';
		if (!formData.direccion) errors.direccion = 'Dirección es requerida';
		if (!formData.telefono) errors.telefono = 'Teléfono es requerido';
		if (!formData.correo) errors.correo = 'Correo es requerido';
		else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
			errors.correo = 'Correo inválido';
		}
		if (!formData.contacto_emergencia)
			errors.contacto_emergencia = 'Contacto de emergencia es requerido';
		if (!formData.telefono_emergencia)
			errors.telefono_emergencia = 'Teléfono de emergencia es requerido';

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

	<!-- Apellidos y Fecha de Nacimiento -->
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
			<label for="fecha_nacimiento" class="block text-sm font-medium text-gray-700 mb-1">
				Fecha de Nacimiento <span class="text-red-500">*</span>
			</label>
			<input
				type="date"
				id="fecha_nacimiento"
				bind:value={formData.fecha_nacimiento}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.fecha_nacimiento}
				disabled={isLoading}
			/>
			{#if errors.fecha_nacimiento}
				<p class="text-red-500 text-sm mt-1">{errors.fecha_nacimiento}</p>
			{/if}
		</div>
	</div>

	<!-- Sexo -->
	<div>
		<label for="sexo" class="block text-sm font-medium text-gray-700 mb-1">
			Sexo <span class="text-red-500">*</span>
		</label>
		<select
			id="sexo"
			bind:value={formData.sexo}
			class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			disabled={isLoading}
		>
			<option value="M">Masculino</option>
			<option value="F">Femenino</option>
		</select>
	</div>

	<!-- Dirección -->
	<div>
		<label for="direccion" class="block text-sm font-medium text-gray-700 mb-1">
			Dirección <span class="text-red-500">*</span>
		</label>
		<input
			type="text"
			id="direccion"
			bind:value={formData.direccion}
			maxlength="255"
			class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
			class:border-red-500={errors.direccion}
			disabled={isLoading}
		/>
		{#if errors.direccion}
			<p class="text-red-500 text-sm mt-1">{errors.direccion}</p>
		{/if}
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

	<!-- Contacto de Emergencia -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="contacto_emergencia" class="block text-sm font-medium text-gray-700 mb-1">
				Contacto de Emergencia <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="contacto_emergencia"
				bind:value={formData.contacto_emergencia}
				maxlength="150"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.contacto_emergencia}
				disabled={isLoading}
			/>
			{#if errors.contacto_emergencia}
				<p class="text-red-500 text-sm mt-1">{errors.contacto_emergencia}</p>
			{/if}
		</div>

		<div>
			<label for="telefono_emergencia" class="block text-sm font-medium text-gray-700 mb-1">
				Teléfono de Emergencia <span class="text-red-500">*</span>
			</label>
			<input
				type="tel"
				id="telefono_emergencia"
				bind:value={formData.telefono_emergencia}
				maxlength="20"
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				class:border-red-500={errors.telefono_emergencia}
				disabled={isLoading}
			/>
			{#if errors.telefono_emergencia}
				<p class="text-red-500 text-sm mt-1">{errors.telefono_emergencia}</p>
			{/if}
		</div>
	</div>

	<!-- Botón Submit -->
	<div class="flex justify-end">
		<button
			type="submit"
			disabled={isLoading}
			class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{#if isLoading}
				Guardando...
			{:else}
				{submitLabel}
			{/if}
		</button>
	</div>
</form>
