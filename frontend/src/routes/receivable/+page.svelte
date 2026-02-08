<script lang="ts">
    import { onMount } from "svelte";
    import { Wallet, TrendingUp, Users, Calendar, Info } from "lucide-svelte";
    import * as m from "../../paraglide/messages";
    import { getLocale } from "../../paraglide/runtime";
    import {
        getAnalysis,
        formatAmount,
        formatNumber,
        formatDate,
    } from "$lib/api";
    import BarChart from "$lib/components/BarChart.svelte";
    import LineChart from "$lib/components/LineChart.svelte";

    let loading = $state(true);
    let error = $state("");

    let dailyData = $state<any>(null);
    let cumulativeData = $state<any>(null);
    let topBeneficiariesData = $state<any>(null);
    let summaryStats = $state<any>(null);

    onMount(async () => {
        try {
            const [daily, cumulative, top, summary] = await Promise.all([
                getAnalysis("Receivable", "daily_breakdown"),
                getAnalysis("Receivable", "cumulative"),
                getAnalysis("Receivable", "top_beneficiaries"),
                getAnalysis("Receivable", "summary_statistics"),
            ]);

            // Format Daily Data for Bar Chart
            if (daily?.data?.daily_breakdown) {
                dailyData = {
                    labels: daily.data.daily_breakdown.map((d: any) =>
                        formatDate(d.jalali_date),
                    ),
                    datasets: [
                        {
                            label: m.chart_daily_revenue(),
                            data: daily.data.daily_breakdown.map(
                                (d: any) => d.sum,
                            ),
                            backgroundColor: "rgba(16, 185, 129, 0.5)",
                            borderColor: "rgb(16, 185, 129)",
                            borderWidth: 1,
                        },
                    ],
                };
            }

            // Format Cumulative Data for Line Chart
            if (cumulative?.data?.cumulative_data) {
                cumulativeData = {
                    labels: cumulative.data.cumulative_data.map((d: any) =>
                        formatDate(d.jalali_date),
                    ),
                    datasets: [
                        {
                            label: m.stat_total_receivable(),
                            data: cumulative.data.cumulative_data.map(
                                (d: any) => d.cumulative,
                            ),
                            fill: true,
                            backgroundColor: "rgba(16, 185, 129, 0.1)",
                            borderColor: "rgb(16, 185, 129)",
                            tension: 0.4,
                        },
                    ],
                };
            }

            // Format Top Beneficiaries for Chart
            if (top?.data?.beneficiaries) {
                topBeneficiariesData = {
                    labels: top.data.beneficiaries.map(
                        (d: any) =>
                            d.beneficiary ||
                            d.customer_name ||
                            d.company_name ||
                            d.name ||
                            m.label_unknown(),
                    ),
                    datasets: [
                        {
                            label: m.stat_total_receivable(),
                            data: top.data.beneficiaries.map((d: any) => d.sum),
                            backgroundColor: "rgba(16, 185, 129, 0.7)",
                        },
                    ],
                };
            }

            summaryStats = summary?.data;
            loading = false;
        } catch (e: any) {
            console.error("Failed to fetch receivable data:", e);
            error = m.error_api();
        } finally {
            loading = false;
        }
    });
</script>

<div class="space-y-6">
    <!-- Header -->
    <div
        class="flex flex-col md:flex-row md:items-center justify-between gap-4"
    >
        <div class="flex items-center gap-4">
            <div
                class="p-3 bg-emerald-500 text-white rounded-xl shadow-lg ring-4 ring-emerald-500/20"
            >
                <Wallet class="w-8 h-8" />
            </div>
            <div>
                <h1 class="text-3xl font-bold">{m.page_receivable_title()}</h1>
                <p class="text-base-content/60">
                    {m.page_receivable_subtitle()}
                </p>
            </div>
        </div>
        {#if loading}
            <span class="loading loading-spinner loading-md"></span>
        {/if}
    </div>

    {#if error}
        <div class="alert alert-error">
            <Info class="w-5 h-5" />
            <span>{error}</span>
        </div>
    {/if}

    {#if !loading && !error}
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
                        <TrendingUp class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_total_receivable()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(summaryStats?.total_sum || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
                        <Calendar class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_active_invoices()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatNumber(summaryStats?.total_rows || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-purple-100 text-purple-600 rounded-lg">
                        <Users class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_avg_receivable()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(summaryStats?.total_mean || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-orange-100 text-orange-600 rounded-lg">
                        <Info class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.table_col_records()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatNumber(summaryStats?.total_rows || 0)}
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-6">
                    <h2 class="card-title text-lg mb-4">
                        {m.chart_revenue_trend()}
                    </h2>
                    <div class="h-[300px]">
                        {#if cumulativeData}
                            <LineChart data={cumulativeData} />
                        {:else}
                            <div
                                class="flex items-center justify-center h-full text-base-content/40"
                            >
                                {m.no_data()}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-6">
                    <h2 class="card-title text-lg mb-4">
                        {m.chart_daily_revenue()}
                    </h2>
                    <div class="h-[300px]">
                        {#if dailyData}
                            <BarChart data={dailyData} />
                        {:else}
                            <div
                                class="flex items-center justify-center h-full text-base-content/40"
                            >
                                {m.no_data()}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row 2 -->
        <div class="card bg-base-100 shadow-sm border border-base-200">
            <div class="card-body p-6">
                <h2 class="card-title text-lg mb-4">
                    {m.chart_top_customers()}
                </h2>
                <div class="h-[400px]">
                    {#if topBeneficiariesData}
                        <BarChart
                            data={topBeneficiariesData}
                            horizontal={true}
                        />
                    {:else}
                        <div
                            class="flex items-center justify-center h-full text-base-content/40"
                        >
                            {m.no_data()}
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    {/if}
</div>
