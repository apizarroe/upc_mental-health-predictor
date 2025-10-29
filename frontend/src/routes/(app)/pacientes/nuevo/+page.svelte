<script>
	import { goto } from '$app/navigation';
	import PatientForm from '$lib/components/forms/PatientForm.svelte';

	let isLoading = false;
	let error = null;

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;

			const response = await fetch('/api/pacientes', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				goto('/pacientes');
			} else {
				error = result.error || 'Error al crear paciente';
			}
		} catch (err) {
			error = 'Error de conexión con el servidor';
			console.error(err);
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Nuevo Paciente - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<button
			on:click={() => goto('/pacientes')}
			class="text-blue-600 hover:text-blue-800 mb-4 inline-flex items-center"
		>
			← Volver a la lista
		</button>
		<h1 class="text-3xl font-bold text-gray-900">Nuevo Paciente</h1>
		<p class="mt-2 text-gray-600">Registra un nuevo paciente en el sistema</p>
	</div>

	<!-- Error message -->
	{#if error}
		<div class="mb-6 bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
			{error}
		</div>
	{/if}

	<!-- Formulario -->
	<div class="bg-white shadow-md rounded-lg p-6">
		<PatientForm onSubmit={handleSubmit} {isLoading} submitLabel="Crear Paciente" />
	</div>
</div>
