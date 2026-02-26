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
            interaction: {
                mode: 'index' as const,
                intersect: false
            },
            animation: {
                duration: 850,
                easing: 'easeOutQuart' as const
            },
            elements: {
                line: {
                    borderWidth: 2.5
                },
                point: {
                    radius: 2,
                    hoverRadius: 5,
                    hitRadius: 24
                }
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
                    displayColors: true,
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
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: '#e2e8f055'
                    }
                },
                y: {
                    ticks: {
                        color: '#64748b',
                        callback: (value: number | string) =>
                            new Intl.NumberFormat('fa-IR', { notation: 'compact' }).format(Number(value))
                    },
                    grid: {
                        color: '#e2e8f088'
                    }
                }
            }
        };
    }

    onMount(() => {
        chart = new Chart(canvas, {
            type: 'line',
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
