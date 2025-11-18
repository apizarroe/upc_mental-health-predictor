<script>
	import '../../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { canAccessPacientes, canAccessEspecialistas, canAccessHistorias } from '$lib/utils/permissions.js';

	let { data, children } = $props();
	let sidebarOpen = $state(true);
	let userMenuOpen = $state(false);

	let user = $derived(data.user);

	const allNavigation = [
		{ name: 'Inicio', href: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', requiresPermission: null },
		{ name: 'Dashboard', href: '/dashboard', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', requiresPermission: null },
		{ name: 'Pacientes', href: '/pacientes', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', requiresPermission: 'pacientes' },
		{ name: 'Especialistas', href: '/especialistas', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01', requiresPermission: 'especialistas' },
		{ name: 'Historias Clínicas', href: '/historias', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', requiresPermission: 'historias' }
	];

	// Filtrar navegación según permisos del usuario
	const navigation = $derived(allNavigation.filter(item => {
		if (!item.requiresPermission) return true; // Siempre mostrar items sin requerimiento de permisos

		switch (item.requiresPermission) {
			case 'pacientes':
				return canAccessPacientes(user.rol);
			case 'especialistas':
				return canAccessEspecialistas(user.rol);
			case 'historias':
				return canAccessHistorias(user.rol);
			default:
				return true;
		}
	}));

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

<div class="min-h-screen flex" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
	<!-- Sidebar -->
	<aside class="hidden md:flex md:flex-col w-64 bg-white/95 backdrop-blur-sm" style="box-shadow: 4px 0 20px rgba(102, 126, 234, 0.15);">
		<!-- Logo -->
		<div class="p-6 border-b border-gray-200">
			<div class="flex items-center">
				<div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);">
					<svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
					</svg>
				</div>
				<div class="ml-3">
					<h1 class="text-base font-bold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Centro de Salud Mental</h1>
					<p class="text-xs font-medium" style="color: #667eea;">Sistema de Gestión</p>
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 px-4 py-6 space-y-2">
			{#each navigation as item}
				<a
					href={item.href}
					class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-300 {isActive(item.href) ? 'text-white' : 'text-gray-700 hover:bg-purple-50'}"
					style={isActive(item.href) ? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);' : ''}
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
					</svg>
					{item.name}
				</a>
			{/each}
		</nav>

		<!-- User Menu -->
		<div class="p-4 border-t border-gray-200">
			<div class="relative">
				<button
					onclick={() => (userMenuOpen = !userMenuOpen)}
					class="flex items-center gap-3 w-full px-3 py-3 rounded-lg transition-all duration-300 hover:bg-purple-50"
				>
					<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 4px 10px rgba(240, 147, 251, 0.3);">
						{getInitials(user.nombres, user.apellidos)}
					</div>
					<div class="flex-1 text-left">
						<p class="text-sm font-semibold text-gray-900 truncate">{user.nombres}</p>
						<p class="text-xs text-gray-500 capitalize">{user.rol}</p>
					</div>
					<svg class="w-4 h-4 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
					</svg>
				</button>

				{#if userMenuOpen}
					<div class="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-xl py-1 z-50">
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
	</aside>

	<!-- Mobile Header -->
	<div class="md:hidden fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm z-50" style="box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);">
		<div class="flex items-center justify-between p-4">
			<div class="flex items-center">
				<div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
					<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
					</svg>
				</div>
				<h1 class="ml-2 text-sm font-bold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Centro de Salud Mental</h1>
			</div>
			<button
				onclick={() => (sidebarOpen = !sidebarOpen)}
				class="p-2 rounded-lg"
				style="color: #667eea;"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
				</svg>
			</button>
		</div>
	</div>

	<!-- Mobile Sidebar -->
	{#if sidebarOpen}
		<div class="md:hidden fixed inset-0 z-40 bg-black/50" onclick={() => (sidebarOpen = false)}></div>
		<aside class="md:hidden fixed top-0 left-0 bottom-0 w-64 bg-white z-50 transform transition-transform duration-300" style="box-shadow: 4px 0 20px rgba(102, 126, 234, 0.15);">
			<!-- Logo -->
			<div class="p-6 border-b border-gray-200">
				<div class="flex items-center">
					<div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
						<svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
						</svg>
					</div>
					<div class="ml-3">
						<h1 class="text-base font-bold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Centro de Salud Mental</h1>
						<p class="text-xs font-medium" style="color: #667eea;">Sistema de Gestión</p>
					</div>
				</div>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 px-4 py-6 space-y-2">
				{#each navigation as item}
					<a
						href={item.href}
						onclick={() => (sidebarOpen = false)}
						class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-300 {isActive(item.href) ? 'text-white' : 'text-gray-700 hover:bg-purple-50'}"
						style={isActive(item.href) ? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);' : ''}
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
						</svg>
						{item.name}
					</a>
				{/each}
			</nav>

			<!-- User Info -->
			<div class="p-4 border-t border-gray-200">
				<div class="flex items-center gap-3 px-3 py-2">
					<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
						{getInitials(user.nombres, user.apellidos)}
					</div>
					<div class="flex-1">
						<p class="text-sm font-semibold text-gray-900">{user.nombres}</p>
						<p class="text-xs text-gray-500 capitalize">{user.rol}</p>
					</div>
				</div>
				<button
					onclick={handleLogout}
					class="w-full mt-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
					</svg>
					Cerrar Sesión
				</button>
			</div>
		</aside>
	{/if}

	<!-- Main Content -->
	<main class="flex-1 md:ml-0 mt-16 md:mt-0">
		{@render children()}
	</main>
</div>
