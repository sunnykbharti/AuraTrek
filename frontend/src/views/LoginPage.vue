<template>
  <div class="login-body min-vh-100 d-flex justify-content-center align-items-center">
    <div class="card shadow-sm p-4" style="width:100%; max-width: 400px; border-radius: 12px; background-color: #F7F3E9; border: 1px solid #E6DEC9;">
      <div class="text-center">
        <h2 class="fw-bold" style="color: #000000; letter-spacing: -0.5px;">AuraTrek</h2>
        <p class="text-muted small">Sign in to coordinate your next adventure</p>
      </div>

      <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success py-2 small" role="alert">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: #4A4438;">Email Address</label>
          <input type="email" class="form-control" v-model="email" placeholder="name@example.com" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: #4A4438;">Password</label>
          <input type="password" class="form-control" v-model="password" placeholder="**********" required>
        </div>

        <button type="submit" class="btn btn-primary w-100 fw-bold mt-2" style="background-color:darkgoldenrod; border: none;" :disabled="isLoading">
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"  role="status"></span>
          Login
        </button>
      </form>

      <div class="text-center mt-4">
        <p class="text-muted xsmall">Are you a trekker? 
          <router-link to="/register" class="text-decoration-none">Register here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const successMessage = ref('')
    const isLoading = ref(false)

    const handleLogin = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      isLoading.value = true

      try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.value, password: password.value })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.message || "Login Failure!")
        }

        localStorage.setItem('token', data.token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('username', data.name || 'admin')

        successMessage.value = "Login Successful! Redirecting..."

        email.value = ''
        password.value = ''

        setTimeout(() => {
          if (data.role === 'admin') {
            router.push('/admin-dashboard')
          } 
          else if (data.role === 'staff') {
            router.push('/staff-dashboard')
          }
          else if (data.role === 'trekker'){
            router.push('/user-dashboard')
          }
          else {
            router.push('/')
          }

        }, 1500)

      } catch (error) {
        errorMessage.value = error.message
      } finally {
        isLoading.value = false
      }
    }

    return { email, password, errorMessage, successMessage, isLoading, handleLogin }
  }
}
</script>

<style scoped>
.login-body {
  background-color:darkorange;
}
</style>
