<template>
    <div class="staff-wrapper">
        <!-- top most bar in the view -->
         <nav class="navbar px-4 shadow-sm">
            <span class="navbar-brand fw-bold fs-4">AuraTrek</span>
            <div class="d-flex align-items-center">
                <span class="staff-badge fw-semibold small px-3 py-2 rounded-pill">
                    Guide : {{ current_staff_name }}
                </span>
            </div>
         </nav>

         <!-- Sidebar LAyout-->
          <div class="sidebar shadow-sm">
            <div>
                <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'dashboard' }" @click.prevent="switchTab('dashboard')">📊 Dashboard</a>
            </div>
            <div>
                <hr class="sidebar-divider">
                <button @click="handleLogout" class="btn btn-logout w-100 fw-bold d-flex align-items-center justify-content-center">
                🚪 Logout
                </button>
            </div>
          </div>

          <!-- Content block -->
           <div class="main-content">
            <div class="container-fluid">

                <!-- Tab1 : Staff Dashboard -->
                 <div v-if="currentTab === 'dashboard'">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h2 class="fw-bold mb-1 text-dark"> My Expeditions </h2>
                            <p class="text-muted small"> Trek routes assigned to your supervision </p>
                        </div>
                    </div>

                    <!-- Trek Update Form Modal (Slots / Status / Stage) -->
                    <div v-if="showTrekModal" class="custom-modal shadow p-4 mb-4 bg-white border rounded">
                        <h4 class="fw-bold text-dark mb-3">Update Trek Details — {{ editingTrek?.t_name }}</h4>
                        <form @submit.prevent="saveTrekEdits">
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <label class="form-label small fw-semibold">Available Slots</label>
                                    <input type="number" class="form-control" v-model.number="trekForm.t_slots" required min="0">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label small fw-semibold">Booking Status</label>
                                    <select class="form-select" v-model="trekForm.t_status">
                                        <option value="Open">Open</option>
                                        <option value="Closed">Closed</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label small fw-semibold">Trek Stage</label>
                                    <select class="form-select" v-model="trekForm.t_stage">
                                        <option value="Upcoming">Upcoming</option>
                                        <option value="Started">Started</option>
                                        <option value="Completed">Completed</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mt-3 text-end">
                                <button type="button" @click="showTrekModal = false" class="btn btn-sm btn-secondary me-2">Cancel</button>
                                <button type="submit" class="btn btn-sm btn-primary">Save Changes</button>
                            </div>
                        </form>
                    </div>

                    <!-- Applications Modal -->
                    <div v-if="showRosterModal" class="custom-modal shadow p-4 mb-4 bg-white border rounded">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4 class="fw-bold mb-0 text-dark">Applications — {{ selectedTrekContext?.t_name }}</h4>
                            <button @click="showRosterModal = false" class="btn-close shadow-none"></button>
                        </div>
                        <table class="table align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th>Trekker Email</th>
                                    <th>Applied Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="user in activeParticipantsList" :key="user.a_id">
                                    <td class="fw-semibold">{{ user.username }}</td>
                                    <td>{{ user.a_date }}</td>
                                    <td>
                                        <span class="badge text-uppercase px-2 py-1" :class="user.a_status === 'applied' ? 'bg-info-subtle text-info' : 'bg-success-subtle text-success'">
                                            {{ user.a_status }}
                                        </span>
                                    </td>
                                </tr>
                                <tr v-if="activeParticipantsList.length === 0">
                                    <td colspan="3" class="text-center text-muted py-3">No active registration applications mapped for this trail route.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Assigned Trek Routes Display Table -->
                    <div class="card p-4 shadow-sm border-0 bg-white" style="border-radius:12px;">
                        <table class="table align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th>Trek Name</th>
                                    <th>Location</th>
                                    <th>Difficulty</th>
                                    <th>Duration</th>
                                    <th>Slots</th>
                                    <th>Registered</th>
                                    <th>Status</th>
                                    <th class="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="trek in myTreks" :key="trek.t_id">
                                    <td class="fw-bold">{{ trek.t_name }}</td>
                                    <td>{{ trek.t_location }}</td>
                                    <td><span class="badge bg-secondary">{{ trek.t_difficulty }}</span></td>
                                    <td>{{ trek.t_duration }} Days</td>
                                    <td>{{ trek.t_slots }} slots</td>
                                    <td>{{ trek.registered_users || 0 }}</td>
                                    <td>
                                        <span class="badge" :class="trek.t_status === 'Closed' ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success'">
                                            {{ trek.t_status || 'Open' }}
                                        </span>
                                    </td>
                                    <td class="text-end">
                                        <button @click="openEditModal(trek)" class="btn btn-sm btn-outline-secondary me-2">✏️ Edit</button>
                                        <button @click="openRosterModal(trek)" class="btn btn-sm btn-outline-dark">👥 Applications</button>
                                    </td>
                                </tr>
                                <tr v-if="myTreks.length === 0">
                                    <td colspan="9" class="text-center text-muted py-3">No trek routes assigned to you yet. Check back later!</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Container for error (if any) -->
                    <div v-if="error" class="alert alert-danger py-2 small mt-4 shadow-sm" role="alert">
                        ⚠️ {{ error }}
                    </div>
                 </div>
            </div>
           </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
    name: 'StaffDashboard',
    setup() {
        const router = useRouter()
        const myTreks = ref([])
        const current_staff_name = ref('')
        const error = ref('')

        const currentTab = ref('dashboard')

        // Edit modal state (mirrors AdminDashboard's Trek Routes modal pattern)
        const showTrekModal = ref(false)
        const editingTrek = ref(null)
        const trekForm = ref({ t_slots: 0, t_status: 'Open' })

        // Applications modal state
        const showRosterModal = ref(false)
        const selectedTrekContext = ref(null)
        const activeParticipantsList = ref([])

        const getHeaders = () => {
            const token = localStorage.getItem('token')
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }

        const fetchAssignedTreks = async () => {
            const token = localStorage.getItem('token')
            current_staff_name.value = localStorage.getItem('username')

            if (!token) {
                router.push('/')
                return
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/api/staff/treks', {
                    method: 'GET',
                    headers: getHeaders()
                })
                const data = await response.json()
                if (!response.ok) throw new Error(data.message)

                myTreks.value = data
            } catch (err) {
                error.value = err.message || "Failed to load data"
            }
        }

        const openEditModal = (trek) => {
            editingTrek.value = trek
            trekForm.value = {
                t_slots: trek.t_slots,
                t_status: trek.t_status || 'Open'
            }
            showTrekModal.value = true
        }

        const saveTrekEdits = async () => {
            error.value = ''
            try {
                const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${editingTrek.value.t_id}`, {
                    method: 'PUT',
                    headers: getHeaders(),
                    body: JSON.stringify({
                        t_slots: trekForm.value.t_slots,
                        t_status: trekForm.value.t_status
                    })
                })
                const data = await response.json()
                if (!response.ok) throw new Error(data.message)

                showTrekModal.value = false
                editingTrek.value = null
                await fetchAssignedTreks()
            } catch (err) {
                error.value = err.message || "Failed to sync trek modifications updates."
            }
        }

        const openRosterModal = async (trek) => {
            error.value = ''
            selectedTrekContext.value = trek
            try {
                const response = await fetch(`http://127.0.0.1:5000/api/staff/treks/${trek.t_id}/participants`, {
                    method: 'GET',
                    headers: getHeaders()
                })
                const data = await response.json()
                if (!response.ok) throw new Error(data.message)

                activeParticipantsList.value = data
                showRosterModal.value = true
            } catch (err) {
                error.value = err.message || "Roster tracking table loading sequence failed."
            }
        }

        const switchTab = (tabName) => {
            currentTab.value = tabName
            if (tabName === 'dashboard') fetchAssignedTreks()
        }

        const handleLogout = () => {
            localStorage.clear()
            router.push('/')
        }

        onMounted(() => {
            fetchAssignedTreks()
        })

        return {
            myTreks,
            currentTab,
            switchTab,
            current_staff_name,
            error,
            handleLogout,
            showTrekModal,
            editingTrek,
            trekForm,
            openEditModal,
            saveTrekEdits,
            showRosterModal,
            selectedTrekContext,
            activeParticipantsList,
            openRosterModal
        }
    }
}
</script>

<style scoped>
.staff-wrapper { background-color: #fdfbf7; min-height: 100vh; }
.navbar { background-color: #ffffff; border-bottom: 1px solid #ebdcb9; height: 65px; position: fixed; top: 0; left: 0; right: 0; z-index: 1030; }
.navbar-brand { color: #2b7a78; }
.staff-badge { background-color: #e3fafc; color: #0b7285; }

.sidebar { width: 260px; height: calc(100vh - 65px); background-color: #efede7; border-right: 1px solid #ebdcb9; position: fixed; top: 65px; left: 0; display: flex; flex-direction: column; justify-content: space-between; padding: 20px; z-index: 1020; }
.sidebar-divider { border-top: 1px solid #dcd9cf; }
.nav-link-custom { display: block; padding: 12px 15px; color: #4a4438; text-decoration: none; font-weight: 600; border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; }
.nav-link-custom.active { background-color: #2b7a78; color: #ffffff !important; }

.main-content { margin-left: 260px; padding: 40px; margin-top: 65px; min-height: calc(100vh - 65px); background-color: #f4ebd9; }
.btn-logout { background-color: #d9534f; color: white; padding: 11px; border-radius: 8px; border: none; }

.custom-modal { border: 1px solid #ebdcb9 !important; border-radius: 12px; }
</style>