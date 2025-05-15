import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
export default defineNuxtConfig({
	build: {
		transpile: ['vuetify'],
	  },
	modules: [
		(_options, nuxt) => {
			nuxt.hooks.hook('vite:extendConfig', (config) => {
			  // @ts-expect-error
			  config.plugins.push(vuetify({ autoImport: true }))
			})
		  },
		"@nuxt/eslint",
		"@nuxt/fonts",
		"@nuxt/icon",
		"@nuxt/ui"
	],
	devtools: { enabled: true },
	vite: {
		vue: {
			template: {
				transformAssetUrls,
			}
		},
		plugins: [require('vite-tsconfig-paths').default()]
	},
	ui: {
		prefix: 'Nuxt',
	},
	compatibilityDate: "2024-11-01",
	eslint: {
		config: {
			stylistic: {
				semi: true,
				quotes: "double",
				commaDangle: "always-multiline",
				indent: "tab",
			},
		},
	},
});
