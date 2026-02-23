import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PdfStudioApp from './PdfStudioApp.vue'
import router from './router'
import './style.css'

const app = createApp(PdfStudioApp)
app.use(createPinia())
app.use(router)
app.mount('#pdf-studio-app')
