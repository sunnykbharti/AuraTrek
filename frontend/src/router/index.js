import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/admin-dashboard',
      name: 'admin-dashboard',
      // Lazy loading for the dashboard view
      component: () => import('../views/AdminDashboard.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/staff-dashboard',
      name: 'staff-dashboard',
      component: () => import('../views/StaffDashboard.vue')
    },
    {
      path: '/user-dashboard',
      name: 'user-dashboard',
      component: () => import('../views/UserDashboard.vue')
    }
  ]
})

export default router