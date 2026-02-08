# JEC Financial Analysis Frontend

Professional dashboard built with **Svelte 5**, **SvelteKit**, **Tailwind CSS v4**, and **daisyUI 5**.

## Features
- 📊 **Responsive Dashboard**: Built with the daisyUI Drawer component.
- 🎨 **Modern UI**: Tailwind CSS v4 engine with daisyUI 5 beta.
- 🧩 **Modular Components**: Lucide icons and Svelte 5 snippets/runes.
- 🌑 **Theme Support**: Includes light and dark mode support.

## Project Structure
- `src/routes/+layout.svelte`: Main dashboard shell with sidebar and navbar.
- `src/routes/+page.svelte`: Executive overview and statistics.
- `src/routes/invoices/`: Sales analysis (Placeholder).
- `src/routes/payable/`: Accounts payable analysis (Placeholder).
- `src/routes/performa/`: Proforma documentation analysis (Placeholder).

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

## Production Build

```bash
npm run build
npm run preview
```

## Integration with Backend
This frontend is designed to work with the Python-based analysis backend. Future steps involve creating a REST API (using FastAPI or similar) to serve the processed data from `DataAnalyzer`.
