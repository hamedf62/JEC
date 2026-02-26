<script lang="ts">
    import '../app.css';
    import * as m from '../paraglide/messages';
    import { getLocale, setLocale } from '../paraglide/runtime';
    import { page } from '$app/state';
    import {
        Wallet,
        Receipt,
        FileText,
        BarChart3,
        Activity,
        Settings,
        Menu,
        LogOut,
        User,
        Languages,
        ChevronLeft,
        ChevronRight,
        Sparkles
    } from 'lucide-svelte';

    let { children } = $props();

    let sidebarOpen = $state(false);

    const menuItems = $derived([
        { name: m.nav_overview(), icon: BarChart3, href: '/' },
        { name: m.nav_cashflow(), icon: Activity, href: '/cashflow' },
        { name: m.nav_invoices(), icon: Receipt, href: '/invoices' },
        { name: m.nav_receivable(), icon: Wallet, href: '/receivable' },
        { name: m.nav_payable(), icon: Wallet, href: '/payable' },
        { name: m.nav_performa(), icon: FileText, href: '/performa' },
        { name: m.nav_settings(), icon: Settings, href: '/settings' }
    ]);

    function toggleLanguage() {
        const newLocale = getLocale() === 'fa' ? 'en' : 'fa';
        setLocale(newLocale);
        document.documentElement.lang = newLocale;
        document.documentElement.dir = newLocale === 'fa' ? 'rtl' : 'ltr';
    }

    function isActive(href: string) {
        return page.url.pathname === href;
    }
</script>

<div class="drawer lg:drawer-open" dir={getLocale() === 'fa' ? 'rtl' : 'ltr'}>
    <input id="dashboard-drawer" type="checkbox" class="drawer-toggle" bind:checked={sidebarOpen} />

    <div class="drawer-content flex flex-col dashboard-shell">
        <div class="navbar border-b border-base-200/80 bg-white/80 px-4 lg:px-6 backdrop-blur-xl">
            <div class="flex-none lg:hidden">
                <label for="dashboard-drawer" class="btn btn-square btn-ghost">
                    <Menu class="h-6 w-6" />
                </label>
            </div>
            <div class="flex-1">
                <div class="flex items-center gap-2">
                    <div class="rounded-xl bg-[color:var(--jec-primary-soft)] p-2 text-[color:var(--jec-primary)]">
                        <Sparkles class="h-4 w-4" />
                    </div>
                    <span class="text-xl font-black tracking-tight text-slate-900">{m.app_title()}</span>
                </div>
            </div>
            <div class="flex-none gap-2">
                <button class="btn btn-ghost gap-2 rounded-xl" onclick={toggleLanguage}>
                    <Languages class="h-4 w-4" />
                    <span class="text-xs uppercase">{getLocale()}</span>
                </button>

                <div class="dropdown dropdown-end">
                    <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
                        <div class="flex w-10 items-center justify-center rounded-full bg-slate-100">
                            <User class="h-5 w-5 text-slate-600" />
                        </div>
                    </div>
                    <ul class="menu dropdown-content z-[1] mt-3 w-52 rounded-box border border-base-200 bg-base-100 p-2 shadow-md">
                        <li><a href="/settings">{m.nav_profile()}</a></li>
                        <li><a href="/settings">{m.nav_settings()}</a></li>
                        <li><a href="/settings">{m.nav_logout()}</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <main class="min-h-[calc(100vh-64px)] overflow-auto p-4 md:p-6 lg:p-8">
            <div class="mx-auto max-w-7xl fade-up">
                {@render children()}
            </div>
        </main>
    </div>

    <div class="drawer-side z-20">
        <label for="dashboard-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
        <div class="flex min-h-full w-72 flex-col border-s border-base-200 bg-white/90 backdrop-blur-xl">
            <div class="hidden items-center gap-3 border-b border-base-200 p-6 lg:flex">
                <div class="grid h-10 w-10 place-items-center rounded-2xl bg-[color:var(--jec-primary)] text-white">
                    <BarChart3 class="h-5 w-5" />
                </div>
                <div>
                    <p class="text-sm text-slate-500">Jahan Electronic</p>
                    <h2 class="text-lg font-black text-slate-900">{m.admin_panel()}</h2>
                </div>
            </div>

            <ul class="menu flex-grow gap-1 p-4">
                <li class="menu-title text-xs font-black uppercase tracking-widest text-slate-400">
                    {m.sidebar_main()}
                </li>
                {#each menuItems as item}
                    <li>
                        <a
                            href={item.href}
                            class={`group flex items-center gap-3 rounded-xl px-4 py-3 transition-all ${isActive(item.href)
                                ? 'bg-teal-50 text-teal-700 ring-1 ring-teal-100'
                                : 'text-slate-700 hover:bg-slate-100'}`}
                        >
                            <item.icon class="h-5 w-5" />
                            <span class="font-medium">{item.name}</span>
                            {#if isActive(item.href)}
                                {#if getLocale() === 'fa'}
                                    <ChevronLeft class="ms-auto h-4 w-4" />
                                {:else}
                                    <ChevronRight class="ms-auto h-4 w-4" />
                                {/if}
                            {/if}
                        </a>
                    </li>
                {/each}
            </ul>

            <div class="border-t border-base-200 p-4">
                <button class="btn btn-ghost btn-block justify-start gap-3 rounded-xl text-error hover:bg-red-50">
                    <LogOut class="h-5 w-5" />
                    <span>{m.nav_logout()}</span>
                </button>
            </div>
        </div>
    </div>
</div>
