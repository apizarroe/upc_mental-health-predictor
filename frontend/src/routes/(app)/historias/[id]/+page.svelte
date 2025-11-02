<script>
	import { goto } from '$app/navigation';
	import HistoriaClinicaForm from '$lib/components/forms/HistoriaClinicaForm.svelte';

	let { data } = $props();

	let isLoading = $state(false);
	let error = $state(null);
	let isEditing = $state(false);
	let successMessage = $state(null);

	let historia = $derived(data.historia);
	let medicaciones = $state(data.medicaciones || []);

	// Parsear hábitos personales
	let habitosPersonales = $derived.by(() => {
		if (!historia.habitos_personales) return null;
		try {
			return JSON.parse(historia.habitos_personales);
		} catch {
			return null;
		}
	});

	// Parsear antecedentes familiares
	let antecedentesFamiliares = $derived.by(() => {
		if (!historia.antecedentes_familiares) return null;
		try {
			return JSON.parse(historia.antecedentes_familiares);
		} catch {
			return null;
		}
	});

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;
			successMessage = null;

			const response = await fetch(`/api/historias/${historia.id_historia}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				successMessage = 'Historia clínica actualizada exitosamente';
				isEditing = false;
				// Recargar la página para obtener datos actualizados
				setTimeout(() => window.location.reload(), 1500);
			} else {
				error = result.error || 'Error al actualizar historia clínica';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}

	async function handleCerrarHistoria() {
		const motivo = prompt('Ingrese el motivo de cierre de la historia clínica:');
		if (!motivo || motivo.trim() === '') {
			alert('Debe ingresar un motivo para cerrar la historia clínica');
			return;
		}

		if (!confirm('¿Está seguro de cerrar esta historia clínica? Esta acción no se puede deshacer.')) {
			return;
		}

		try {
			const response = await fetch(`/api/historias/${historia.id_historia}/cerrar`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ motivo_cierre: motivo })
			});

			const result = await response.json();

			if (result.success) {
				alert('Historia clínica cerrada exitosamente');
				window.location.reload();
			} else {
				alert('Error al cerrar historia clínica: ' + result.error);
			}
		} catch (err) {
			alert('Error de conexión al cerrar historia clínica');
			console.error(err);
		}
	}

	function formatDate(dateString) {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);
		return date.toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function calcularEdad(fechaNacimiento) {
		if (!fechaNacimiento) return 'N/A';
		const hoy = new Date();
		const nacimiento = new Date(fechaNacimiento);
		let edad = hoy.getFullYear() - nacimiento.getFullYear();
		const mes = hoy.getMonth() - nacimiento.getMonth();
		if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
			edad--;
		}
		return edad;
	}
</script>

<svelte:head>
	<title>{historia.paciente_nombres} {historia.paciente_apellidos} - Historia Clínica</title>
</svelte:head>

<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<button
			onclick={() => goto('/historias')}
			class="text-white hover:text-white/80 mb-4 inline-flex items-center"
		>
			← Volver a la lista
		</button>
		<div class="flex justify-between items-start">
			<div>
				<h1 class="text-3xl font-bold text-white">
					Historia Clínica
				</h1>
				<p class="mt-2 text-white/80">
					{historia.paciente_nombres} {historia.paciente_apellidos}
				</p>
			</div>
			<div class="flex gap-2">
				{#if historia.situacion_historia !== 'Cerrada'}
					<button
						onclick={() => (isEditing = !isEditing)}
						class="px-4 py-2 bg-white text-purple-600 rounded-md hover:bg-gray-50 font-semibold"
					>
						{isEditing ? 'Cancelar Edición' : 'Editar'}
					</button>
					<button
						onclick={handleCerrarHistoria}
						class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-semibold"
					>
						Cerrar Historia
					</button>
				{:else}
					<span class="px-4 py-2 bg-gray-100 text-gray-800 rounded-md font-semibold">
						Historia Cerrada
					</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- Success Message -->
	{#if successMessage}
		<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
			<p class="text-green-800">{successMessage}</p>
		</div>
	{/if}

	<!-- Error Message -->
	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
			<p class="text-red-800">{error}</p>
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Left Column: Patient Info -->
		<div class="lg:col-span-1 space-y-6">
			<!-- Información del Paciente -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Información del Paciente</h2>
				<div class="space-y-3">
					<div>
						<p class="text-sm text-gray-600">Nombre Completo</p>
						<p class="font-medium">{historia.paciente_nombres} {historia.paciente_apellidos}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">DNI</p>
						<p class="font-medium">{historia.paciente_dni}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Edad</p>
						<p class="font-medium">{calcularEdad(historia.paciente_fecha_nacimiento)} años</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Sexo</p>
						<p class="font-medium">{historia.paciente_sexo === 'M' ? 'Masculino' : 'Femenino'}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Teléfono</p>
						<p class="font-medium">{historia.paciente_telefono || 'N/A'}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Correo</p>
						<p class="font-medium text-sm">{historia.paciente_correo || 'N/A'}</p>
					</div>
				</div>
			</div>

			<!-- Información de la Historia -->
			<div class="bg-white rounded-xl shadow-lg p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Información de la Historia</h2>
				<div class="space-y-3">
					<div>
						<p class="text-sm text-gray-600">ID Historia</p>
						<p class="font-medium">#{historia.id_historia}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Fecha Apertura</p>
						<p class="font-medium text-sm">{formatDate(historia.fecha_apertura)}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Especialista Apertura</p>
						<p class="font-medium">{historia.especialista_nombres} {historia.especialista_apellidos}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Estado</p>
						<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {historia.situacion_historia === 'Cerrada' ? 'bg-gray-100 text-gray-800' : 'bg-green-100 text-green-800'}">
							{historia.situacion_historia || 'Abierta'}
						</span>
					</div>
					{#if historia.fecha_cierre}
						<div>
							<p class="text-sm text-gray-600">Fecha Cierre</p>
							<p class="font-medium text-sm">{formatDate(historia.fecha_cierre)}</p>
						</div>
						<div>
							<p class="text-sm text-gray-600">Motivo Cierre</p>
							<p class="text-sm">{historia.motivo_cierre}</p>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Right Column: Clinical Info -->
		<div class="lg:col-span-2">
			{#if isEditing}
				<!-- Edit Mode -->
				<div class="bg-white rounded-xl shadow-lg p-6">
					<HistoriaClinicaForm
						historia={historia}
						onSubmit={handleSubmit}
						isLoading={isLoading}
						submitLabel="Guardar Cambios"
						isNew={false}
					/>
				</div>
			{:else}
				<!-- View Mode -->
				<div class="space-y-6">
					<!-- Servicio de Origen -->
					{#if historia.servicio_origen}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Servicio de Origen</h3>
							<p class="text-gray-700">{historia.servicio_origen}</p>
						</div>
					{/if}

					<!-- Evaluación Inicial -->
					{#if historia.evaluacion_inicial}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Evaluación Inicial</h3>
							<p class="text-gray-700 whitespace-pre-wrap">{historia.evaluacion_inicial}</p>
						</div>
					{/if}

					<!-- Diagnóstico Inicial -->
					{#if historia.diagnostico_inicial}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Diagnóstico Inicial</h3>
							<p class="text-gray-700 whitespace-pre-wrap">{historia.diagnostico_inicial}</p>
						</div>
					{/if}

					<!-- Antecedentes Personales -->
					{#if historia.antecedentes_personales}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Antecedentes Personales</h3>
							<p class="text-gray-700 text-sm whitespace-pre-wrap">{historia.antecedentes_personales}</p>
						</div>
					{/if}

					<!-- Antecedentes Familiares -->
					{#if antecedentesFamiliares}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-4">Antecedentes Familiares de Salud Mental</h3>

							{#if antecedentesFamiliares.depresion || antecedentesFamiliares.ansiedad || antecedentesFamiliares.bipolaridad || antecedentesFamiliares.esquizofrenia || antecedentesFamiliares.tdah || antecedentesFamiliares.toc || antecedentesFamiliares.adicciones || antecedentesFamiliares.suicidio}
								<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
									{#if antecedentesFamiliares.depresion}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Depresión</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.ansiedad}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Ansiedad</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.bipolaridad}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Trastorno Bipolar</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.esquizofrenia}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Esquizofrenia</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.tdah}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">TDAH</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.toc}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">TOC</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.adicciones}
										<div class="flex items-center p-2 bg-blue-50 border border-blue-200 rounded-lg">
											<svg class="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Adicciones</span>
										</div>
									{/if}
									{#if antecedentesFamiliares.suicidio}
										<div class="flex items-center p-2 bg-red-50 border border-red-200 rounded-lg">
											<svg class="w-4 h-4 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-800">Intento de Suicidio</span>
										</div>
									{/if}
								</div>
							{:else}
								<p class="text-sm text-gray-600 mb-4">No se reportan antecedentes familiares de salud mental</p>
							{/if}

							{#if antecedentesFamiliares.otros}
								<div class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
									<h4 class="font-medium text-gray-900 text-sm mb-1">Detalles Adicionales</h4>
									<p class="text-sm text-gray-700">{antecedentesFamiliares.otros}</p>
								</div>
							{/if}
						</div>
					{/if}

					<!-- Antecedentes Psicosociales -->
					{#if historia.antecedentes_psicosociales}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Antecedentes Psicosociales</h3>
							<p class="text-gray-700 text-sm whitespace-pre-wrap">{historia.antecedentes_psicosociales}</p>
						</div>
					{/if}

					<!-- Hábitos Personales -->
					{#if habitosPersonales}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-4">Hábitos Personales</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<!-- Alcohol -->
								{#if habitosPersonales.alcohol}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Consumo de Alcohol</h4>
										<p class="text-gray-700">
											<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {habitosPersonales.alcohol === 'No' ? 'bg-green-100 text-green-800' : habitosPersonales.alcohol === 'Ocasional' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
												{habitosPersonales.alcohol}
											</span>
										</p>
										{#if habitosPersonales.alcohol_frecuencia}
											<p class="text-sm text-gray-600 mt-1">Frecuencia: {habitosPersonales.alcohol_frecuencia}</p>
										{/if}
									</div>
								{/if}

								<!-- Tabaco -->
								{#if habitosPersonales.tabaco}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Consumo de Tabaco</h4>
										<p class="text-gray-700">
											<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {habitosPersonales.tabaco === 'No' ? 'bg-green-100 text-green-800' : habitosPersonales.tabaco === 'Ex-fumador' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}">
												{habitosPersonales.tabaco}
											</span>
										</p>
										{#if habitosPersonales.tabaco_frecuencia}
											<p class="text-sm text-gray-600 mt-1">{habitosPersonales.tabaco_frecuencia}</p>
										{/if}
									</div>
								{/if}

								<!-- Drogas -->
								{#if habitosPersonales.drogas}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Consumo de Drogas</h4>
										<p class="text-gray-700">
											<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {habitosPersonales.drogas === 'No' ? 'bg-green-100 text-green-800' : habitosPersonales.drogas === 'Ocasional' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
												{habitosPersonales.drogas}
											</span>
										</p>
										{#if habitosPersonales.drogas_frecuencia}
											<p class="text-sm text-gray-600 mt-1">{habitosPersonales.drogas_frecuencia}</p>
										{/if}
									</div>
								{/if}

								<!-- Sueño -->
								{#if habitosPersonales.sueño_horas || habitosPersonales.sueño_calidad}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Patrón de Sueño</h4>
										{#if habitosPersonales.sueño_horas}
											<p class="text-sm text-gray-700">Horas: <span class="font-medium">{habitosPersonales.sueño_horas}</span></p>
										{/if}
										{#if habitosPersonales.sueño_calidad}
											<p class="text-sm text-gray-700 mt-1">
												Calidad:
												<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {habitosPersonales.sueño_calidad === 'Buena' ? 'bg-green-100 text-green-800' : habitosPersonales.sueño_calidad === 'Regular' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
													{habitosPersonales.sueño_calidad}
												</span>
											</p>
										{/if}
									</div>
								{/if}

								<!-- Alimentación -->
								{#if habitosPersonales.alimentacion}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Alimentación</h4>
										<p class="text-gray-700">
											<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {habitosPersonales.alimentacion === 'Adecuada' ? 'bg-green-100 text-green-800' : habitosPersonales.alimentacion === 'Regular' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
												{habitosPersonales.alimentacion}
											</span>
										</p>
									</div>
								{/if}

								<!-- Ejercicio -->
								{#if habitosPersonales.ejercicio}
									<div class="border border-gray-200 rounded-lg p-4 bg-gray-50">
										<h4 class="font-medium text-gray-900 text-sm mb-2">Actividad Física</h4>
										<p class="text-gray-700">
											<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {habitosPersonales.ejercicio === 'No realiza' ? 'bg-red-100 text-red-800' : habitosPersonales.ejercicio.includes('Diario') || habitosPersonales.ejercicio.includes('4-5') ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}">
												{habitosPersonales.ejercicio}
											</span>
										</p>
									</div>
								{/if}
							</div>

							<!-- Otros hábitos -->
							{#if habitosPersonales.otros}
								<div class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
									<h4 class="font-medium text-gray-900 text-sm mb-1">Otros Hábitos</h4>
									<p class="text-sm text-gray-700">{habitosPersonales.otros}</p>
								</div>
							{/if}
						</div>
					{/if}

					<!-- Situación Familiar y Laboral -->
					{#if historia.situacion_familiar || historia.situacion_laboral}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-4">Situación Actual</h3>
							<div class="space-y-4">
								{#if historia.situacion_familiar}
									<div>
										<h4 class="font-medium text-gray-900 mb-2">Situación Familiar</h4>
										<p class="text-gray-700 text-sm whitespace-pre-wrap">{historia.situacion_familiar}</p>
									</div>
								{/if}
								{#if historia.situacion_laboral}
									<div>
										<h4 class="font-medium text-gray-900 mb-2">Situación Laboral</h4>
										<p class="text-gray-700 text-sm whitespace-pre-wrap">{historia.situacion_laboral}</p>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Tratamientos Previos -->
					{#if historia.tratamientos_previos}
						<div class="bg-white rounded-xl shadow-lg p-6">
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Tratamientos Previos</h3>
							<p class="text-gray-700 whitespace-pre-wrap">{historia.tratamientos_previos}</p>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>
