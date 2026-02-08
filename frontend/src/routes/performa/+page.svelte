<script lang="ts">
    import { onMount } from "svelte";
    import { FileText, TrendingUp, Users, Calendar, Info } from "lucide-svelte";
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
                getAnalysis("Performa", "daily_breakdown"),
                getAnalysis("Performa", "cumulative"),
                getAnalysis("Performa", "top_beneficiaries"),
                getAnalysis("Performa", "summary_statistics"),
            ]);

            // Format Daily Data
            if (daily?.data?.daily_breakdown) {
                dailyData = {
                    labels: daily.data.daily_breakdown.map((d: any) =>
                        formatDate(d.jalali_date),
                    ),
                    datasets: [
                        {
                            label: m.chart_daily(),
                            data: daily.data.daily_breakdown.map(
                                (d: any) => d.sum,
                            ),
                            backgroundColor: "rgba(139, 92, 246, 0.5)",
                            borderColor: "rgb(139, 92, 246)",
                            borderWidth: 1,
                        },
                    ],
                };
            }

            // Format Cumulative Data
            if (cumulative?.data?.cumulative_data) {
                cumulativeData = {
                    labels: cumulative.data.cumulative_data.map((d: any) =>
                        formatDate(d.jalali_date),
                    ),
                    datasets: [
                        {
                            label: m.chart_pipeline_growth(),
                            data: cumulative.data.cumulative_data.map(
                                (d: any) => d.cumulative,
                            ),
                            fill: true,
                            backgroundColor: "rgba(139, 92, 246, 0.1)",
                            borderColor: "rgb(139, 92, 246)",
                            tension: 0.1,
                        },
                    ],
                };
            }

            // Format Top Beneficiaries
            if (top?.data?.beneficiaries) {
                topBeneficiariesData = {
                    labels: top.data.beneficiaries.map(
                        (b: any) =>
                            b.customer_name ||
                            b.beneficiary ||
                            b.name ||
                            m.label_unknown(),
                    ),
                    datasets: [
                        {
                            label: m.stat_total_projected(),
                            data: top.data.beneficiaries.map((b: any) => b.sum),
                            backgroundColor: "rgba(236, 72, 153, 0.5)",
                            borderColor: "rgb(236, 72, 153)",
                            borderWidth: 1,
                        },
                    ],
                };
            }

            summaryStats = summary?.data;
            loading = false;
        } catch (e: any) {
            error = e.message || "Failed to load analysis data";
            loading = false;
        }
    });
</script>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
            <div class="p-3 bg-accent/10 rounded-2xl text-accent">
                <FileText class="w-8 h-8" />
            </div>
            <div>
                <h1 class="text-3xl font-bold">{m.page_performa_title()}</h1>
                <p class="text-base-content/60">
                    {m.page_performa_subtitle()}
                </p>
            </div>
        </div>
        {#if loading}
            <span class="loading loading-spinner loading-md"></span>
        {/if}
    </div>

    {#if error}
        <div class="alert alert-error">
            <span>{error}</span>
        </div>
    {/if}

    {#if !loading && !error}
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-purple-100 text-purple-600 rounded-lg">
                        <TrendingUp class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_total_projected()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(summaryStats?.total_sum || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-pink-100 text-pink-600 rounded-lg">
                        <Calendar class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_pending_performa()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatNumber(summaryStats?.total_rows || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                        <Users class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_avg_value()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(summaryStats?.total_mean || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-gray-100 text-gray-600 rounded-lg">
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

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Cumulative Chart -->
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body">
                    <h2 class="card-title text-sm font-bold opacity-70">
                        {m.chart_pipeline_growth()}
                    </h2>
                    <div class="h-64 mt-4">
                        {#if cumulativeData}
                            <LineChart
                                data={cumulativeData}
                                title={m.chart_pipeline_growth()}
                            />
                        {:else}
                            <div
                                class="flex items-center justify-center h-full opacity-30 italic"
                            >
                                {m.no_data()}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Daily Chart -->
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body">
                    <h2 class="card-title text-sm font-bold opacity-70">
                        {m.chart_daily()}
                    </h2>
                    <div class="h-64 mt-4">
                        {#if dailyData}
                            <BarChart
                                data={dailyData}
                                title={m.chart_daily()}
                            />
                        {:else}
                            <div
                                class="flex items-center justify-center h-full opacity-30 italic"
                            >
                                {m.no_data()}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Top Customers Chart -->
            <div
                class="card bg-base-100 shadow-sm border border-base-200 lg:col-span-2"
            >
                <div class="card-body">
                    <h2 class="card-title text-sm font-bold opacity-70">
                        {m.chart_top_leads()}
                    </h2>
                    <div class="h-80 mt-4">
                        {#if topBeneficiariesData}
                            <BarChart
                                data={topBeneficiariesData}
                                title={m.chart_top_leads()}
                            />
                        {:else}
                            <div
                                class="flex items-center justify-center h-full opacity-30 italic"
                            >
                                {m.no_data()}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
