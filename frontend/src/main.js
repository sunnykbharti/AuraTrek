import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import Bootstrap CSS and JS bundle globally
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min'

const app = createApp(App)

app.use(router)
app.mount('#app')
