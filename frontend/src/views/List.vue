<template>
  <div class="body-container">
    <div class="grid">
      <TaskGroupCard title="Important & Urgent" color="red" :task-level="1" :initialItems="urgentImportant" />
      <TaskGroupCard title="Important but Not Urgent" color="yellow" :task-level="2" :initialItems="importantNotUrgent" />
      <TaskGroupCard title="Not Important but Urgent" color="blue" :task-level="3" :initialItems="urgentNotImportant" />
      <TaskGroupCard title="Not Important & Not Urgent" color="green" :task-level="4" :initialItems="notUrgentNotImportant" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TaskGroupCard from '../components/TaskGroupCard.vue'
import { getTaskList } from '../api/tasks'

const taskList = ref([])


onMounted(async() => {
  try{
    taskList.value = await getTaskList()
  } catch (e) {
    console.error(e)
  }
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


</script>

<style scoped>
.body-container {
  margin: 0 auto;
  padding: 20px 50px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>