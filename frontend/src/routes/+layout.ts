// This dashboard app is fully client-side rendered.
// Disabling SSR here avoids bundling browser-only libraries
// (chart.js, svelte-chartjs) into the server-side bundle.
export const ssr = false;
export const prerender = false;
