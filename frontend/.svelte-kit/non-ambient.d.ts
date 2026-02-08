
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/cashflow" | "/invoices" | "/payable" | "/performa" | "/receivable";
		RouteParams(): {
			
		};
		LayoutParams(): {
			"/": Record<string, never>;
			"/cashflow": Record<string, never>;
			"/invoices": Record<string, never>;
			"/payable": Record<string, never>;
			"/performa": Record<string, never>;
			"/receivable": Record<string, never>
		};
		Pathname(): "/" | "/cashflow" | "/cashflow/" | "/invoices" | "/invoices/" | "/payable" | "/payable/" | "/performa" | "/performa/" | "/receivable" | "/receivable/";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/fonts/Vazirmatn-Black.woff2" | "/fonts/Vazirmatn-Bold.woff2" | "/fonts/Vazirmatn-ExtraBold.woff2" | "/fonts/Vazirmatn-ExtraLight.woff2" | "/fonts/Vazirmatn-Light.woff2" | "/fonts/Vazirmatn-Medium.woff2" | "/fonts/Vazirmatn-Regular.woff2" | "/fonts/Vazirmatn-SemiBold.woff2" | "/fonts/Vazirmatn-Thin.woff2" | "/fonts/Vazirmatn[wght].woff2" | string & {};
	}
}