<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data, children } = $props();
	let user = $derived(data.user);

	const navigation = [
		{
			name: 'Inicio',
			href: '/paciente/inicio',
			icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
		},
		{
			name: 'Mi Perfil',
			href: '/paciente/perfil',
			icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
		},
		{
			name: 'Notas',
			href: '/paciente/notas',
			icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'
		}
	];

	function isActive(href) {
		return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
	}

	async function handleLogout() {
		try {
			await fetch('/api/auth/logout-paciente', {
				method: 'POST'
			});
			goto('/');
		} catch (error) {
			console.error('Error al cerrar sesión:', error);
			goto('/');
		}
	}

	function getInitials(nombres, apellidos) {
		const n = nombres?.charAt(0) || '';
		const a = apellidos?.charAt(0) || '';
		return (n + a).toUpperCase();
	}
</script>

<svelte:head>
	<title>Portal de Pacientes</title>
</svelte:head>

<div class="min-h-screen flex" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
	<!-- Sidebar -->
	<aside class="w-64 bg-white/95 backdrop-blur-sm flex flex-col" style="box-shadow: 4px 0 20px rgba(102, 126, 234, 0.15);">
		<!-- Logo -->
		<div class="p-6 border-b border-gray-200">
			<div class="flex items-center">
				<div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);">
					<svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
					</svg>
				</div>
				<div class="ml-3">
					<h1 class="text-sm font-bold" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
						Centro de Salud Mental
					</h1>
					<p class="text-xs font-medium text-purple-600">Portal de Pacientes</p>
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
					<span>{item.name}</span>
				</a>
			{/each}
		</nav>

		<!-- User Info & Logout -->
		<div class="p-4 border-t border-gray-200">
			<div class="flex items-center mb-3 px-3 py-2 bg-purple-50 rounded-lg">
				<div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
					{getInitials(user.nombres, user.apellidos)}
				</div>
				<div class="ml-3 flex-1 min-w-0">
					<p class="text-sm font-semibold text-gray-900 truncate">
						{user.nombres} {user.apellidos}
					</p>
					<p class="text-xs text-gray-600 truncate">DNI: {user.dni}</p>
				</div>
			</div>

			<button
				onclick={handleLogout}
				class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-sm font-semibold transition-colors"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
				</svg>
				Cerrar Sesión
			</button>
		</div>
	</aside>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto">
		{@render children()}
	</main>
</div>
