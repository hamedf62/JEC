const API_BASE = '/api';

export interface AnalysisResult {
    file_type: string;
    analysis_type: string;
    data: Record<string, unknown>;
    timestamp: string;
    cache_key: string;
}

export async function getAnalysis(
    fileType: string,
    analysisType: string
): Promise<AnalysisResult> {
    const response = await fetch(
        `${API_BASE}/analysis/${encodeURIComponent(fileType)}/${encodeURIComponent(analysisType)}`
    );
    if (!response.ok) {
        throw new Error(`API error ${response.status}: ${response.statusText}`);
    }
    return response.json();
}

export async function getSummary(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE}/summary`);
    if (!response.ok) {
        throw new Error(`API error ${response.status}: ${response.statusText}`);
    }
    return response.json();
}

export function formatDate(dateStr: string | null | undefined): string {
    if (!dateStr) return '-';
    return String(dateStr);
}

export function formatAmount(amount: number | null | undefined): string {
    if (amount === null || amount === undefined || isNaN(Number(amount))) return '0';
    return new Intl.NumberFormat('fa-IR').format(Number(amount));
}

export function formatNumber(num: number | null | undefined): string {
    if (num === null || num === undefined || isNaN(Number(num))) return '0';
    return new Intl.NumberFormat('fa-IR').format(Number(num));
}
