<!-- the page's some settings were partially modified by AI -->
<template>
    <div class="home-page">
        <a-card class="home-card">
          <div class="home-header">
            <div class="left">
              <div class="home-subtitle">Welcome to Task Tracker! Have a quick look for today's tasks.</div>
              <h1>👋 Hi,{{ times }}</h1>
            </div>
            <div class="right">
              <div class="task-summary">
                <span class="label">TODAY TASKS</span>
                <span class="count">{{ todayTasks.length }}</span>
              </div>
            </div>
          </div>

      <div class="task-today-block">
        <!-- <div class="block-head">
          <h3>Today tasks</h3>
          <span class="task-count">{{ todayTasks.length }} task{{ todayTasks.length === 1 ? '' : 's' }}</span>
        </div> -->
        <div v-if="todayTasks.length > 0">
          <div class="task-list-header">
            <span>Task</span>
            <span>Task type</span>
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
                <span class="task-type">{{ taskTypeLabel(item.task_level) }}</span>
                <span class="task-due-date">{{ formatDate(item.dueDate) }}</span>
              </div>
            </a-list-item>
          </template>
        </a-list>
         </div>
          <div v-else class="task-empty">
          <a-empty description="Please go to task Board to create tasks." />
        </div>
      </div>

      <div class="actions">
        <a-button type="primary" size="large" @click="goToBoard">Go To Task Board</a-button>
        <a-button size="large" @click="goToPast">Task Statistics</a-button>
      </div>
        </a-card>
    </div>
</template>


<script setup>

import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getTaskList } from '../api/tasks'


const router = useRouter()

const times = computed(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
})



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
const todayTasks = ref([])
async function loadTodayTasks() {
  try {
    const tasks = await getTaskList()
    todayTasks.value = tasks.filter((task) => isToday(task.dueDate))
  } catch (err) {
    console.error('Failed to load today tasks', err)
    todayTasks.value = []
  }
}

const TASK_LEVEL_LABELS = {
  1: 'Important & Urgent',
  2: 'Important but Not Urgent',
  3: 'Not Important but Urgent',
  4: 'Not Important & Not Urgent',
}

function taskTypeLabel(level) {
  const n = Number(level)
  if (n >= 1 && n <= 4) return TASK_LEVEL_LABELS[n]
  return 'Uncategorised'
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
.home-page {
  padding: 32px 20px 48px;
  border-radius: 16px;
  background:
  radial-gradient(ellipse 80% 50% at 50% -20%, var(--home-bg-radial, rgba(37, 99, 235, 0.15)), transparent),
  linear-gradient(180deg, var(--home-bg-top, #f1f5f9) 0%, var(--home-bg-mid, #f8fafc) 45%, var(--home-bg-bottom, #f1f5f9) 100%);
}


.home-card {
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.1);
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}


.home-subtitle {
  margin: 0 0 8px 0;
  color: #6b7280;
  font-weight: 500;
}

.home-header {
  display: flex;
  justify-content: space-between; 
  align-items: flex-start;
}


.right h3 {
  margin: 0;
  font-size: 16px;
}

.task-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.task-summary .count {
  font-size: 40px;
  font-weight: 600;
  color: #111827;
  line-height: 1;
}

.task-summary .label {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
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
  gap: 8px; 
}


.task-list {
  border-radius: 10px;
  overflow: hidden;
}

.task-list-header,
.task-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr; 
  align-items: center;
}

.task-list-header span,
.task-item span {
  text-align: center;
}

.task-list-header {
  padding: 8px 12px;
  font-size: calc(var(--app-font-size, 16px) * 0.95);
  font-weight: 600;
}

.task-item {
  width: 100%;
  font-size: calc(var(--app-font-size, 16px) * 0.95);
}

.task-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; 
}


.actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  width: 100%;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
    gap: 12px;
  }
  .actions .ant-btn {
    width: 100%;
    min-width: 0;
  }
}
</style>



