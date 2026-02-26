<script lang="ts">
    import * as m from '../../paraglide/messages';
    import { getLocale } from '../../paraglide/runtime';
    import { ShieldCheck, Bell, Languages, Palette, SlidersHorizontal } from 'lucide-svelte';

    const prefs = [
        { icon: Bell, title: getLocale() === 'fa' ? 'اعلان ها' : 'Notifications', desc: getLocale() === 'fa' ? 'دریافت اعلان گزارش ها و نوسانات غیرعادی.' : 'Receive alerts for reports and unusual changes.' },
        { icon: Languages, title: getLocale() === 'fa' ? 'زبان پنل' : 'Dashboard Language', desc: getLocale() === 'fa' ? 'نمایش خودکار فارسی یا انگلیسی.' : 'Automatically display Persian or English.' },
        { icon: Palette, title: getLocale() === 'fa' ? 'نمایش ظاهری' : 'Appearance', desc: getLocale() === 'fa' ? 'تم مینیمال روشن با کنتراست بالا.' : 'Light minimal theme with high contrast.' },
        { icon: ShieldCheck, title: getLocale() === 'fa' ? 'امنیت' : 'Security', desc: getLocale() === 'fa' ? 'ثبت دستگاه های فعال و فعالیت حساب.' : 'Track active devices and account activity.' }
    ];
</script>

<div class="space-y-6">
    <div class="rounded-2xl border border-base-200 bg-white p-6 shadow-sm">
        <div class="flex items-center gap-3">
            <div class="rounded-xl bg-teal-50 p-2 text-teal-700">
                <SlidersHorizontal class="h-5 w-5" />
            </div>
            <div>
                <h1 class="text-2xl font-black text-slate-900">{m.nav_settings()}</h1>
                <p class="text-sm text-slate-500">{getLocale() === 'fa' ? 'پیکربندی تنظیمات پنل مدیریت' : 'Configure dashboard preferences and system behavior.'}</p>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        {#each prefs as item}
            <div class="card">
                <div class="card-body">
                    <div class="flex items-start gap-3">
                        <div class="rounded-xl bg-slate-100 p-2 text-slate-700">
                            <item.icon class="h-5 w-5" />
                        </div>
                        <div>
                            <h2 class="text-base font-bold text-slate-900">{item.title}</h2>
                            <p class="mt-1 text-sm text-slate-500">{item.desc}</p>
                        </div>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>
