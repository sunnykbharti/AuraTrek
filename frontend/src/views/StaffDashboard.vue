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
                <!-- <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'routes' }" @click.prevent="switchTab('routes')">🗺️ Trek Routes</a>
                <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'users' }" @click.prevent="switchTab('users')">👥 Manage Users</a>
                <a href="#" class="nav-link-custom" :class="{ active: currentTab === 'staff' }" @click.prevent="switchTab('staff')">🧑‍💼 Manage Staff</a> -->
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
                 <div v-if="currentTab === 'dashbaord'">
                    <div class="mb-4">
                        <h2 class="fw-bold mb-1 text-dark"> My Expeditions </h2>
                        <p class="text-muted small"> Trek routes assigned to yout supervision </p>
                    </div>

                    <!-- Trek Cards Display -->
                    <div class="row g-4">
                        <div class="col-md-6 col-lg-4" v-for="trek in myTreks" :key="trek.t_id">
                            <div class="card trek-card p-4 shadow-sm border-0">
                                <span class="badge bg-secondary-subtle text-secondary text-uppercase tracking-wider mb-2 align-slef-start py-1.5 px-2">
                                    {{  trek.t_difficulty }}
                                </span>
                                <h4 class="fw-bold mb-1 text-dark">{{ trek.t_name }}</h4>
                                <p class="text-muted small mb-3">📍 {{  trek.t_location }}</p>

                                <div class="d-flex justify-content-between border-top pt-3 small text-secondary">
                                    <span>⏱️ <strong>{{  trek.t_duration }} Days</strong></span>
                                    <span>👥 <strong>{{  trek.t_slots }} Slots left</strong></span>
                                </div>
                            </div>
                        </div>

                        <!-- Case when no allotted treks -->
                        <div class="col-12 text-center py-5 text-muted" v-if="myTreks.length === 0">
                            <h3> No Active Expeditions  </h3>
                            <p class="small">You haven't been assigned to any upcoming trek routes yet. Check back later!!!!!</p>
                        </div>
                    </div>

                    <!-- Container for error (if any) -->
                    <div v-if="error" class="alert alert-danger py-2 small mt-4 shadow-sm" role="alert">
                        {{ error }}
                    </div>
                 </div>
            </div>
           </div>
    </div>
</template>

<script>
import { ref,onMounted } from 'vue';
import { useRouter } from 'vue-router'

export default {
    name: 'StaffDashboard',
    setup() {
        const router = useRouter()
        const myTreks = ref([])
        const current_staff_name = ref('')
        const error = ref('')

        const fetchAssignedTreks = async () => {
            const token = localStorage.getItem('token')
            current_staff_name.value = localStorage.getItem('username')

            if (!token) {
                router.push('/')
                return
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/api/staff/my-treks', {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ${token}',
                        'Content-Type': 'application/json'
                    }
                })
                const data = await response.json()
                if (!response.ok) throw new Error(data.message)

                myTreks.value = data
            } catch (err) {
                error.value = err.message || "Failed to load data"
            }
        }

        const switchTab = (tabName) =>)

        const handleLogout = () => {
            localStorage.clear()
            router.push('/')
        }

        onMounted(() => {
            fetchAssignedTreks()
        })

        return {
            myTreks,
            current_staff_name,
            error,
            handleLogout
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
.trek-card { background-color: #ffffff; border-radius: 12px; border-top: 4px solid #2b7a78 !important; }
.btn-logout { background-color: #d9534f; color: white; padding: 11px; border-radius: 8px; border: none; }
</style>