import { createRouter, createWebHistory } from 'vue-router'
import List from '../views/List.vue'
import Calendar from '../views/Calendar.vue'
import Dashboard from '../views/Dashboard.vue'
import Pomodoro from '../views/Pomodoro.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/list' },
    { path: '/list', component: List },
    { path: '/calendar', component: Calendar },
    { path: '/dashboard', component: Dashboard },
    { path: '/pomodoro', component: Pomodoro },
  ],
})