<script lang="ts">
    import "../app.css";
    import * as m from "../paraglide/messages";
    import { getLocale, setLocale } from "../paraglide/runtime";
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
    } from "lucide-svelte";

    let { children } = $props();

    let sidebarOpen = $state(false);

    const menuItems = $derived([
        { name: m.nav_overview(), icon: BarChart3, href: "/" },
        { name: m.nav_cashflow(), icon: Activity, href: "/cashflow" },
        { name: m.nav_invoices(), icon: Receipt, href: "/invoices" },
        { name: m.nav_receivable(), icon: Wallet, href: "/receivable" },
        { name: m.nav_payable(), icon: Wallet, href: "/payable" },
        { name: m.nav_performa(), icon: FileText, href: "/performa" },
    ]);

    function toggleLanguage() {
        const newLocale = getLocale() === "fa" ? "en" : "fa";
        setLocale(newLocale);
        // Persist in cookie if needed, but for now just state
        document.documentElement.lang = newLocale;
        document.documentElement.dir = newLocale === "fa" ? "rtl" : "ltr";
    }
</script>

<div class="drawer lg:drawer-open" dir={getLocale() === "fa" ? "rtl" : "ltr"}>
    <input
        id="dashboard-drawer"
        type="checkbox"
        class="drawer-toggle"
        bind:checked={sidebarOpen}
    />

    <div class="drawer-content flex flex-col">
        <!-- Navbar -->
        <div class="navbar bg-base-100 border-b border-base-200 px-4">
            <div class="flex-none lg:hidden">
                <label for="dashboard-drawer" class="btn btn-square btn-ghost">
                    <Menu class="w-6 h-6" />
                </label>
            </div>
            <div class="flex-1">
                <span
                    class="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
                >
                    {m.app_title()}
                </span>
            </div>
            <div class="flex-none gap-2">
                <!-- Language Switcher -->
                <button
                    class="btn btn-ghost btn-circle"
                    onclick={toggleLanguage}
                >
                    <Languages class="w-5 h-5" />
                    <span class="text-xs uppercase">{getLocale()}</span>
                </button>

                <div class="dropdown dropdown-end">
                    <div
                        tabindex="0"
                        role="button"
                        class="btn btn-ghost btn-circle avatar"
                    >
                        <div
                            class="w-10 rounded-full bg-base-200 flex items-center justify-center"
                        >
                            <User class="w-6 h-6" />
                        </div>
                    </div>
                    <ul
                        tabindex="0"
                        class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52"
                    >
                        <li><a>{m.nav_profile()}</a></li>
                        <li><a>{m.nav_settings()}</a></li>
                        <li><a>{m.nav_logout()}</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <main class="p-6 bg-base-200/50 min-h-[calc(100vh-64px)] overflow-auto">
            <div class="max-w-7xl mx-auto">
                {@render children()}
            </div>
        </main>
    </div>

    <!-- Sidebar -->
    <div class="drawer-side z-20">
        <label
            for="dashboard-drawer"
            aria-label="close sidebar"
            class="drawer-overlay"
        ></label>
        <div
            class="w-64 min-h-full bg-base-100 border-r border-base-200 flex flex-col"
        >
            <div
                class="p-6 flex items-center gap-3 border-b border-base-200 lg:flex hidden"
            >
                <div
                    class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-content"
                >
                    <BarChart3 class="w-5 h-5" />
                </div>
                <span class="text-xl font-bold">{m.admin_panel()}</span>
            </div>

            <ul class="menu p-4 gap-2 flex-grow">
                <li
                    class="menu-title text-xs uppercase tracking-widest opacity-50 font-bold mb-2"
                >
                    {m.sidebar_main()}
                </li>
                {#each menuItems as item}
                    <li>
                        <a
                            href={item.href}
                            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-200 transition-colors"
                        >
                            <item.icon class="w-5 h-5" />
                            <span>{item.name}</span>
                        </a>
                    </li>
                {/each}

                <div class="divider"></div>

                <li
                    class="menu-title text-xs uppercase tracking-widest opacity-50 font-bold mb-2"
                >
                    {m.sidebar_system()}
                </li>
                <li>
                    <a
                        href="/settings"
                        class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-base-200 transition-colors"
                    >
                        <Settings class="w-5 h-5" />
                        <span>{m.nav_settings()}</span>
                    </a>
                </li>
            </ul>

            <div class="p-4 border-t border-base-200">
                <button
                    class="btn btn-ghost btn-block justify-start gap-3 text-error hover:bg-error/10"
                >
                    <LogOut class="w-5 h-5" />
                    <span>{m.nav_logout()}</span>
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    @reference "../app.css";

    :global(body) {
        @apply bg-base-200;
    }
</style>
