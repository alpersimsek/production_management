import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
axios.defaults.headers.common['Content-Type'] = 'application/json'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

app.mount('#app')
