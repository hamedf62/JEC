<script lang="ts">
    import { Chart, registerables } from 'chart.js';
    import { onMount } from 'svelte';

    Chart.register(...registerables);

    interface Props {
        data: {
            labels: string[];
            datasets: Record<string, unknown>[];
        };
        title?: string;
    }

    let { data, title = '' }: Props = $props();

    let canvas: HTMLCanvasElement;
    let chart: Chart | null = null;

    function buildOptions() {
        return {
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
        };
    }

    onMount(() => {
        chart = new Chart(canvas, {
            type: 'bar',
            data: data as any,
            options: buildOptions()
        });
        return () => chart?.destroy();
    });

    $effect(() => {
        if (chart && data) {
            chart.data = data as any;
            chart.options = buildOptions() as any;
            chart.update();
        }
    });
</script>

<div class="relative h-full w-full">
    <canvas bind:this={canvas}></canvas>
</div>
