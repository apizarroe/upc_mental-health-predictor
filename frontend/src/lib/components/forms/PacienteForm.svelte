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

	// Validación en tiempo real para Teléfono del paciente (solo números, máximo 9 dígitos)
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

	// Validación en tiempo real para Contacto de emergencia (solo letras y espacios)
	function handleContactoEmergenciaInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea letra o espacio
		let cleanValue = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.contacto_emergencia = cleanValue;
	}

	// Validación en tiempo real para Teléfono de emergencia (solo números, máximo 9 dígitos)
	function handleTelefonoEmergenciaInput(event) {
		let value = event.target.value;

		// Remover cualquier caracter que no sea número
		let cleanValue = value.replace(/\D/g, '');

		// Verificar si se intenta superar el límite de 9 caracteres
		if (cleanValue.length > 9) {
			alert('El teléfono de emergencia no puede superar los 9 dígitos');
			cleanValue = cleanValue.slice(0, 9);
		}

		// Actualizar el valor
		event.target.value = cleanValue;
		formData.telefono_emergencia = cleanValue;
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

		if (!formData.fecha_nacimiento) errors.fecha_nacimiento = 'Fecha de nacimiento es requerida';
		if (!formData.direccion) errors.direccion = 'Dirección es requerida';

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

		// Validación de Contacto de emergencia
		if (!formData.contacto_emergencia) {
			errors.contacto_emergencia = 'Contacto de emergencia es requerido';
		} else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(formData.contacto_emergencia)) {
			errors.contacto_emergencia = 'El contacto de emergencia solo puede contener letras y espacios';
		}

		// Validación de Teléfono de emergencia
		if (!formData.telefono_emergencia) {
			errors.telefono_emergencia = 'Teléfono de emergencia es requerido';
		} else if (!/^\d{9}$/.test(formData.telefono_emergencia)) {
			errors.telefono_emergencia = 'El teléfono de emergencia debe tener exactamente 9 dígitos numéricos';
		}

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

	<!-- Apellidos y Fecha de Nacimiento -->
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

	<!-- Contacto de Emergencia -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<div>
			<label for="contacto_emergencia" class="block text-sm font-medium text-gray-700 mb-1">
				Contacto de Emergencia <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="contacto_emergencia"
				value={formData.contacto_emergencia}
				oninput={handleContactoEmergenciaInput}
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
				value={formData.telefono_emergencia}
				oninput={handleTelefonoEmergenciaInput}
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
