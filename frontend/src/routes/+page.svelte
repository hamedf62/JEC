<script lang="ts">
    import { onMount } from "svelte";
    import * as m from "../paraglide/messages";
    import { getLocale } from "../paraglide/runtime";
    import { getSummary, getAnalysis, formatDate } from "$lib/api";
    import BarChart from "$lib/components/BarChart.svelte";
    import LineChart from "$lib/components/LineChart.svelte";
    import {
        TrendingUp,
        Package,
        DollarSign,
        ArrowUpRight,
        ArrowDownRight,
        Receipt,
        Wallet,
        FileText,
        Activity,
        AlertCircle,
        RefreshCw,
    } from "lucide-svelte";

    let summary = $state<any>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    // Default placeholder data
    let revenueTrendData = $state({
        labels: [],
        datasets: [
            {
                label: m.chart_revenue_trend(),
                data: [],
                borderColor: "#4f46e5",
                backgroundColor: "rgba(79, 70, 229, 0.1)",
                fill: true,
                tension: 0.4,
            },
        ],
    });

    let categoryData = $state({
        labels: [],
        datasets: [],
    });

    let displayCategoryData = $derived({
        labels: [
            m.nav_payable(),
            m.nav_receivable ? m.nav_receivable() : "Receivable",
            m.nav_invoices(),
            m.nav_performa(),
        ],
        datasets: categoryData.datasets,
    });

    async function loadData() {
        loading = true;
        error = null;
        try {
            const [summaryData, invoiceTrend, cashFlow] = await Promise.all([
                getSummary().catch(() => null),
                getAnalysis("Invoices", "daily_breakdown").catch(() => null),
                getAnalysis("Payable", "cash_flow").catch(() => null),
            ]);

            if (summaryData) {
                console.log("Summary data loaded:", summaryData);
                summary = summaryData;
                if (cashFlow && cashFlow.data) {
                    summary.CashFlow = cashFlow.data;
                }
            } else {
                console.error("Summary data is null");
            }

            if (
                invoiceTrend &&
                invoiceTrend.data &&
                invoiceTrend.data.daily_breakdown
            ) {
                const daily = invoiceTrend.data.daily_breakdown;
                revenueTrendData = {
                    labels: daily.map((d: any) =>
                        formatDate(d.jalali_date || d.date),
                    ),
                    datasets: [
                        {
                            label: m.chart_daily_revenue(),
                            data: daily.map((d: any) => d.sum),
                            borderColor: "#4f46e5",
                            backgroundColor: "rgba(79, 70, 229, 0.1)",
                            fill: true,
                            tension: 0.4,
                        },
                    ],
                };
            }

            // Update category chart from summary
            if (summary) {
                categoryData = {
                    labels: [
                        m.nav_payable(),
                        m.nav_receivable(),
                        m.nav_invoices(),
                        m.nav_performa(),
                    ],
                    datasets: [
                        {
                            label: m.chart_doc_count(),
                            data: [
                                summary.Payable?.total_rows || 0,
                                summary.Receivable?.total_rows || 0,
                                summary.Invoices?.total_rows || 0,
                                summary.Performa?.total_rows || 0,
                            ],
                            backgroundColor: [
                                "rgba(244, 63, 94, 0.7)",
                                "rgba(14, 165, 233, 0.7)",
                                "rgba(34, 197, 94, 0.7)",
                                "rgba(234, 179, 8, 0.7)",
                            ],
                            borderRadius: 8,
                        },
                    ],
                };
            }
        } catch (e: any) {
            console.error(e);
            error = m.error_api();
        } finally {
            loading = false;
        }
    }

    onMount(loadData);

    function formatStatValue(val: number, isCurrency: boolean = false) {
        if (isCurrency) {
            const formatted = new Intl.NumberFormat(
                getLocale() === "fa" ? "fa-IR" : "en-US",
                {
                    maximumFractionDigits: 1,
                },
            ).format(val / 1000000);
            return formatted + (getLocale() === "fa" ? " م" : "M");
        }
        return new Intl.NumberFormat(
            getLocale() === "fa" ? "fa-IR" : "en-US",
        ).format(val);
    }

    let statsList = $derived([
        {
            title: m.stat_total_sales(),
            value: summary?.Invoices
                ? formatStatValue(summary.Invoices.total_sum, true)
                : "0",
            unit: getLocale() === "fa" ? m.label_rial() : "IRR",
            change: "+12.5%",
            trend: "up",
            icon: DollarSign,
        },
        {
            title: m.stat_active_invoices(),
            value: summary?.Invoices
                ? formatStatValue(summary.Invoices.total_rows)
                : "0",
            unit: m.stat_docs(),
            change: "+8",
            trend: "up",
            icon: Receipt,
        },
        {
            title: m.stat_accounts_payable(),
            value: summary?.Payable
                ? formatStatValue(summary.Payable.total_sum, true)
                : "0",
            unit: getLocale() === "fa" ? m.label_rial() : "IRR",
            change: "-2.4%",
            trend: "down",
            icon: Wallet,
        },
        {
            title: m.nav_cashflow(),
            value: summary?.CashFlow
                ? formatStatValue(summary.CashFlow.current_position, true)
                : "0",
            unit: getLocale() === "fa" ? m.label_rial() : "IRR",
            change: summary?.CashFlow?.net_cash_flow > 0 ? "+Trend" : "-Trend",
            trend: summary?.CashFlow?.net_cash_flow > 0 ? "up" : "down",
            icon: Activity,
        },
    ]);
</script>

<div class="space-y-6">
    <div
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
    >
        <div>
            <h1 class="text-3xl font-black tracking-tight italic">
                {m.dashboard_title()}
            </h1>
            <p class="text-base-content/60">
                {m.dashboard_subtitle()}
            </p>
        </div>
        <div class="flex gap-2">
            <button
                class="btn btn-outline border-base-300"
                onclick={loadData}
                disabled={loading}
            >
                <RefreshCw class="w-4 h-4 {loading ? 'animate-spin' : ''}" />
                {m.btn_refresh()}
            </button>
            <button class="btn btn-primary shadow-lg shadow-primary/20"
                >{m.btn_generate_report()}</button
            >
        </div>
    </div>

    {#if error}
        <div class="alert alert-error shadow-lg">
            <AlertCircle class="w-6 h-6" />
            <div>
                <h3 class="font-bold">Connection Error</h3>
                <div class="text-xs">{error}</div>
            </div>
            <button class="btn btn-sm btn-ghost" onclick={loadData}
                >Retry</button
            >
        </div>
    {/if}

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each statsList as stat}
            <div
                class="card bg-base-100 shadow-sm border border-base-200 hover:shadow-md transition-all group"
            >
                <div class="card-body p-6">
                    <div class="flex justify-between items-start">
                        <div
                            class="p-3 bg-base-200/50 rounded-xl group-hover:bg-primary group-hover:text-primary-content transition-colors"
                        >
                            <stat.icon class="w-6 h-6" />
                        </div>
                        <div class="text-right">
                            <p
                                class="text-[10px] text-base-content/50 uppercase tracking-widest font-black"
                            >
                                {stat.title}
                            </p>
                            <div
                                class="flex items-baseline justify-end gap-1 mt-1"
                            >
                                <h2 class="text-2xl font-black tracking-tight">
                                    {stat.value}
                                </h2>
                                <span class="text-[10px] opacity-40 font-bold"
                                    >{stat.unit}</span
                                >
                            </div>
                        </div>
                    </div>
                    <div
                        class="mt-4 flex items-center justify-between border-t border-base-100 pt-4"
                    >
                        <div
                            class="flex items-center gap-1.5 {stat.trend ===
                            'up'
                                ? 'text-success'
                                : 'text-error'}"
                        >
                            <div class="p-0.5 rounded-full bg-current/10">
                                {#if stat.trend === "up"}
                                    <ArrowUpRight class="w-3 h-3" />
                                {:else}
                                    <ArrowDownRight class="w-3 h-3" />
                                {/if}
                            </div>
                            <span class="text-sm font-bold">{stat.change}</span>
                        </div>
                        <span
                            class="text-[10px] text-base-content/30 uppercase font-black tracking-tighter"
                            >{m.stat_growth()}</span
                        >
                    </div>
                </div>
            </div>
        {/each}
    </div>

    <!-- Analysis Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div
            class="card bg-base-100 shadow-sm border border-base-200 lg:col-span-2"
        >
            <div class="card-body">
                <div class="flex justify-between items-center mb-6">
                    <div>
                        <h3 class="font-bold text-lg">
                            {m.chart_revenue_trend()}
                        </h3>
                        <p class="text-xs opacity-50">
                            {m.chart_revenue_subtitle()}
                        </p>
                    </div>
                    <div class="join">
                        <button class="btn btn-xs join-item btn-active"
                            >{m.chart_daily()}</button
                        >
                        <button class="btn btn-xs join-item"
                            >{m.chart_monthly()}</button
                        >
                    </div>
                </div>
                <div class="h-80 w-full relative">
                    {#if loading}
                        <div
                            class="absolute inset-0 flex items-center justify-center bg-base-100/50 z-10"
                        >
                            <span class="loading loading-ring loading-lg"
                            ></span>
                        </div>
                    {/if}
                    <LineChart data={revenueTrendData} />
                </div>
            </div>
        </div>

        <div class="card bg-base-100 shadow-sm border border-base-200">
            <div class="card-body">
                <h3 class="font-bold text-lg mb-6">
                    {m.chart_document_volume()}
                </h3>
                <div class="h-80 w-full relative">
                    {#if loading}
                        <div
                            class="absolute inset-0 flex items-center justify-center bg-base-100/50 z-10"
                        >
                            <span class="loading loading-ring loading-lg"
                            ></span>
                        </div>
                    {/if}
                    <BarChart data={displayCategoryData} />
                </div>
            </div>
        </div>
    </div>

    <!-- Detailed Analysis Table -->
    <div class="card bg-base-100 shadow-sm border border-base-200">
        <div class="card-body p-0">
            <div
                class="p-6 border-b border-base-200 flex justify-between items-center bg-base-100"
            >
                <h3 class="font-bold text-lg">{m.table_title()}</h3>
                <div class="badge badge-primary badge-outline">
                    {m.table_subtitle()}
                </div>
            </div>
            <div class="overflow-x-auto min-h-64">
                {#if loading}
                    <div class="flex items-center justify-center h-64">
                        <span class="loading loading-dots loading-md"></span>
                    </div>
                {:else if summary}
                    <table class="table table-zebra table-md">
                        <thead class="bg-base-200/50">
                            <tr>
                                <th>{m.table_col_source()}</th>
                                <th>{m.table_col_records()}</th>
                                <th>{m.table_col_value()}</th>
                                <th>{m.table_col_avg()}</th>
                                <th>{m.table_col_status()}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each Object.entries(summary) as [key, data]}
                                <tr>
                                    <td class="font-bold">
                                        {#if key === "Payable"}
                                            {m.nav_payable()}
                                        {:else}
                                            {key === "Invoices"
                                                ? m.nav_invoices()
                                                : key === "Performa"
                                                  ? m.nav_performa()
                                                  : key === "Receivable"
                                                    ? m.nav_receivable()
                                                    : key}
                                        {/if}
                                    </td>
                                    <td>{data.total_rows}</td>
                                    <td class="font-mono"
                                        >{(
                                            data.total_sum || 0
                                        ).toLocaleString()}</td
                                    >
                                    <td class="opacity-70">
                                        {data.numeric_statistics
                                            ? (
                                                  data.numeric_statistics
                                                      .total_amount?.mean ||
                                                  data.numeric_statistics.amount
                                                      ?.mean ||
                                                  0
                                              ).toLocaleString()
                                            : "0"}
                                    </td>
                                    <td
                                        ><div
                                            class="badge badge-success badge-xs"
                                        >
                                            {m.status_active()}
                                        </div></td
                                    >
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {:else}
                    <div
                        class="flex items-center justify-center h-64 opacity-30 italic"
                    >
                        {m.no_data()}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>
