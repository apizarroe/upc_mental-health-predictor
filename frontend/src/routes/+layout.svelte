<script>
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/stores';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

	const navigation = [
		{ name: 'Dashboard', href: '/' },
		{ name: 'Pacientes', href: '/pacientes' },
		{ name: 'Especialistas', href: '/especialistas' },
		{ name: 'Historias Clínicas', href: '/historias' }
	];

	function isActive(href) {
		if (href === '/') return $page.url.pathname === '/';
		return $page.url.pathname.startsWith(href);
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="min-h-screen" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
	<!-- Header/Navbar -->
	<nav class="bg-white/95 backdrop-blur-sm sticky top-0 z-50" style="box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<!-- Logo y nombre -->
				<div class="flex items-center">
					<div class="flex-shrink-0 flex items-center">
						<div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);">
							<svg
								class="w-7 h-7 text-white"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
								/>
							</svg>
						</div>
						<div class="ml-3">
							<h1 class="text-lg font-bold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Centro de Salud Mental</h1>
							<p class="text-xs font-medium" style="color: #667eea;">Sistema de Gestión</p>
						</div>
					</div>
				</div>

				<!-- Desktop Navigation -->
				<div class="hidden md:flex md:items-center md:space-x-2">
					{#each navigation as item}
						<a
							href={item.href}
							class="px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 {isActive(
								item.href
							)
								? 'text-white'
								: 'text-gray-700 hover:text-white'}"
							style={isActive(item.href)
								? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);'
								: ''}
							onmouseenter={(e) => {
								if (!isActive(item.href)) {
									e.currentTarget.style.background = 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)';
								}
							}}
							onmouseleave={(e) => {
								if (!isActive(item.href)) {
									e.currentTarget.style.background = '';
								}
							}}
						>
							{item.name}
						</a>
					{/each}
				</div>

				<!-- User menu / Actions -->
				<div class="hidden md:flex md:items-center gap-2">
					<button
						class="p-2 rounded-lg transition-all duration-300"
						style="color: #667eea;"
						title="Notificaciones"
						onmouseenter={(e) => {
							e.currentTarget.style.background = 'rgba(102, 126, 234, 0.1)';
							e.currentTarget.style.transform = 'scale(1.05)';
						}}
						onmouseleave={(e) => {
							e.currentTarget.style.background = '';
							e.currentTarget.style.transform = 'scale(1)';
						}}
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
							/>
						</svg>
					</button>
					<div class="ml-1 relative flex items-center">
						<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 4px 10px rgba(240, 147, 251, 0.3);">
							U
						</div>
					</div>
				</div>

				<!-- Mobile menu button -->
				<div class="flex items-center md:hidden">
					<button
						onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
						class="inline-flex items-center justify-center p-2 rounded-lg"
						style="color: #667eea;"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							{#if mobileMenuOpen}
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							{:else}
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 6h16M4 12h16M4 18h16"
								/>
							{/if}
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Mobile menu -->
		{#if mobileMenuOpen}
			<div class="md:hidden" style="border-top: 2px solid rgba(102, 126, 234, 0.1);">
				<div class="px-2 pt-2 pb-3 space-y-1">
					{#each navigation as item}
						<a
							href={item.href}
							onclick={() => (mobileMenuOpen = false)}
							class="block px-3 py-2 rounded-lg text-base font-semibold {isActive(item.href)
								? 'text-white'
								: 'text-gray-700'}"
							style={isActive(item.href)
								? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
								: ''}
						>
							{item.name}
						</a>
					{/each}
				</div>
			</div>
		{/if}
	</nav>

	<!-- Main Content -->
	<main class="min-h-[calc(100vh-4rem)]">
		{@render children?.()}
	</main>

	<!-- Footer -->
	<footer class="bg-white/95 backdrop-blur-sm mt-12" style="border-top: 2px solid rgba(102, 126, 234, 0.2);">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex flex-col md:flex-row justify-between items-center">
				<p class="text-sm font-medium" style="color: #667eea;">
					© 2024 Centro de Salud Mental. Todos los derechos reservados.
				</p>
				<p class="text-xs font-medium text-gray-600 mt-2 md:mt-0">
					Sistema de Gestión v1.0 | Universidad Peruana de Ciencias Aplicadas
				</p>
			</div>
		</div>
	</footer>
</div>
