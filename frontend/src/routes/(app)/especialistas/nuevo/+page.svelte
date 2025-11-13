<script>
	import { goto } from '$app/navigation';
	import EspecialistaForm from '$lib/components/forms/EspecialistaForm.svelte';

	let isLoading = $state(false);
	let error = $state(null);

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;

			const response = await fetch('/api/especialistas', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();

			if (result.success) {
				goto('/especialistas');
			} else {
				error = result.error || 'Error al crear especialista';
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
	<title>Nuevo Especialista - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<button
			onclick={() => goto('/especialistas')}
			class="text-white hover:text-gray-200 mb-4 inline-flex items-center"
		>
			← Volver a la lista
		</button>
		<h1 class="text-3xl font-bold text-white">Nuevo Especialista</h1>
		<p class="mt-2 text-white">Registra un nuevo especialista en el sistema</p>
	</div>

	<!-- Error message -->
	{#if error}
		<div class="mb-6 bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
			{error}
		</div>
	{/if}

	<!-- Formulario -->
	<div class="bg-white shadow-md rounded-lg p-6">
		<EspecialistaForm onSubmit={handleSubmit} {isLoading} submitLabel="Crear Especialista" />
	</div>
</div>
