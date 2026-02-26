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
        horizontal?: boolean;
    }

    let { data, title = '', horizontal = false }: Props = $props();

    let canvas: HTMLCanvasElement;
    let chart: Chart | null = null;

    function cloneData(input: Props['data']) {
        if (!input) {
            return { labels: [], datasets: [] };
        }
        try {
            return structuredClone(input);
        } catch {
            return JSON.parse(JSON.stringify(input));
        }
    }

    function buildOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: horizontal ? ('y' as const) : ('x' as const),
            animation: {
                duration: 800,
                easing: 'easeOutQuart' as const
            },
            plugins: {
                legend: {
                    position: 'top' as const,
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle' as const,
                        boxHeight: 8,
                        color: '#334155'
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172acc',
                    titleColor: '#f8fafc',
                    bodyColor: '#e2e8f0',
                    padding: 10,
                    cornerRadius: 10
                },
                title: {
                    display: !!title,
                    text: title,
                    color: '#0f172a',
                    font: {
                        family: 'Vazirmatn',
                        weight: 700
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#64748b',
                        callback: (value: number | string) =>
                            horizontal
                                ? String(value)
                                : new Intl.NumberFormat('fa-IR', { notation: 'compact' }).format(Number(value))
                    },
                    grid: {
                        color: '#e2e8f088'
                    }
                },
                y: {
                    ticks: {
                        color: '#64748b',
                        callback: (value: number | string) =>
                            horizontal
                                ? new Intl.NumberFormat('fa-IR', { notation: 'compact' }).format(Number(value))
                                : String(value)
                    },
                    grid: {
                        color: '#e2e8f055'
                    }
                }
            }
        };
    }

    onMount(() => {
        chart = new Chart(canvas, {
            type: 'bar',
            data: cloneData(data) as any,
            options: buildOptions()
        });

        return () => chart?.destroy();
    });

    $effect(() => {
        if (chart && data) {
            chart.data = cloneData(data) as any;
            chart.options = buildOptions() as any;
            chart.update();
        }
    });
</script>

<div class="relative h-full w-full">
    <canvas bind:this={canvas}></canvas>
</div>
