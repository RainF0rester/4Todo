<template>
    <div class="welcome-page">
        <a-card class="welcome-card">
          <div class="welcome-header">
            <div class="welcome-subtitle">Welcome to Task Tracker!</div>
            <h1>👋 Hi,{{ times }}</h1>
          </div>


      <div class="task-today-block">
        <div class="block-head">
          <h3>Today tasks</h3>
          <span class="task-count">{{ todayTasks.length }} task{{ todayTasks.length === 1 ? '' : 's' }}</span>
        </div>
        <div v-if="todayTasks.length > 0" class="task-list-header">
          <span><CarryOutOutlined />Task</span>
          <span>Due time</span>
        </div>
        <a-list
          :data-source="todayTasks"
          size="small"
          bordered
          class="task-list">
          <template #renderItem="{ item }">
            <a-list-item>
              <div class="task-item">
                <span class="task-title">{{ item.title }}</span>
                <span class="task-due-date">{{ formatDate(item.dueDate) }}</span>
              </div>
            </a-list-item>
          </template>
        </a-list>
      </div>

      <div class="actions">
        <a-button type="primary" size="large" @click="goToBoard">Go To Task Board</a-button>
        <a-button size="large" @click="goToPast">View Past Tasks</a-button>
      </div>
        </a-card>
    </div>
</template>


<script setup>

import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getTaskList } from '../api/tasks'
import { CarryOutOutlined  } from '@ant-design/icons-vue'


const router = useRouter()
const times = computed(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
})

const todayTasks = ref([])

// Check if the date is today
function isToday(dateStr) {
  if (!dateStr) return false
  const due = new Date(dateStr)
  if (Number.isNaN(due.getTime())) return false
  const now = new Date()
  return (
    due.getFullYear() === now.getFullYear() &&
    due.getMonth() === now.getMonth() &&
    due.getDate() === now.getDate()
  )
}
// Load tasks and filter today's tasks
async function loadTodayTasks() {
  try {
    const tasks = await getTaskList()
    todayTasks.value = tasks.filter((task) => isToday(task.dueDate))
  } catch (err) {
    console.error('Failed to load today tasks', err)
    todayTasks.value = []
  }
}

// Format date to HH:mm
function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('en', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}


function goToBoard() {
  router.push('/list')
}

function goToPast() {
  router.push('/dashboard')
}

onMounted(() => {
  loadTodayTasks()
})

</script>


<style scoped>
.welcome-page {
  min-height: calc(100vh - 64px);
  padding: 32px 20px 48px;
  border-radius: 16px;
  background:
  radial-gradient(ellipse 80% 50% at 50% -20%, rgba(37, 99, 235, 0.15), transparent),
  linear-gradient(180deg, #f1f5f9 0%, #f8fafc 45%, #f1f5f9 100%);
}



.welcome-card {
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.1);
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}


.welcome-subtitle {
  margin: 0 0 8px 0;
  color: #6b7280;
  font-weight: 500;
}

.welcome-header h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
  color: #111827;
}



.task-today-block {
background: #ffffff;
}

.task-today-block h3 {
  margin: 0;
  font-size: 18px;
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}



.task-count {
  font-size: 12px;
  color: #2563eb;
  background: #eaf2ff;
  border-radius: 999px;
  padding: 4px 10px;
}

.task-list {
  border-radius: 10px;
  overflow: hidden;
}

.task-item {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.task-list-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
}


.task-title {
  font-weight: 500;
  color: #1f2937;
}

.task-due-date {
  font-size: 12px;
  color: #6b7280;
}
.actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}
</style>



