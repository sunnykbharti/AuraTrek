<template>
  <div class="trekker-wrapper">
    <nav class="navbar px-4 shadow-sm">
      <span class="navbar-brand fw-bold fs-4">AuraTrek</span>
      <div class="d-flex align-items-center">
        <span class="user-badge fw-semibold small px-3 py-2 rounded-pill">
          Explorer: {{ current_user_name }}
        </span>
      </div>
    </nav>

    <div class="sidebar shadow-sm">
      <div>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'explore' }" @click.prevent="switchTab('explore')">🧭 Explore</a>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'history' }" @click.prevent="switchTab('history')">📜 Trek History</a>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'profile' }" @click.prevent="switchTab('profile')">👤 Profile</a>
      </div>
      <div>
        <hr class="sidebar-divider">
        <button @click="handleLogout" class="btn btn-logout w-100 fw-bold d-flex align-items-center justify-content-center">
          🚪 Logout Now
        </button>
      </div>
    </div>

    <div class="main-content">
      <div class="container-fluid">

        <div v-if="successMessage" class="alert alert-success py-2 small shadow-sm" role="alert">
          🎉 {{ successMessage }}
        </div>
        <div v-if="error" class="alert alert-danger py-2 small shadow-sm" role="alert">
          ⚠️ {{ error }}
        </div>

        <div v-if="currentTab === 'explore'">
          <div class="mb-4">
            <h2 class="fw-bold mb-1 text-dark">Discover New Horizons</h2>
            <p class="text-muted small">Search, filter, and book approved upcoming trek paths instantly</p>
          </div>

          <div class="card p-3 mb-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label small fw-semibold text-muted">Search Location / Trail name</label>
                <input type="text" class="form-control form-control-sm" placeholder="e.g. Manali, Kedarnath...." v-model="filters.search">
              </div>
              <div class="col-md-4">
                <label class="form-label small fw-semibold text-muted">Difficulty Level</label>
                <select class="form-select form-select-sm" v-model="filters.difficulty">
                  <option value="">All</option>
                  <option value="easy">Easy</option>
                  <option value="moderate">Moderate</option>
                  <option value="difficult">Difficult</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label small fw-semibold text-muted">Max Duration (Days)</label>
                <input type="number" class="form-control form-control-sm" placeholder="e.g. 5" v-model.number="filters.maxDuration" min="1">
              </div>
            </div>
          </div>

          <div class="row g-4">
            <div class="col-md-6 col-lg-4" v-for="trek in filteredTreks" :key="trek.t_id">
              <div class="card path-card p-4 shadow-sm h-100 border-0 d-flex flex-column justify-content-between">
                <div>
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge bg-secondary-subtle text-secondary text-uppercase tracking-wider py-1.5 px-2">
                      {{ trek.t_difficulty }}
                    </span>
                    <span class="badge bg-primary-subtle text-primary text-uppercase tracking-wider py-1.5 px-2">
                      👥 {{ trek.t_slots }} Slots left
                    </span>
                  </div>
                  <h4 class="fw-bold text-dark mb-1">{{ trek.t_name }}</h4>
                  <p class="text-muted small">📍 {{ trek.t_location }}</p>
                </div>

                <div class="border-top pt-3 mt-3">
                  <div class="d-flex justify-content-between align-items-center mb-3 text-secondary small">
                    <span>⏱️ <strong>{{ trek.t_duration }} Days</strong></span>
                  </div>
                  <button @click="bookTrekSlot(trek.t_id)" class="btn btn-sm btn-primary w-100 fw-bold py-2" :disabled="trek.t_slots <= 0">
                    {{ trek.t_slots <= 0 ? '🚫 Fully Booked' : '🎒 Book my Slot' }}
                  </button>
                </div>
              </div>
            </div>

            <div class="col-12 text-center py-5 text-muted" v-if="filteredTreks.length === 0">
              <h3>🧭 No Treks Found</h3>
              <p class="small">No upcoming treks match your search criteria. Please adjust your filters and try again.</p>
            </div>
          </div>
        </div>

        <div v-if="currentTab === 'history'">
          <div class="mb-4">
            <h2 class="fw-bold mb-1 text-dark">My Booking Expeditions History</h2>
            <p class="text-muted small">Monitor tracking updates and previous trail allocation parameters</p>
          </div>

          <div class="mb-4 d-flex justify-content-between align-items-center">
            <div>
              <h2 class="fw-bold mb-1 text-dark">My Expedition Bookings</h2>
              <p class="text-muted small">Track status parameters of your active and previous slots</p>
            </div>
            <!-- Trigger Batch Export button -->
             <button @click="triggerBatchCSVExport" class="btn btn-dark fw-bold btn-sm px-3">
              Export history as CSV
             </button>
          </div>

          <div class="card p-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
            <table class="table align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Expedition Trail Target</th>
                  <th>Request Process Date</th>
                  <th>Tracking Status Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in bookingHistory" :key="booking.a_id">
                  <td class="fw-bold">{{ booking.trek_name }}</td>
                  <td>{{ booking.date_applied }}</td>
                  <td>
                    <span class="badge py-1.5 px-2.5 rounded-pill text-uppercase" :class="booking.status === 'APPLIED' ? 'bg-warning text-dark' : 'bg-success text-white'">
                      {{ booking.status }}
                    </span>
                  </td>
                </tr>
                <tr v-if="bookingHistory.length === 0">
                  <td colspan="3" class="text-center text-muted py-4">You have no upcoming or past booked treks yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="currentTab === 'profile'">
          <div class="mb-4">
            <h2 class="fw-bold mb-1 text-dark">Profile Settings</h2>
            <p class="text-muted small">Synchronize metadata values used for expedition validation criteria</p>
          </div>

          <div class="card p-4 shadow-sm border-0 bg-white max-profile-width" style="border-radius:12px;">
            <form @submit.prevent="updateUserProfile">
              <div class="row g-3">
                <div class="col-md-12">
                  <label class="form-label small fw-semibold">Full Profile Name</label>
                  <input type="text" class="form-control" v-model="profileForm.name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Contact Phone Number</label>
                  <input type="number" class="form-control" v-model="profileForm.phone" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Age (Years)</label>
                  <input type="number" class="form-control" v-model="profileForm.age" required min="10">
                </div>
                <div class="col-md-12">
                  <label class="form-label small fw-semibold">Home City Location</label>
                  <input type="text" class="form-control" v-model="profileForm.city" required>
                </div>
              </div>
              <div class="mt-4 text-end">
                <button type="submit" class="btn btn-sm btn-primary fw-bold px-4 py-2">💾 Save Profile Details</button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'UserDashboard',
  setup() {
    const router = useRouter()
    const currentTab = ref('explore')
    const error = ref('')
    const successMessage = ref('')
    const current_user_name = ref('')

    const openTrekList = ref([])
    const bookingHistory = ref([])
    
    const filters = ref({ search: '', difficulty: '', maxDuration: null })
    const profileForm = ref({ name: '', phone: '', age: '', city: '' })

    const getHeaders = () => {
      const token = localStorage.getItem('token')
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }

    const fetchAvailableTreks = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/treks', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        openTrekList.value = data
      } catch(err) {
        error.value = err.message || 'Retrieval error'
      }
    }

    const fetchMyHistory = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/user/bookings', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        bookingHistory.value = data
      } catch (err) {
        error.value = err.message || "Failed to sync booking data log"
      }
    }

    const fetchUserProfile = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/user/profile', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (response.ok) profileForm.value = data
      } catch (err) { /* Silent Handle */ }
    }

    const filteredTreks = computed(() => {
      return openTrekList.value.filter(trek => {
        const matchesSearch = trek.t_name.toLowerCase().includes(filters.value.search.toLowerCase()) || 
                             trek.t_location.toLowerCase().includes(filters.value.search.toLowerCase())
        const matchesDifficulty = !filters.value.difficulty || 
                                 trek.t_difficulty.toLowerCase() === filters.value.difficulty.toLowerCase()
        const matchesDuration = !filters.value.maxDuration || trek.t_duration <= filters.value.maxDuration
        return matchesSearch && matchesDifficulty && matchesDuration
      })
    })

    // Corrected Endpoint Endpoint Mapping Context
    const bookTrekSlot = async (trekId) => {
      error.value = ''
      successMessage.value = ''
      if (!confirm('Are you sure you want to book a slot for this trek?')) return
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/user/book/${trekId}`, {
          method: 'POST',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        
        successMessage.value = "Booking Applied Successfully! Check your trek history tab."
        await fetchAvailableTreks() 
      } catch(err) {
        error.value = err.message || 'Booking failed'
      }
    }

    const updateUserProfile = async () => {
      error.value = ''
      successMessage.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/user/profile', {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify(profileForm.value)
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        successMessage.value = "Profile metrics synchronized successfully!"
      } catch (err) {
        error.value = err.message || "Profile updates sync failed"
      }
    }

    const switchTab = (tabName) => {
      currentTab.value = tabName
      error.value = ''
      successMessage.value = ''
      if (tabName === 'explore') fetchAvailableTreks()
      if (tabName === 'history') fetchMyHistory()
      if (tabName === 'profile') fetchUserProfile()
    }

    const handleLogout = () => {
      localStorage.clear()
      router.push('/')
    }

    const triggerBatchCSVExport = async () => {
      error.value = ''
      successMessage.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/user/export-history',{
          method: 'POST',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)

        successMessage.value = data.message
      }
      catch (err) {
        error.value = err.message || "Export failed"
      }
      }

    onMounted(() => {
      const token = localStorage.getItem('token')
      current_user_name.value = localStorage.getItem('username')
      if (!token) {
        router.push('/')
      } else {
        fetchAvailableTreks()
      }
    })

    return {
      currentTab, successMessage, error, current_user_name, filters, filteredTreks, 
      bookingHistory, profileForm, switchTab, bookTrekSlot, updateUserProfile, handleLogout,
      triggerBatchCSVExport
    }
  }
}
</script>

<style scoped>
.trekker-wrapper { background-color: #fdfbf7; min-height: 100vh; }
.navbar { background-color: #ffffff; border-bottom: 1px solid #ebdcb9; height: 65px; position: fixed; top: 0; left: 0; right: 0; z-index: 1030; }
.navbar-brand { color: #ee710a; }
.user-badge { background-color: #fff3e0; color: #e65100; }

.sidebar { width: 260px; height: calc(100vh - 65px); background-color: #efede7; border-right: 1px solid #d69c0c; position: fixed; top: 65px; left: 0; display: flex; flex-direction: column; justify-content: space-between; padding: 20px; z-index: 1020; }
.sidebar-divider { border-top: 1px solid #dcd9cf; }
.nav-link-custom { display: block; padding: 12px 15px; color: #4a4438; text-decoration: none; font-weight: 600; border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; }
.nav-link-custom:hover, .nav-link-custom.active { background-color: #ee710a; color: #ffffff !important; }

.main-content { margin-left: 260px; padding: 40px; margin-top: 65px; min-height: calc(100vh - 65px); background-color: #f4ebd9; }
.path-card { background-color: #ffffff; border-radius: 12px; transition: transform 0.2s ease; }
.path-card:hover { transform: scale(1.02); }
.max-profile-width { max-width: 600px; }
.btn-logout { background-color: #d9534f; color: white; padding: 11px; border-radius: 8px; border: none; }
</style>