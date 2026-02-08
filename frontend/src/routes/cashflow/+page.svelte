<script lang="ts">
    import { onMount } from "svelte";
    import {
        Activity,
        ArrowUpCircle,
        ArrowDownCircle,
        Scale,
        Calendar,
    } from "lucide-svelte";
    import * as m from "../../paraglide/messages";
    import { getLocale } from "../../paraglide/runtime";
    import { getAnalysis, formatAmount, formatNumber } from "$lib/api";
    import LineChart from "$lib/components/LineChart.svelte";

    let loading = $state(true);
    let error = $state("");

    let cashFlowData = $state<any>(null);
    let chartData = $state<any>(null);
    let todayMarker = $state<string | null>(null);

    onMount(async () => {
        try {
            // We can use any valid file type here as the backend cash_flow ignore it
            const response = await getAnalysis("Payable", "cash_flow");

            if (response && response.data) {
                const data = response.data;
                cashFlowData = data;
                todayMarker = data.today_jalali || data.today;

                if (data.daily_flow) {
                    chartData = {
                        labels: data.daily_flow.map(
                            (d: any) => d.jalali_date || d.date,
                        ),
                        datasets: [
                            {
                                label: m.nav_cashflow(),
                                data: data.daily_flow.map(
                                    (d: any) => d.cumulative,
                                ),
                                borderColor: "#0ea5e9",
                                backgroundColor: "rgba(14, 165, 233, 0.1)",
                                fill: true,
                                tension: 0.4,
                                pointRadius: 2,
                                borderWeight: 3,
                            },
                        ],
                    };
                }
            }
            loading = false;
        } catch (e: any) {
            error = e.message || "Failed to load cash flow data";
            loading = false;
        }
    });
</script>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
            <div class="p-3 bg-info/10 rounded-2xl text-info">
                <Activity class="w-8 h-8" />
            </div>
            <div>
                <h1 class="text-3xl font-bold">{m.page_cashflow_title()}</h1>
                <p class="text-base-content/60">
                    {m.page_cashflow_subtitle()}
                </p>
            </div>
        </div>
        {#if loading}
            <span class="loading loading-spinner loading-md"></span>
        {/if}
    </div>

    {#if error}
        <div class="alert alert-error shadow-lg">
            <span>{error}</span>
        </div>
    {/if}

    {#if !loading && !error}
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
                        <Scale class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {getLocale() === "fa"
                                ? "وضعیت فعلی"
                                : "Current Position"}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(cashFlowData?.current_position || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-green-100 text-green-600 rounded-lg">
                        <ArrowUpCircle class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {getLocale() === "fa"
                                ? "مجموع ورودی"
                                : "Total Incoming"}
                        </p>
                        <p class="text-lg font-bold text-success">
                            {formatAmount(cashFlowData?.total_income || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-red-100 text-red-600 rounded-lg">
                        <ArrowDownCircle class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {getLocale() === "fa"
                                ? "مجموع خروجی"
                                : "Total Outgoing"}
                        </p>
                        <p class="text-lg font-bold text-error">
                            {formatAmount(cashFlowData?.total_outcome || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-purple-100 text-purple-600 rounded-lg">
                        <Activity class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {getLocale() === "fa"
                                ? "خالص نقدینگی"
                                : "Net Cash Flow"}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(cashFlowData?.net_cash_flow || 0)}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Chart -->
        <div class="card bg-base-100 shadow-md border border-base-200">
            <div class="card-body">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="card-title text-xl font-bold">
                        {getLocale() === "fa"
                            ? "روند تغییرات نقدینگی"
                            : "Cash Flow Trend"}
                    </h2>
                    <div class="badge badge-outline gap-2 p-3">
                        <Calendar class="w-4 h-4" />
                        <span
                            >{getLocale() === "fa" ? "امروز: " : "Today: "}
                            {todayMarker}</span
                        >
                    </div>
                </div>
                <div class="h-[400px]">
                    {#if chartData}
                        <LineChart data={chartData} title={m.nav_cashflow()} />
                    {/if}
                </div>
                <div
                    class="mt-4 p-4 bg-info/5 rounded-xl border border-info/10"
                >
                    <p class="text-sm text-info flex items-center gap-2">
                        <Activity class="w-4 h-4" />
                        {getLocale() === "fa"
                            ? "این نمودار نشان‌دهنده تغییرات نقدینگی در گذشته و پیش‌بینی آینده بر اساس سررسید چک‌ها و فاکتورهاست."
                            : "This chart shows cash flow changes in the past and future projections based on due dates of cheques and invoices."}
                    </p>
                </div>
            </div>
        </div>

        <!-- Breakdown by Type -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="card bg-base-100 shadow-md border border-base-200">
                <div class="card-header p-6 pb-0">
                    <h2 class="text-lg font-bold">
                        {getLocale() === "fa"
                            ? "تفکیک منابع نقدینگی"
                            : "Cash Source Breakdown"}
                    </h2>
                </div>
                <div class="card-body">
                    <div class="overflow-x-auto">
                        <table class="table w-full">
                            <thead>
                                <tr>
                                    <th
                                        >{getLocale() === "fa"
                                            ? "نوع"
                                            : "Type"}</th
                                    >
                                    <th
                                        >{getLocale() === "fa"
                                            ? "تعداد"
                                            : "Count"}</th
                                    >
                                    <th
                                        >{getLocale() === "fa"
                                            ? "مجموع"
                                            : "Total"}</th
                                    >
                                </tr>
                            </thead>
                            <tbody>
                                {#each cashFlowData?.type_summary || [] as item}
                                    <tr class="hover">
                                        <td>
                                            <span
                                                class="badge badge-ghost font-medium"
                                                >{item.type}</span
                                            >
                                        </td>
                                        <td>{formatNumber(item.count)}</td>
                                        <td
                                            class={item.sum < 0
                                                ? "text-error"
                                                : "text-success"}
                                        >
                                            {formatAmount(Math.abs(item.sum))}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-md border border-base-200">
                <div class="card-header p-6 pb-0">
                    <h2 class="text-lg font-bold">
                        {getLocale() === "fa"
                            ? "تبادلات اخیر و آتی"
                            : "Recent & Future Transactions"}
                    </h2>
                </div>
                <div class="card-body">
                    <div class="overflow-x-auto max-h-[300px] overflow-y-auto">
                        <table class="table table-sm w-full">
                            <thead>
                                <tr>
                                    <th
                                        >{getLocale() === "fa"
                                            ? "تاریخ"
                                            : "Date"}</th
                                    >
                                    <th
                                        >{getLocale() === "fa"
                                            ? "نوع"
                                            : "Type"}</th
                                    >
                                    <th
                                        >{getLocale() === "fa"
                                            ? "مبلغ"
                                            : "Amount"}</th
                                    >
                                </tr>
                            </thead>
                            <tbody>
                                {#each (cashFlowData?.detailed_transactions || []).slice(-20) as tx}
                                    <tr class="hover">
                                        <td class="text-xs whitespace-nowrap"
                                            >{tx.jalali_date}</td
                                        >
                                        <td
                                            ><span class="text-xs"
                                                >{tx.type}</span
                                            ></td
                                        >
                                        <td
                                            class={tx.amount < 0
                                                ? "text-error font-medium"
                                                : "text-success font-medium"}
                                        >
                                            {formatNumber(Math.abs(tx.amount))}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
