<script>
	import { goto } from '$app/navigation';

	let { data } = $props();

	let paciente = $derived(data.paciente);
	let tieneHistoria = $derived(data.tieneHistoria);

	function formatDate(dateString) {
		const date = new Date(dateString);
		return date.toLocaleDateString('es-PE', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function calcularEdad(fechaNacimiento) {
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
	<title>{paciente.nombres} {paciente.apellidos} - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Back button -->
	<div class="mb-8">
		<button
			onclick={() => goto('/pacientes')}
			class="text-white/80 hover:text-white mb-4 flex items-center gap-2"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Volver a Pacientes
		</button>
	</div>

	<div class="bg-white shadow-md rounded-lg overflow-hidden">
		<!-- Header dentro de la tarjeta -->
		<div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
			<div class="flex justify-between items-start gap-4">
				<div class="flex-1 min-w-0">
					<h1 class="text-2xl font-bold text-gray-900 break-words">
						{paciente.nombres}
						{paciente.apellidos}
					</h1>
					<p class="mt-1 text-gray-600">Información del paciente (Solo lectura)</p>
				</div>
				<div class="flex-shrink-0 flex items-center gap-2">
					{#if tieneHistoria}
						<span class="inline-flex items-center px-3 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-md">
							<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							Con Historial Clínico
						</span>
					{:else}
						<span class="inline-flex items-center px-3 py-2 text-sm font-medium text-orange-700 bg-orange-100 rounded-md">
							<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
							</svg>
							Sin Historial Clínico
						</span>
					{/if}
				</div>
			</div>
		</div>

		<!-- Modo Vista (Solo lectura) -->
		<div class="p-6">
			<!-- Información Personal -->
			<div class="mb-8">
				<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">Información Personal</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="text-sm font-medium text-gray-500">DNI</label>
						<p class="mt-1 text-gray-900">{paciente.dni}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Fecha de Nacimiento</label>
						<p class="mt-1 text-gray-900">
							{formatDate(paciente.fecha_nacimiento)}
							<span class="text-gray-500">({calcularEdad(paciente.fecha_nacimiento)} años)</span>
						</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Sexo</label>
						<p class="mt-1 text-gray-900">{paciente.sexo === 'M' ? 'Masculino' : 'Femenino'}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Estado</label>
						<p class="mt-1">
							<span
								class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {paciente.flg_activo
									? 'bg-green-100 text-green-800'
									: 'bg-red-100 text-red-800'}"
							>
								{paciente.flg_activo ? 'Activo' : 'Inactivo'}
							</span>
						</p>
					</div>
				</div>
			</div>

			<!-- Información de Contacto -->
			<div class="mb-8">
				<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
					Información de Contacto
				</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="text-sm font-medium text-gray-500">Dirección</label>
						<p class="mt-1 text-gray-900">{paciente.direccion}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Teléfono</label>
						<p class="mt-1 text-gray-900">{paciente.telefono}</p>
					</div>
					<div class="md:col-span-2">
						<label class="text-sm font-medium text-gray-500">Correo Electrónico</label>
						<p class="mt-1 text-gray-900">{paciente.correo}</p>
					</div>
				</div>
			</div>

			<!-- Contacto de Emergencia -->
			<div class="mb-8">
				<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
					Contacto de Emergencia
				</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="text-sm font-medium text-gray-500">Nombre</label>
						<p class="mt-1 text-gray-900">{paciente.contacto_emergencia}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Teléfono</label>
						<p class="mt-1 text-gray-900">{paciente.telefono_emergencia}</p>
					</div>
				</div>
			</div>

			<!-- Información del Sistema -->
			<div>
				<h2 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">
					Información del Sistema
				</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="text-sm font-medium text-gray-500">ID del Paciente</label>
						<p class="mt-1 text-gray-900">{paciente.id_paciente}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Fecha de Registro</label>
						<p class="mt-1 text-gray-900">{formatDate(paciente.fecha_registro)}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Estado Clínico</label>
						<p class="mt-1 text-gray-900">{paciente.estado_clinico ?? '—'}</p>
					</div>
					<div>
						<label class="text-sm font-medium text-gray-500">Fecha de Última Consulta</label>
						<p class="mt-1 text-gray-900">
							{paciente.fecha_ultima_consulta ? formatDate(paciente.fecha_ultima_consulta) : '—'}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
