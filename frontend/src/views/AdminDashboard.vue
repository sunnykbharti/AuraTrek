<template>
  <div class="admin-wrapper">
    <!-- uppermost navigation bar having app name and user username -->
    <nav class="navbar px-4 shadow-sm">
      <span class="navbar-brand fw-bold fs-4">AuraTrek</span>
      <div class="d-flex align-items-center">
        <span class="admin-badge fw-semibold small px-3 py-2 rounded-pill">
          👤 {{ current_admin_name }}
        </span>
      </div>
    </nav>

    <!-- Sidebar Navigation -->
    <div class="sidebar shadow-sm">
      <div>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'dashboard' }" @click.prevent="switchTab('dashboard')">📊 Dashboard</a>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'routes' }" @click.prevent="switchTab('routes')">🗺️ Trek Routes</a>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'users' }" @click.prevent="switchTab('users')">👥 Manage Users</a>
        <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'staff' }" @click.prevent="switchTab('staff')">🧑‍💼 Manage Staff</a>
      </div>
      <div>
        <hr class="sidebar-divider">
        <button @click="handleLogout" class="btn btn-logout w-100 fw-bold d-flex align-items-center justify-content-center">
          🚪 Logout
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <div class="container-fluid">
        
        <!-- Tab 1: Live Overview Dashboard -->
        <div v-if="currentTab === 'dashboard'">
          <div class="mb-4">
            <h2 class="fw-bold mb-1 text-dark">Overview</h2>
            <p class="text-muted small">Live platform metrics and administrative statistics</p>
          </div>

          <div class="row g-4">
            <div class="col-md-6 col-lg-4">
              <div class="card metric-card p-4 shadow-sm border-0 trekker-border">
                <span class="card-label text-muted small fw-bold text-uppercase tracking-wider">Total Active Trekkers</span>
                <h1 class="fw-bold mt-2 display-5 text-dark">{{ app_data.totalTrekkers }}</h1>
              </div>
            </div>
            <div class="col-md-6 col-lg-4">
              <div class="card metric-card p-4 shadow-sm border-0 staff-border">
                <span class="card-label text-muted small fw-bold text-uppercase tracking-wider">Registered Staff</span>
                <h1 class="fw-bold mt-2 display-5 text-dark">{{ app_data.totalStaff }}</h1>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Trek Routes Configuration -->
        <div v-if="currentTab === 'routes'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 class="fw-bold mb-1 text-dark">Trek Routes</h2>
              <p class="text-muted small">Create, modify, or remove available trails</p>
            </div>
            <button @click="openTrekModal()" class="btn btn-primary fw-bold">+ Create New Route</button>
          </div>

          <!-- Route Management Form Modal Backdrop -->
          <div v-if="showTrekModal" class="custom-modal shadow p-4 mb-4 bg-white border rounded">
            <h4 class="fw-bold text-dark mb-3">{{ editingTrekId ? 'Update Trek Details' : 'Create New Trek Route' }}</h4>
            <form @submit.prevent="saveTrekRoute">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Trek Name</label>
                  <input type="text" class="form-control" v-model="trekForm.t_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-semibold">Location</label>
                  <input type="text" class="form-control" v-model="trekForm.t_location" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">Difficulty</label>
                  <select class="form-select" v-model="trekForm.t_difficulty" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Difficult">Difficult</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">Duration (Days)</label>
                  <input type="number" class="form-control" v-model="trekForm.t_duration" required min="1">
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">Available Slots</label>
                  <input type="number" class="form-control" v-model="trekForm.t_slots" required min="1">
                </div>
                <!-- Connected Staff Assignment Selector Inside Form Wrap -->
                <div class="col-md-12">
                  <label class="form-label small fw-semibold">Assign Staff Guide</label>
                  <select class="form-select" v-model="trekForm.t_staff">
                    <option :value="null">None (Leave Unassigned)</option>
                    <option v-for="staff in availableStaffOptions" :key="staff.u_id" :value="staff.u_id">
                      {{ staff.username }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="mt-3 text-end">
                <button type="button" @click="showTrekModal = false" class="btn btn-sm btn-secondary me-2">Cancel</button>
                <button type="submit" class="btn btn-sm btn-primary">Save Changes</button>
              </div>
            </form>
          </div>

          <!-- Active Trek Routes Display Table -->
          <div class="card p-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
            <table class="table align-middle">
              <thead class="table-light">
                <tr>
                  <th>Trek Name</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Duration</th>
                  <th>Slots</th>
                  <th>Assigned Staff</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trek in treksList" :key="trek.t_id">
                  <td class="fw-bold">{{ trek.t_name }}</td>
                  <td>{{ trek.t_location }}</td>
                  <td><span class="badge bg-secondary">{{ trek.t_difficulty }}</span></td>
                  <td>{{ trek.t_duration }} Days</td>
                  <td>{{ trek.t_slots }} slots</td>
                  <td>{{ getStaffName(trek.t_staff) }}</td>
                  <td class="text-end">
                    <button @click="openTrekModal(trek)" class="btn btn-sm btn-outline-secondary me-2">✏️ Edit</button>
                    <button @click="deleteTrekRoute(trek.t_id)" class="btn btn-sm btn-outline-danger">🗑️ Delete</button>
                  </td>
                </tr>
                <tr v-if="treksList.length === 0">
                  <td colspan="7" class="text-center text-muted py-3">No trek routes available. Click create to add one!</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab 3: Accounts System Moderation Panel (Users) -->
        <div v-if="currentTab === 'users'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 class="fw-bold mb-1 text-dark">Manage Trekkers</h2>
              <p class="text-muted small">Search, deactivate, or blacklist accounts live on platform criteria</p>
            </div>
            <input type="text" class="form-control w-25 search-bar" placeholder="🔍 Search accounts..." v-model="searchQuery">
          </div>

          <div class="card p-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
            <table class="table align-middle">
              <thead class="table-light">
                <tr>
                  <th>User Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th class="text-end">Moderation</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in filteredAccounts" :key="account.u_id">
                  <td>{{ account.username }}</td>
                  <td><span class="badge bg-dark-subtle text-dark text-uppercase">{{ account.u_role }}</span></td>
                  <td>
                    <span class="badge" :class="account.u_status === 'active' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
                      {{ account.u_status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button @click="toggleAccountStatus(account.u_id)" class="btn btn-sm" :class="account.u_status === 'active' ? 'btn-outline-danger' : 'btn-outline-success'">
                      {{ account.u_status === 'active' ? '⛔ Deactivate / Blacklist' : '✅ Reactivate' }}
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredAccounts.length === 0">
                  <td colspan="4" class="text-center text-muted py-3">No matching accounts found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab 4: Manage Staff Members -->
        <div v-if="currentTab === 'staff'">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 class="fw-bold mb-1 text-dark">Manage Staff Members</h2>
              <p class="text-muted small">Search accounts or onboard a new internal team guide</p>
            </div>
            <div class="d-flex gap-2 w-50 justify-content-end">
              <input type="text" class="form-control w-50 search-bar" placeholder="🔍 Search staff..." v-model="searchQuery">
              <button @click="showStaffForm = !showStaffForm" class="btn btn-primary fw-bold btn-sm px-3">
                {{ showStaffForm ? '✕ Close Form' : '➕ Add Staff' }}
              </button>
            </div>
          </div>

          <!-- Inline Staff Registration Form Panel -->
          <div v-if="showStaffForm" class="card p-4 mb-4 border-0 shadow-sm bg-white" style="border-radius:12px; border: 1px solid #ebdcb9 !important;">
            <h5 class="fw-bold text-dark mb-3">Onboard New Staff Member</h5>
            <form @submit.prevent="submitStaffRegistration">
              <div class="row g-3 align-items-end">
                <div class="col-md-5">
                  <label class="form-label small fw-semibold">Staff Email Address</label>
                  <input type="email" class="form-control form-control-sm" v-model="staffForm.email" placeholder="guide@auratrek.com" required>
                </div>
                <div class="col-md-5">
                  <label class="form-label small fw-semibold">Temporary Password</label>
                  <input type="password" class="form-control form-control-sm" v-model="staffForm.password" placeholder="********" required minlength="6">
                </div>
                <div class="col-md-2">
                  <button type="submit" class="btn btn-sm btn-dark w-100 fw-bold py-2">Create Account</button>
                </div>
              </div>
            </form>
          </div>

          <!-- Existing Staff Display Table -->
          <div class="card p-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
            <table class="table align-middle">
              <thead class="table-light">
                <tr>
                  <th>User Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th class="text-end">Moderation</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in filteredAccounts" :key="account.u_id">
                  <td>{{ account.username }}</td>
                  <td><span class="badge bg-dark-subtle text-dark text-uppercase">{{ account.u_role }}</span></td>
                  <td>
                    <span class="badge" :class="account.u_status === 'active' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
                      {{ account.u_status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button @click="toggleAccountStatus(account.u_id)" class="btn btn-sm" :class="account.u_status === 'active' ? 'btn-outline-danger' : 'btn-outline-success'">
                      {{ account.u_status === 'active' ? '⛔ Deactivate / Blacklist' : '✅ Reactivate' }}
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredAccounts.length === 0">
                  <td colspan="4" class="text-center text-muted py-3">No staff records matching your search queries found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Global Alert Banner -->
        <div v-if="error" class="alert alert-danger py-2 small mt-4 shadow-sm" role="alert">
          ⚠️ {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminDashboard',
  setup() {
    const router = useRouter()
    
    const currentTab = ref('dashboard')
    const searchQuery = ref('')
    const error = ref('')
    const current_admin_name = ref('')
    
    const app_data = ref({ totalTrekkers: 0, totalStaff: 0 })
    const accountsList = ref([]) 
    const treksList = ref([])    

    const showTrekModal = ref(false)
    const editingTrekId = ref(null)
    const trekForm = ref({ t_name: '', t_location: '', t_difficulty: 'Easy', t_duration: 1, t_slots: 10, t_staff: null })

    const showStaffForm = ref(false)
    const staffForm = ref({ email: '', password: '' })

    const availableStaffOptions = computed(() => {
      return accountsList.value.filter(acc => acc.u_role === 'staff' && acc.u_status === 'active')
    })

    const getHeaders = () => {
      const token = localStorage.getItem('token')
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }

    const getStaffName = (staffId) => {
      if (!staffId) return 'Unassigned'
      const staff = accountsList.value.find(acc => acc.u_id === staffId)
      return staff ? staff.username : `Staff ID: ${staffId}`
    }

    const fetchDashboard = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/dashboard', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        app_data.value = data.app_data
      } catch (err) {
        error.value = err.message || "Failed to load dashboard metrics statistics."
      }
    }

    const fetchAccounts = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/accounts', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        accountsList.value = data
      } catch (err) {
        error.value = err.message || "Failed to retrieve registered profiles."
      }
    }

    const fetchTreks = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/treks', {
          method: 'GET',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        treksList.value = data
      } catch (err) {
        error.value = err.message || "Failed to sync active trail networks."
      }
    }

    const switchTab = (tabName) => {
      currentTab.value = tabName
      searchQuery.value = ''
      if (tabName === 'dashboard') fetchDashboard()
      if (tabName === 'routes') {
        fetchTreks()
        fetchAccounts()
      }
      if (tabName === 'users' || tabName === 'staff') fetchAccounts()
    }

    const filteredAccounts = computed(() => {
      const targetRole = currentTab.value === 'users' ? 'trekker' : 'staff'
      return accountsList.value.filter(account => {
        const matchesRole = account.u_role === targetRole
        const matchesQuery = account.username.toLowerCase().includes(searchQuery.value.toLowerCase())
        return matchesRole && matchesQuery
      })
    })

    const toggleAccountStatus = async (userId) => {
      error.value = ''
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/admin/accounts/toggle/${userId}`, {
          method: 'POST',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        await fetchAccounts()
        await fetchDashboard()
      } catch (err) {
        error.value = err.message || "Account status modification failed."
      }
    }

    const submitStaffRegistration = async () => {
      error.value = ''
      try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/staff/register', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify(staffForm.value)
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)

        staffForm.value = { email: '', password: '' }
        showStaffForm.value = false
        await fetchAccounts()
        await fetchDashboard()
      } catch (err) {
        error.value = err.message || "Failed to complete staff onboarding setup sequence."
      }
    }

    const openTrekModal = (trek = null) => {
      if (trek) {
        editingTrekId.value = trek.t_id
        trekForm.value = { ...trek }
      } else {
        editingTrekId.value = null
        trekForm.value = { t_name: '', t_location: '', t_difficulty: 'Easy', t_duration: 1, t_slots: 10, t_staff: null }
      }
      showTrekModal.value = true
    }

    const saveTrekRoute = async () => {
      error.value = ''
      const isEditing = editingTrekId.value !== null
      const url = isEditing 
        ? `http://127.0.0.1:5000/api/admin/treks/${editingTrekId.value}`
        : 'http://127.0.0.1:5000/api/admin/treks'
      
      const method = isEditing ? 'PUT' : 'POST'

      try {
        const response = await fetch(url, {
          method: method,
          headers: getHeaders(),
          body: JSON.stringify(trekForm.value)
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)

        showTrekModal.value = false
        editingTrekId.value = null
        await fetchTreks()
      } catch (err) {
        error.value = err.message || "Failed to finalize trek trail adjustments."
      }
    }

    const deleteTrekRoute = async (trekId) => {
      if (!confirm("Are you sure you want to delete this trek route completely?")) return
      error.value = ''
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/admin/treks/${trekId}`, {
          method: 'DELETE',
          headers: getHeaders()
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.message)
        await fetchTreks()
      } catch (err) {
        error.value = err.message || "Failed to remove selected destination route."
      }
    }

    const handleLogout = () => {
      localStorage.clear()
      router.push('/')
    }

    onMounted(() => {
      const token = localStorage.getItem('token')
      current_admin_name.value = localStorage.getItem('username')
      if (!token) {
        router.push('/')
      } else {
        fetchDashboard()
      }
    })

    return {
      currentTab, searchQuery, error, current_admin_name, app_data, accountsList, treksList,
      showTrekModal, editingTrekId, trekForm, filteredAccounts, switchTab,
      openTrekModal, saveTrekRoute, deleteTrekRoute, toggleAccountStatus, handleLogout,
      showStaffForm, staffForm, submitStaffRegistration, availableStaffOptions, getStaffName
    }
  }
}
</script>

<style scoped>
.admin-wrapper { background-color: #fdfbf7; min-height: 100vh; }
.navbar { background-color: #ffffff; border-bottom: 1px solid #ebdcb9; height: 65px; position: fixed; top: 0; left: 0; right: 0; z-index: 1030; }
.navbar-brand { color: #ee710a; }
.admin-badge { background-color: #f7f3e9; color: #2a261f; }

.sidebar { width: 260px; height: calc(100vh - 65px); background-color: #efede7; border-right: 1px solid #d69c0c; position: fixed; top: 65px; left: 0; display: flex; flex-direction: column; justify-content: space-between; padding: 20px; z-index: 1020; }
.sidebar-divider { border-top: 1px solid #dcd9cf; }
.nav-link-custom { display: block; padding: 12px 15px; color: #4a4438; text-decoration: none; font-weight: 600; border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; }
.nav-link-custom:hover, .nav-link-custom.active { background-color: #6e644e; color: #ffffff !important; }

.main-content { margin-left: 260px; padding: 40px; margin-top: 65px; min-height: calc(100vh - 65px); background-color: #f4ebd9; }
.search-bar { border-radius: 8px; border: 1px solid #cbd5e1; }

.metric-card { background-color: #ffffff; border-radius: 14px; transition: transform 0.2s; }
.metric-card:hover { transform: translateY(-2px); }
.trekker-border { border-left: 6px solid #6e644e !important; }
.staff-border { border-left: 6px solid #ee710a !important; }
.custom-modal { border: 1px solid #ebdcb9 !important; border-radius: 12px; }
.btn-logout { background-color: #d9534f; color: white; padding: 11px; border-radius: 8px; border: none; }
.btn-logout:hover { background-color: #c9302c; }
</style>