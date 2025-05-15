// import this after install `@mdi/font` package
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { md1 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    ssr: true,
    blueprint: md1,
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        themes: {
          light: {
            colors: {
              primary: '#1f78b4', 
              secondary: '#b2df8a'
            }
          }
        }
    },
  })
  app.vueApp.use(vuetify)
})