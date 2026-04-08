<template>
  <div class="body-container">
    <div ref="gridRef" class="grid">
      <TaskGroupCard title="Important & Urgent" color="red" :task-level="1" :initialItems="urgentImportant" @reload="loadTasks" />
      <TaskGroupCard title="Important but Not Urgent" color="yellow" :task-level="2" :initialItems="importantNotUrgent" @reload="loadTasks" />
      <TaskGroupCard title="Not Important but Urgent" color="blue" :task-level="3" :initialItems="urgentNotImportant" @reload="loadTasks" />
      <TaskGroupCard title="Not Important & Not Urgent" color="green" :task-level="4" :initialItems="notUrgentNotImportant" @reload="loadTasks" />
    </div>
    <a-dropdown placement="topRight" :trigger="['hover']">
      <a-button type="primary" shape="circle" size="large" class="export-btn">
        <template #icon><DownloadOutlined /></template>
      </a-button>
      <template #overlay>
        <a-menu @click="exportTasks">
          <a-menu-item key="image">Export as Image</a-menu-item>
          <a-menu-item key="excel">Export as Excel</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TaskGroupCard from '../components/TaskGroupCard.vue'
import { getTaskList } from '../api/tasks'
import { DownloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'



const LEVEL_LABEL = {
  1: 'Important & Urgent',
  2: 'Important but Not Urgent',
  3: 'Not Important but Urgent',
  4: 'Not Important & Not Urgent',
}

const taskList = ref([])
async function loadTasks() {
  try {
    taskList.value = await getTaskList()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadTasks()
})

function getUrgentImportantTasks() {
  return taskList.value.filter(t => t.task_level === 1)
}
function getImportantNotUrgentTasks() {
  return taskList.value.filter(t => t.task_level === 2)
}
function getUrgentNotImportantTasks() {
  return taskList.value.filter(t => t.task_level === 3)
}

function getNotUrgentNotImportantTasks() {
  return taskList.value.filter(t => t.task_level === 4)
}


const urgentImportant = computed(getUrgentImportantTasks)
const importantNotUrgent = computed(getImportantNotUrgentTasks)
const urgentNotImportant = computed(getUrgentNotImportantTasks)
const notUrgentNotImportant = computed(getNotUrgentNotImportantTasks)

const gridRef = ref(null)
async function exportToImage() {
  if (!gridRef.value) return message.error('Image exported failed')
  try {
    const canvas = await html2canvas(gridRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#f5f7fb',
      logging: false,
    })
    const downloadLink = document.createElement('a')
    downloadLink.download = 'tasks.png'
    downloadLink.href = canvas.toDataURL()
    downloadLink.click()
    message.success('Image exported')
  } catch (error) {
    console.error(error)
    message.error('Image exported failed')
  }
}


function exportToExcel() {
  const tasks = taskList.value.map(t => ({
    Title: t.title,
    Due: t.dueDate || '',
    Done: t.done ? 'Yes' : 'No',
    Level: LEVEL_LABEL[t.task_level] || 'Unknown',
  }))
  const sheet = XLSX.utils.json_to_sheet(tasks)
  const excel = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(excel, sheet, 'Tasks')
  XLSX.writeFile(excel, 'tasks.xlsx')
}

function exportTasks({ key }) {
  if (key === 'image') {
    exportToImage()
  } 
 if (key === 'excel') {
    exportToExcel()
  }
}

</script>

<style scoped>
.body-container {
  margin: 0 auto;
  padding: 20px 50px;
  position: relative;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.export-btn {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 200;
}


@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>