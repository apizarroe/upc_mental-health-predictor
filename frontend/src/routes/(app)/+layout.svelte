<script>
	import '../../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data, children } = $props();
	let mobileMenuOpen = $state(false);
	let userMenuOpen = $state(false);

	let user = $derived(data.user);

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

	async function handleLogout() {
		try {
			const response = await fetch('/api/auth/logout', {
				method: 'POST'
			});

			if (response.ok) {
				goto('/login');
			}
		} catch (error) {
			console.error('Error al cerrar sesión:', error);
		}
	}

	function getInitials(nombres, apellidos) {
		const n = nombres?.charAt(0) || '';
		const a = apellidos?.charAt(0) || '';
		return (n + a).toUpperCase();
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
							<svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
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
							class="px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-300 {isActive(item.href) ? 'text-white' : 'text-gray-700 hover:text-white'}"
							style={isActive(item.href) ? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);' : ''}
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

				<!-- User menu -->
				<div class="hidden md:flex md:items-center gap-2">
					<div class="relative">
						<button
							onclick={() => (userMenuOpen = !userMenuOpen)}
							class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-300 hover:bg-purple-50"
						>
							<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 4px 10px rgba(240, 147, 251, 0.3);">
								{getInitials(user.nombres, user.apellidos)}
							</div>
							<div class="text-left">
								<p class="text-sm font-semibold text-gray-900">{user.nombres} {user.apellidos}</p>
								<p class="text-xs text-gray-500 capitalize">{user.rol}</p>
							</div>
							<svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>

						{#if userMenuOpen}
							<div class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl py-1 z-50">
								<div class="px-4 py-3 border-b border-gray-100">
									<p class="text-sm font-medium text-gray-900">{user.nombres} {user.apellidos}</p>
									<p class="text-xs text-gray-500">{user.correo}</p>
								</div>
								<button
									onclick={handleLogout}
									class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
								>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
									</svg>
									Cerrar Sesión
								</button>
							</div>
						{/if}
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
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							{:else}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
							{/if}
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Mobile Menu -->
		{#if mobileMenuOpen}
			<div class="md:hidden border-t border-gray-200">
				<div class="px-2 pt-2 pb-3 space-y-1">
					{#each navigation as item}
						<a
							href={item.href}
							class="block px-3 py-2 rounded-md text-base font-medium {isActive(item.href) ? 'text-white' : 'text-gray-700'}"
							style={isActive(item.href) ? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);' : ''}
						>
							{item.name}
						</a>
					{/each}
				</div>
				<div class="pt-4 pb-3 border-t border-gray-200">
					<div class="flex items-center px-5">
						<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
							{getInitials(user.nombres, user.apellidos)}
						</div>
						<div class="ml-3">
							<p class="text-base font-medium text-gray-800">{user.nombres} {user.apellidos}</p>
							<p class="text-sm font-medium text-gray-500">{user.correo}</p>
						</div>
					</div>
					<div class="mt-3 px-2 space-y-1">
						<button
							onclick={handleLogout}
							class="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50"
						>
							Cerrar Sesión
						</button>
					</div>
				</div>
			</div>
		{/if}
	</nav>

	<!-- Main Content -->
	<main>
		{@render children()}
	</main>
</div>