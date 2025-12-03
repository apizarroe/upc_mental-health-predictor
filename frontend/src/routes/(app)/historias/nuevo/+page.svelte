<script>
	import { goto } from '$app/navigation';
	import HistoriaClinicaForm from '$lib/components/forms/HistoriaClinicaForm.svelte';

	let isLoading = $state(false);
	let error = $state(null);
	let validationErrors = $state([]);

	async function handleSubmit(formData) {
		try {
			isLoading = true;
			error = null;
			validationErrors = [];

			// Log para depuración
			console.log('📤 Enviando datos al servidor:', formData);

			const response = await fetch('/api/historias', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			const result = await response.json();
			console.log('📥 Respuesta del servidor:', result);

			if (result.success) {
				goto(`/historias/${result.data.id_historia}`);
			} else {
				error = result.error || 'Error al crear historia clínica';

				// Si hay detalles de validación de Zod, mostrarlos
				if (result.details && Array.isArray(result.details)) {
					validationErrors = result.details.map(err => ({
						field: err.path.join('.'),
						message: err.message
					}));
				}
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
	<title>Nueva Historia Clínica - Sistema de Salud Mental</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<button
			onclick={() => goto('/historias')}
			class="text-white hover:text-white/80 mb-4 inline-flex items-center"
		>
			← Volver a la lista
		</button>
		<h1 class="text-3xl font-bold text-white">Nueva Historia Clínica</h1>
		<p class="mt-2 text-white/80">Crea una nueva historia clínica para un paciente</p>
	</div>

	<!-- Error message -->
	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
			<div class="flex items-start">
				<svg class="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
				</svg>
				<div class="flex-1">
					<p class="text-red-800 font-semibold">{error}</p>

					{#if validationErrors.length > 0}
						<div class="mt-3">
							<p class="text-sm text-red-700 font-medium mb-2">Errores de validación:</p>
							<ul class="list-disc list-inside space-y-1">
								{#each validationErrors as validationError}
									<li class="text-sm text-red-700">
										<span class="font-medium">{validationError.field}:</span> {validationError.message}
									</li>
								{/each}
							</ul>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}

	<!-- Form -->
	<div class="bg-white rounded-xl shadow-lg p-6">
		<HistoriaClinicaForm
			onSubmit={handleSubmit}
			isLoading={isLoading}
			submitLabel="Crear Historia Clínica"
			isNew={true}
		/>
	</div>
</div>
