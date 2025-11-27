<script>
	let { historia = null, onSubmit = () => {}, isLoading = false, submitLabel = 'Guardar', isNew = false } = $props();

	// Función para parsear hábitos personales (acepta string o objeto)
	function parseHabitos(habitos) {
		const defaultHabitos = {
			alcohol: '',
			alcohol_frecuencia: '',
			tabaco: '',
			tabaco_frecuencia: '',
			drogas: '',
			drogas_frecuencia: '',
			sueño_horas: '',
			sueño_calidad: '',
			alimentacion: '',
			ejercicio: '',
			otros: ''
		};

		if (!habitos) return defaultHabitos;

		// Si ya es un objeto (JSONB), retornarlo directamente
		if (typeof habitos === 'object') {
			return { ...defaultHabitos, ...habitos };
		}

		// Si es string (datos antiguos), parsear
		if (typeof habitos === 'string') {
			try {
				return { ...defaultHabitos, ...JSON.parse(habitos) };
			} catch {
				return defaultHabitos;
			}
		}

		return defaultHabitos;
	}

	// Función para parsear antecedentes familiares (acepta string o objeto)
	function parseAntecedentesFamiliares(antecedentes) {
		const defaultAntecedentes = {
			depresion: false,
			ansiedad: false,
			bipolaridad: false,
			esquizofrenia: false,
			tdah: false,
			toc: false,
			adicciones: false,
			suicidio: false,
			otros: ''
		};

		if (!antecedentes) return defaultAntecedentes;

		// Si ya es un objeto (JSONB), retornarlo directamente
		if (typeof antecedentes === 'object') {
			return { ...defaultAntecedentes, ...antecedentes };
		}

		// Si es string (datos antiguos), parsear
		if (typeof antecedentes === 'string') {
			try {
				return { ...defaultAntecedentes, ...JSON.parse(antecedentes) };
			} catch {
				return defaultAntecedentes;
			}
		}

		return defaultAntecedentes;
	}

	// Datos del formulario
	let formData = $state({
		id_paciente: historia?.id_paciente || null,
		servicio_origen: historia?.servicio_origen || '',
		antecedentes_personales: historia?.antecedentes_personales || '',
		antecedentes_psicosociales: historia?.antecedentes_psicosociales || '',
		situacion_familiar: historia?.situacion_familiar || '',
		situacion_laboral: historia?.situacion_laboral || '',
		evaluacion_inicial: historia?.evaluacion_inicial || '',
		diagnostico_inicial: historia?.diagnostico_inicial || '',
		tratamientos_previos: historia?.tratamientos_previos || ''
	});

	// Hábitos personales como objeto separado
	let habitosPersonales = $state(parseHabitos(historia?.habitos_personales));

	// Antecedentes familiares como objeto separado
	let antecedentesFamiliares = $state(parseAntecedentesFamiliares(historia?.antecedentes_familiares));

	// Estado para búsqueda de paciente
	let dniSearch = $state('');
	let pacienteEncontrado = $state(null);
	let searchError = $state('');
	let isSearching = $state(false);

	let errors = $state({});

	async function buscarPaciente() {
		if (!dniSearch || dniSearch.length < 8) {
			searchError = 'Ingrese un DNI válido (mínimo 8 dígitos)';
			return;
		}

		try {
			isSearching = true;
			searchError = '';
			pacienteEncontrado = null;

			const response = await fetch(`/api/pacientes/buscar-dni/${dniSearch}`);
			const result = await response.json();

			if (result.success) {
				if (result.data.tiene_historia_activa) {
					searchError = 'Este paciente ya tiene una historia clínica activa';
					pacienteEncontrado = null;
				} else {
					pacienteEncontrado = result.data.paciente;
					// Convertir explícitamente a número para asegurar que Zod lo valide correctamente
					formData.id_paciente = Number(pacienteEncontrado.id_paciente);
					searchError = '';
				}
			} else {
				searchError = result.error || 'Paciente no encontrado';
				pacienteEncontrado = null;
			}
		} catch (err) {
			searchError = 'Error al buscar paciente';
			console.error(err);
		} finally {
			isSearching = false;
		}
	}

	function validateForm() {
		errors = {};

		if (!formData.id_paciente) {
			errors.paciente = 'Debe buscar y seleccionar un paciente';
		}

		return Object.keys(errors).length === 0;
	}

	function handleSubmit(e) {
		e.preventDefault();
		if (validateForm()) {
			// Enviar hábitos personales y antecedentes familiares como objetos
			// PostgreSQL JSONB los almacenará correctamente
			const dataToSubmit = {
				...formData,
				habitos_personales: habitosPersonales,
				antecedentes_familiares: antecedentesFamiliares
			};
			onSubmit(dataToSubmit);
		}
	}
</script>

{#if isNew}
	<!-- Búsqueda de Paciente -->
	<div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
		<h3 class="text-lg font-semibold text-gray-900 mb-4">1. Buscar Paciente</h3>

		<div class="flex gap-4">
			<div class="flex-1">
				<label for="dni-search" class="block text-sm font-medium text-gray-700 mb-1">
					DNI del Paciente <span class="text-red-500">*</span>
				</label>
				<input
					type="text"
					id="dni-search"
					bind:value={dniSearch}
					disabled={isSearching || !!pacienteEncontrado}
					placeholder="Ingrese DNI"
					class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
					maxlength="12"
				/>
			</div>
			<div class="flex items-end">
				<button
					type="button"
					onclick={buscarPaciente}
					disabled={isSearching || !!pacienteEncontrado}
					class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if isSearching}
						Buscando...
					{:else}
						Buscar
					{/if}
				</button>
			</div>
		</div>

		{#if searchError}
			<p class="mt-2 text-sm text-red-600">{searchError}</p>
		{/if}

		{#if pacienteEncontrado}
			<div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
				<div class="flex items-start justify-between">
					<div>
						<p class="font-semibold text-gray-900">Paciente Encontrado:</p>
						<p class="text-gray-700">{pacienteEncontrado.nombres} {pacienteEncontrado.apellidos}</p>
						<p class="text-sm text-gray-600">DNI: {pacienteEncontrado.dni}</p>
						<p class="text-sm text-gray-600">Correo: {pacienteEncontrado.correo || 'N/A'}</p>
						<p class="text-sm text-gray-600">Teléfono: {pacienteEncontrado.telefono || 'N/A'}</p>
					</div>
					<button
						type="button"
						onclick={() => {
							pacienteEncontrado = null;
							formData.id_paciente = null;
							dniSearch = '';
						}}
						class="text-sm text-red-600 hover:text-red-800"
					>
						Cambiar paciente
					</button>
				</div>
			</div>
		{/if}

		{#if errors.paciente}
			<p class="mt-2 text-sm text-red-600">{errors.paciente}</p>
		{/if}
	</div>
{/if}

<form onsubmit={(e) => { e.preventDefault(); handleSubmit(e); }} class="space-y-6">
	<div class="bg-white rounded-lg p-6 border border-gray-200">
		<h3 class="text-lg font-semibold text-gray-900 mb-4">
			{isNew ? '2. Información de la Historia Clínica' : 'Información de la Historia Clínica'}
		</h3>

		<!-- Servicio de Origen -->
		<div class="mb-4">
			<label for="servicio_origen" class="block text-sm font-medium text-gray-700 mb-1">
				Servicio de Origen
			</label>
			<input
				type="text"
				id="servicio_origen"
				bind:value={formData.servicio_origen}
				placeholder="Ej: Consulta Externa, Emergencia"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
				maxlength="100"
			/>
		</div>

		<!-- Antecedentes Personales -->
		<div class="mb-4">
			<label for="antecedentes_personales" class="block text-sm font-medium text-gray-700 mb-1">
				Antecedentes Personales
			</label>
			<textarea
				id="antecedentes_personales"
				bind:value={formData.antecedentes_personales}
				rows="3"
				placeholder="Describa los antecedentes médicos personales del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Antecedentes Familiares - MEJORADO CON CHECKBOXES -->
		<div class="mb-4">
			<div class="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
				<h4 class="text-md font-semibold text-gray-900 mb-4">Antecedentes Familiares de Salud Mental</h4>
				<p class="text-sm text-gray-600 mb-4">Seleccione si algún familiar ha sido diagnosticado con alguna de estas condiciones:</p>

				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					<!-- Depresión -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.depresion}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Depresión</span>
						</label>
					</div>

					<!-- Ansiedad -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.ansiedad}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Ansiedad</span>
						</label>
					</div>

					<!-- Bipolaridad -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.bipolaridad}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Trastorno Bipolar</span>
						</label>
					</div>

					<!-- Esquizofrenia -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.esquizofrenia}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Esquizofrenia</span>
						</label>
					</div>

					<!-- TDAH -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.tdah}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">TDAH</span>
						</label>
					</div>

					<!-- TOC -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.toc}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">TOC</span>
						</label>
					</div>

					<!-- Adicciones -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.adicciones}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Adicciones</span>
						</label>
					</div>

					<!-- Suicidio -->
					<div class="bg-white p-3 rounded-lg border border-gray-200">
						<label class="flex items-center cursor-pointer">
							<input
								type="checkbox"
								bind:checked={antecedentesFamiliares.suicidio}
								class="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<span class="text-sm font-medium text-gray-700">Intento de Suicidio</span>
						</label>
					</div>
				</div>

				<!-- Otros antecedentes -->
				<div class="mt-4">
					<label for="otros_antecedentes" class="block text-sm font-medium text-gray-700 mb-1">
						Otros Antecedentes o Detalles
					</label>
					<textarea
						id="otros_antecedentes"
						bind:value={antecedentesFamiliares.otros}
						rows="2"
						placeholder="Especifique otros antecedentes familiares o detalles adicionales..."
						class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					></textarea>
				</div>
			</div>
		</div>

		<!-- Antecedentes Psicosociales -->
		<div class="mb-4">
			<label for="antecedentes_psicosociales" class="block text-sm font-medium text-gray-700 mb-1">
				Antecedentes Psicosociales
			</label>
			<textarea
				id="antecedentes_psicosociales"
				bind:value={formData.antecedentes_psicosociales}
				rows="3"
				placeholder="Describa el contexto psicosocial del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Hábitos Personales - MEJORADO CON CONTROLES VISUALES -->
		<div class="mb-4">
			<div class="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
				<h4 class="text-md font-semibold text-gray-900 mb-4">Hábitos Personales</h4>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- Alcohol -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Consumo de Alcohol</label>
						<div class="space-y-2">
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.alcohol}
									value="No"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">No consume</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.alcohol}
									value="Ocasional"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Ocasional</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.alcohol}
									value="Frecuente"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Frecuente</span>
							</label>
						</div>
						{#if habitosPersonales.alcohol && habitosPersonales.alcohol !== 'No'}
							<div class="mt-3">
								<label class="block text-xs text-gray-600 mb-1">Frecuencia</label>
								<select
									bind:value={habitosPersonales.alcohol_frecuencia}
									class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								>
									<option value="">Seleccione...</option>
									<option value="1-2 veces/mes">1-2 veces por mes</option>
									<option value="1-2 veces/semana">1-2 veces por semana</option>
									<option value="3-4 veces/semana">3-4 veces por semana</option>
									<option value="Diario">Diario</option>
								</select>
							</div>
						{/if}
					</div>

					<!-- Tabaco -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Consumo de Tabaco</label>
						<div class="space-y-2">
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.tabaco}
									value="No"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">No fuma</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.tabaco}
									value="Ex-fumador"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Ex-fumador</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.tabaco}
									value="Fumador"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Fumador</span>
							</label>
						</div>
						{#if habitosPersonales.tabaco === 'Fumador' || habitosPersonales.tabaco === 'Ex-fumador'}
							<div class="mt-3">
								<label class="block text-xs text-gray-600 mb-1">Frecuencia/Cantidad</label>
								<select
									bind:value={habitosPersonales.tabaco_frecuencia}
									class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								>
									<option value="">Seleccione...</option>
									<option value="Menos de 5 cigarrillos/día">Menos de 5 cigarrillos/día</option>
									<option value="5-10 cigarrillos/día">5-10 cigarrillos/día</option>
									<option value="11-20 cigarrillos/día">11-20 cigarrillos/día</option>
									<option value="Más de 20 cigarrillos/día">Más de 20 cigarrillos/día</option>
								</select>
							</div>
						{/if}
					</div>

					<!-- Drogas -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Consumo de Drogas</label>
						<div class="space-y-2">
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.drogas}
									value="No"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">No consume</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.drogas}
									value="Ocasional"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Ocasional</span>
							</label>
							<label class="flex items-center">
								<input
									type="radio"
									bind:group={habitosPersonales.drogas}
									value="Frecuente"
									class="mr-2 text-purple-600 focus:ring-purple-500"
								/>
								<span class="text-sm">Frecuente</span>
							</label>
						</div>
						{#if habitosPersonales.drogas && habitosPersonales.drogas !== 'No'}
							<div class="mt-3">
								<label class="block text-xs text-gray-600 mb-1">Especificar</label>
								<input
									type="text"
									bind:value={habitosPersonales.drogas_frecuencia}
									placeholder="Tipo y frecuencia"
									class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								/>
							</div>
						{/if}
					</div>

					<!-- Sueño -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Patrón de Sueño</label>
						<div class="space-y-3">
							<div>
								<label class="block text-xs text-gray-600 mb-1">Horas de sueño</label>
								<select
									bind:value={habitosPersonales.sueño_horas}
									class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								>
									<option value="">Seleccione...</option>
									<option value="Menos de 4h">Menos de 4 horas</option>
									<option value="4-5h">4-5 horas</option>
									<option value="6-7h">6-7 horas</option>
									<option value="8-9h">8-9 horas</option>
									<option value="Más de 9h">Más de 9 horas</option>
								</select>
							</div>
							<div>
								<label class="block text-xs text-gray-600 mb-1">Calidad del sueño</label>
								<select
									bind:value={habitosPersonales.sueño_calidad}
									class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
								>
									<option value="">Seleccione...</option>
									<option value="Buena">Buena</option>
									<option value="Regular">Regular</option>
									<option value="Mala">Mala</option>
									<option value="Muy mala">Muy mala</option>
								</select>
							</div>
						</div>
					</div>

					<!-- Alimentación -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Alimentación</label>
						<select
							bind:value={habitosPersonales.alimentacion}
							class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
						>
							<option value="">Seleccione...</option>
							<option value="Adecuada">Adecuada y balanceada</option>
							<option value="Regular">Regular</option>
							<option value="Deficiente">Deficiente</option>
							<option value="Excesiva">Excesiva</option>
						</select>
					</div>

					<!-- Ejercicio -->
					<div class="bg-white p-4 rounded-lg border border-gray-200">
						<label class="block text-sm font-medium text-gray-700 mb-2">Actividad Física</label>
						<select
							bind:value={habitosPersonales.ejercicio}
							class="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
						>
							<option value="">Seleccione...</option>
							<option value="No realiza">No realiza ejercicio</option>
							<option value="1 vez/semana">1 vez por semana</option>
							<option value="2-3 veces/semana">2-3 veces por semana</option>
							<option value="4-5 veces/semana">4-5 veces por semana</option>
							<option value="Diario">Diario</option>
						</select>
					</div>
				</div>

				<!-- Otros hábitos -->
				<div class="mt-4">
					<label for="otros_habitos" class="block text-sm font-medium text-gray-700 mb-1">
						Otros Hábitos (opcional)
					</label>
					<textarea
						id="otros_habitos"
						bind:value={habitosPersonales.otros}
						rows="2"
						placeholder="Otros hábitos relevantes..."
						class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
					></textarea>
				</div>
			</div>
		</div>

		<!-- Situación Familiar -->
		<div class="mb-4">
			<label for="situacion_familiar" class="block text-sm font-medium text-gray-700 mb-1">
				Situación Familiar
			</label>
			<textarea
				id="situacion_familiar"
				bind:value={formData.situacion_familiar}
				rows="3"
				placeholder="Describa la situación familiar del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Situación Laboral -->
		<div class="mb-4">
			<label for="situacion_laboral" class="block text-sm font-medium text-gray-700 mb-1">
				Situación Laboral
			</label>
			<textarea
				id="situacion_laboral"
				bind:value={formData.situacion_laboral}
				rows="3"
				placeholder="Describa la situación laboral del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Evaluación Inicial -->
		<div class="mb-4">
			<label for="evaluacion_inicial" class="block text-sm font-medium text-gray-700 mb-1">
				Evaluación Inicial
			</label>
			<textarea
				id="evaluacion_inicial"
				bind:value={formData.evaluacion_inicial}
				rows="4"
				placeholder="Describa la evaluación inicial del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Diagnóstico Inicial -->
		<div class="mb-4">
			<label for="diagnostico_inicial" class="block text-sm font-medium text-gray-700 mb-1">
				Diagnóstico Inicial
			</label>
			<textarea
				id="diagnostico_inicial"
				bind:value={formData.diagnostico_inicial}
				rows="3"
				placeholder="Ingrese el diagnóstico inicial"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>

		<!-- Tratamientos Previos -->
		<div class="mb-4">
			<label for="tratamientos_previos" class="block text-sm font-medium text-gray-700 mb-1">
				Tratamientos Previos
			</label>
			<textarea
				id="tratamientos_previos"
				bind:value={formData.tratamientos_previos}
				rows="3"
				placeholder="Describa los tratamientos previos del paciente"
				class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
			></textarea>
		</div>
	</div>

	<!-- Submit Button -->
	<div class="flex justify-end gap-3">
		<button
			type="submit"
			disabled={isLoading}
			class="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{isLoading ? 'Guardando...' : submitLabel}
		</button>
	</div>
</form>
