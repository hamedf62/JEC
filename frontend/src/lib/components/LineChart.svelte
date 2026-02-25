<script lang="ts">
    import { Line } from 'svelte-chartjs';
    import {
        Chart as ChartJS,
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip,
        Legend,
        Filler
    } from 'chart.js';

    ChartJS.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip,
        Legend,
        Filler
    );

    interface Props {
        data: {
            labels: string[];
            datasets: Record<string, unknown>[];
        };
        title?: string;
    }

    let { data, title = '' }: Props = $props();

    const options = $derived({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'top' as const },
            title: { display: !!title, text: title }
        },
        scales: {
            y: {
                ticks: {
                    callback: (value: number | string) =>
                        new Intl.NumberFormat('fa-IR', { notation: 'compact' }).format(Number(value))
                }
            }
        }
    });
</script>

<div class="relative h-full w-full">
    {#if data}
        <Line {data} {options} />
    {/if}
</div>
