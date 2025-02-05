/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'
// Components
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import DatePicker from 'primevue/datepicker';
import 'primeicons/primeicons.css'; 

// Composables
import { createApp } from 'vue'

const app = createApp(App)
app.use(PrimeVue);  // Use PrimeVue configuration
app.component('DatePicker', DatePicker);  

registerPlugins(app)
app.use(router)
app.mount('#app')
