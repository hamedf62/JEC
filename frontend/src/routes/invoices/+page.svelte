<script lang="ts">
    import { onMount } from "svelte";
    import { Receipt, TrendingUp, Users, Calendar, Info } from "lucide-svelte";
    import * as m from "../../paraglide/messages";
    import { getLocale } from "../../paraglide/runtime";
    import { getAnalysis, formatAmount, formatNumber } from "$lib/api";
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
                getAnalysis("Invoices", "daily_breakdown"),
                getAnalysis("Invoices", "cumulative"),
                getAnalysis("Invoices", "top_beneficiaries"),
                getAnalysis("Invoices", "summary_statistics"),
            ]);

            // Format Daily Data for Bar Chart
            if (daily?.data?.daily_breakdown) {
                dailyData = {
                    labels: daily.data.daily_breakdown.map(
                        (d: any) => d.jalali_date,
                    ),
                    datasets: [
                        {
                            label: m.chart_daily_revenue(),
                            data: daily.data.daily_breakdown.map(
                                (d: any) => d.sum,
                            ),
                            backgroundColor: "rgba(59, 130, 246, 0.5)",
                            borderColor: "rgb(59, 130, 246)",
                            borderWidth: 1,
                        },
                    ],
                };
            }

            // Format Cumulative Data for Line Chart
            if (cumulative?.data?.cumulative_data) {
                cumulativeData = {
                    labels: cumulative.data.cumulative_data.map(
                        (d: any) => d.jalali_date,
                    ),
                    datasets: [
                        {
                            label: m.stat_total_sales(),
                            data: cumulative.data.cumulative_data.map(
                                (d: any) => d.cumulative,
                            ),
                            fill: true,
                            backgroundColor: "rgba(59, 130, 246, 0.1)",
                            borderColor: "rgb(59, 130, 246)",
                            tension: 0.1,
                        },
                    ],
                };
            }

            // Format Top Beneficiaries for Bar Chart
            if (top?.data?.beneficiaries) {
                topBeneficiariesData = {
                    labels: top.data.beneficiaries.map(
                        (b: any) =>
                            b.customer_name ||
                            b.beneficiary ||
                            b.name ||
                            m.label_unknown(),
                    ), // fallback because backend col names vary
                    datasets: [
                        {
                            label: m.stat_total_sales(),
                            data: top.data.beneficiaries.map((b: any) => b.sum),
                            backgroundColor: "rgba(16, 185, 129, 0.5)",
                            borderColor: "rgb(16, 185, 129)",
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
            <div class="p-3 bg-primary/10 rounded-2xl text-primary">
                <Receipt class="w-8 h-8" />
            </div>
            <div>
                <h1 class="text-3xl font-bold">{m.page_invoices_title()}</h1>
                <p class="text-base-content/60">
                    {m.page_invoices_subtitle()}
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
                    <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
                        <TrendingUp class="w-5 h-5" />
                    </div>
                    <div>
                        <p
                            class="text-xs text-base-content/60 uppercase tracking-wider font-semibold"
                        >
                            {m.stat_total_sales()}
                        </p>
                        <p class="text-lg font-bold">
                            {formatAmount(summaryStats?.total_sum || 0)}
                        </p>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body p-4 flex-row items-center gap-4">
                    <div class="p-2 bg-green-100 text-green-600 rounded-lg">
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
                            {m.stat_avg_invoice()}
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

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Cumulative Chart -->
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body">
                    <h2 class="card-title text-sm font-bold opacity-70">
                        {m.chart_revenue_trend()}
                    </h2>
                    <div class="h-64 mt-4">
                        {#if cumulativeData}
                            <LineChart
                                data={cumulativeData}
                                title={m.chart_revenue_trend()}
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

            <!-- Daily Revenue Chart -->
            <div class="card bg-base-100 shadow-sm border border-base-200">
                <div class="card-body">
                    <h2 class="card-title text-sm font-bold opacity-70">
                        {m.chart_daily_revenue()}
                    </h2>
                    <div class="h-64 mt-4">
                        {#if dailyData}
                            <BarChart
                                data={dailyData}
                                title={m.chart_daily_revenue()}
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
                        {m.chart_top_customers()}
                    </h2>
                    <div class="h-80 mt-4">
                        {#if topBeneficiariesData}
                            <BarChart
                                data={topBeneficiariesData}
                                title={m.chart_top_customers()}
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
