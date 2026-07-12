<template>
  <div class="register-body min-vh-100 d-flex justify-content-center align-items-center">
    <div class="card shadow-sm p-4" style="width: 100%; max-width: 450px; border-radius: 16px; background-color: #F7F3E9; border: 1px solid #E6DEC9;">
      <div class="text-center mb-4">
        <h2 class="fw-bold" style="color: tomato; letter-spacing: -0.5px;">AuraTrek</h2>
        <p class="small" style="color: tomato;">Create your Trekker account to explore trails</p>
      </div>

      <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success py-2 small" role="alert">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">Name</label>
          <input type="text" class="form-control" v-model="name" placeholder="Rajesh Kumar" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">Email</label>
          <input type="email" class="form-control" v-model="email" placeholder="rajesh@example.com" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">Phone</label>
          <input type="text" class="form-control" v-model="phone" placeholder="1234567890" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">City</label>
          <input type="text" class="form-control" v-model="city" placeholder="Pune" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">Age</label>
          <input type="number" class="form-control" v-model="age" placeholder="20" required>
        </div>

        <div class="mb-3 text-start">
          <label class="form-label small fw-semibold" style="color: tomato;">Password</label>
          <input type="password" class="form-control" v-model="password" placeholder="********" required>
        </div>

        <button type="submit" class="btn w-100 fw-bold mt-2 text-white" :disabled="isLoading" style="background-color: #007bff; border: none;">
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          Register Account
        </button>
      </form>

      <div class="text-center mt-4">
        <p class="small" style="color: tomato;">Have an Account with us??? 
          <router-link to="/" class="fw-semibold text-decoration-none" style="color: tomato;">Enter the chat</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const name = ref('')
    const email = ref('')
    const password = ref('')
    const phone = ref('')
    const city = ref('')
    const age = ref('')
    const errorMessage = ref('')
    const successMessage = ref('')
    const isLoading = ref(false)

    const handleRegister = async () => {
      errorMessage.value = ''
      successMessage.value = ''
      
      if (password.value.length < 6) {
        errorMessage.value = "Password must be greater than 6 characters."
        return
      }

      isLoading.value = true

      try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name.value, email: email.value, password: password.value, phone: phone.value, city: city.value, age: age.value, role: 'trekker' })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.message || 'Registration failed')
        }

        successMessage.value = "Registration Successful, You can login now....!"

        name.value = ''
        email.value = ''
        password.value = ''
        phone.value = ''
        city.value = ''
        age.value = ''

        setTimeout(() => {
          router.push('/')
        }, 2000)
      } catch (error) {
        errorMessage.value = error.message
      } finally {
        isLoading.value = false
      }
    }

    return { name, email, password, phone, city, age, errorMessage, successMessage, isLoading, handleRegister }
  }
}
</script>

<style scoped>
.register-body {
  background-color: #f7f3e9;
}
</style>